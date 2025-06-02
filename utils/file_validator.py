"""
Модуль валидации файлов для приложения Třešinky Cetechovice.
Обеспечивает безопасную валидацию имен файлов с поддержкой чешских символов.
"""

import os
import re
import unicodedata
import mimetypes
from pathlib import Path
from typing import Tuple, Optional, Dict, Set
from werkzeug.utils import secure_filename as werkzeug_secure_filename

from .logger import validation_logger, log_function_call, log_exception


class FileValidator:
    """Валидатор файлов с поддержкой чешских символов."""
    
    # Допустимые расширения файлов
    ALLOWED_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4'}
    
    # Допустимые MIME типы
    ALLOWED_MIME_TYPES: Set[str] = {
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/webp',
        'image/heic',
        'video/mp4'
    }
    
    # Максимальный размер имени файла
    MAX_FILENAME_LENGTH: int = 255
    
    # Чешские диакритические символы и их ASCII эквиваленты
    CZECH_CHARS_MAP: Dict[str, str] = {
        'á': 'a', 'č': 'c', 'ď': 'd', 'é': 'e', 'ě': 'e', 'í': 'i',
        'ň': 'n', 'ó': 'o', 'ř': 'r', 'š': 's', 'ť': 't', 'ú': 'u',
        'ů': 'u', 'ý': 'y', 'ž': 'z',
        'Á': 'A', 'Č': 'C', 'Ď': 'D', 'É': 'E', 'Ě': 'E', 'Í': 'I',
        'Ň': 'N', 'Ó': 'O', 'Ř': 'R', 'Š': 'S', 'Ť': 'T', 'Ú': 'U',
        'Ů': 'U', 'Ý': 'Y', 'Ž': 'Z'
    }
    
    def __init__(self):
        """Инициализация валидатора."""
        log_function_call(validation_logger, 'FileValidator.__init__')
    
    def normalize_czech_filename(self, filename: str) -> str:
        """
        Нормализует имя файла, заменяя чешские символы на ASCII эквиваленты.
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Нормализованное имя файла
        """
        log_function_call(validation_logger, 'normalize_czech_filename', filename=filename)
        
        try:
            # Заменяем чешские символы
            normalized = filename
            for czech_char, ascii_char in self.CZECH_CHARS_MAP.items():
                normalized = normalized.replace(czech_char, ascii_char)
            
            # Дополнительная нормализация Unicode
            normalized = unicodedata.normalize('NFKD', normalized)
            normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
            
            validation_logger.info(f"Normalized filename: {filename} -> {normalized}")
            return normalized
            
        except Exception as e:
            log_exception(validation_logger, e, 'normalize_czech_filename')
            return filename  # Возвращаем исходное имя при ошибке
    
    def secure_filename(self, filename: str) -> str:
        """
        Создает безопасное имя файла с поддержкой чешских символов.
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Безопасное имя файла
        """
        log_function_call(validation_logger, 'secure_filename', filename=filename)
        
        try:
            if not filename:
                validation_logger.warning("Empty filename provided")
                return "unnamed_file"
            
            # Нормализуем чешские символы
            normalized = self.normalize_czech_filename(filename)
            
            # Используем встроенную функцию Werkzeug
            secured = werkzeug_secure_filename(normalized)
            
            # Если secure_filename возвращает пустую строку
            if not secured:
                validation_logger.warning(f"secure_filename returned empty string for: {filename}")
                # Создаем fallback имя из расширения
                ext = self.get_file_extension(filename)
                secured = f"unnamed_file{ext}"
            
            # Проверяем длину
            if len(secured) > self.MAX_FILENAME_LENGTH:
                name, ext = os.path.splitext(secured)
                max_name_length = self.MAX_FILENAME_LENGTH - len(ext)
                secured = name[:max_name_length] + ext
                validation_logger.warning(f"Filename truncated to: {secured}")
            
            validation_logger.info(f"Secured filename: {filename} -> {secured}")
            return secured
            
        except Exception as e:
            log_exception(validation_logger, e, 'secure_filename')
            # Создаем fallback имя при любой ошибке
            ext = self.get_file_extension(filename) or '.jpg'
            return f"error_file{ext}"
    
    def get_file_extension(self, filename: str) -> str:
        """
        Получает расширение файла в нижнем регистре.
        
        Args:
            filename: Имя файла
            
        Returns:
            Расширение файла
        """
        try:
            return os.path.splitext(filename)[1].lower()
        except Exception as e:
            log_exception(validation_logger, e, 'get_file_extension')
            return ''
    
    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Валидирует расширение файла.
        
        Args:
            filename: Имя файла
            
        Returns:
            Tuple (is_valid, error_message)
        """
        log_function_call(validation_logger, 'validate_file_extension', filename=filename)
        
        try:
            ext = self.get_file_extension(filename)
            
            if not ext:
                error_msg = f"No file extension found in: {filename}"
                validation_logger.warning(error_msg)
                return False, error_msg
            
            if ext not in self.ALLOWED_EXTENSIONS:
                error_msg = f"Extension {ext} not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                validation_logger.warning(error_msg)
                return False, error_msg
            
            validation_logger.info(f"File extension {ext} is valid")
            return True, ""
            
        except Exception as e:
            log_exception(validation_logger, e, 'validate_file_extension')
            return False, f"Error validating extension: {str(e)}"
    
    def validate_mime_type(self, filename: str, file_content: Optional[bytes] = None) -> Tuple[bool, str]:
        """
        Валидирует MIME тип файла.
        
        Args:
            filename: Имя файла
            file_content: Содержимое файла для проверки (опционально)
            
        Returns:
            Tuple (is_valid, error_message)
        """
        log_function_call(validation_logger, 'validate_mime_type', filename=filename)
        
        try:
            # Получаем MIME тип по расширению
            mime_type, _ = mimetypes.guess_type(filename)
            
            if not mime_type:
                # Пытаемся определить по расширению вручную
                ext = self.get_file_extension(filename)
                mime_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', 
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.heic': 'image/heic',
                    '.mp4': 'video/mp4'
                }
                mime_type = mime_map.get(ext)
            
            if not mime_type:
                error_msg = f"Could not determine MIME type for: {filename}"
                validation_logger.warning(error_msg)
                return False, error_msg
            
            if mime_type not in self.ALLOWED_MIME_TYPES:
                error_msg = f"MIME type {mime_type} not allowed"
                validation_logger.warning(error_msg)
                return False, error_msg
            
            validation_logger.info(f"MIME type {mime_type} is valid")
            return True, ""
            
        except Exception as e:
            log_exception(validation_logger, e, 'validate_mime_type')
            return False, f"Error validating MIME type: {str(e)}"
    
    def validate_filename_safety(self, filename: str) -> Tuple[bool, str]:
        """
        Проверяет безопасность имени файла.
        
        Args:
            filename: Имя файла
            
        Returns:
            Tuple (is_valid, error_message)
        """
        log_function_call(validation_logger, 'validate_filename_safety', filename=filename)
        
        try:
            if not filename:
                return False, "Empty filename"
            
            # Проверяем на потенциально опасные символы/паттерны
            dangerous_patterns = [
                r'\.\./',  # Directory traversal
                r'\.\.\\',  # Directory traversal (Windows)
                r'^/',     # Absolute path
                r'^[A-Z]:',  # Windows drive letter
                r'<|>|\||\*|\?|:',  # Запрещенные символы Windows
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, filename):
                    error_msg = f"Dangerous pattern found in filename: {filename}"
                    validation_logger.warning(error_msg)
                    return False, error_msg
            
            # Проверяем длину
            if len(filename) > self.MAX_FILENAME_LENGTH:
                error_msg = f"Filename too long: {len(filename)} > {self.MAX_FILENAME_LENGTH}"
                validation_logger.warning(error_msg)
                return False, error_msg
            
            validation_logger.info(f"Filename safety check passed for: {filename}")
            return True, ""
            
        except Exception as e:
            log_exception(validation_logger, e, 'validate_filename_safety')
            return False, f"Error validating filename safety: {str(e)}"
    
    def validate_file(self, filename: str, file_content: Optional[bytes] = None) -> Tuple[bool, str, str]:
        """
        Полная валидация файла.
        
        Args:
            filename: Имя файла
            file_content: Содержимое файла (опционально)
            
        Returns:
            Tuple (is_valid, secure_filename, error_message)
        """
        log_function_call(validation_logger, 'validate_file', filename=filename)
        
        try:
            # Проверяем безопасность имени файла
            is_safe, safety_error = self.validate_filename_safety(filename)
            if not is_safe:
                return False, "", safety_error
            
            # Проверяем расширение
            is_ext_valid, ext_error = self.validate_file_extension(filename)
            if not is_ext_valid:
                return False, "", ext_error
            
            # Проверяем MIME тип
            is_mime_valid, mime_error = self.validate_mime_type(filename, file_content)
            if not is_mime_valid:
                return False, "", mime_error
            
            # Создаем безопасное имя файла
            secure_name = self.secure_filename(filename)
            
            validation_logger.info(f"File validation passed: {filename} -> {secure_name}")
            return True, secure_name, ""
            
        except Exception as e:
            log_exception(validation_logger, e, 'validate_file')
            return False, "", f"Error during file validation: {str(e)}"


# Создаем глобальный экземпляр валидатора
file_validator = FileValidator() 