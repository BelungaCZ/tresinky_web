"""
Централизованная система логирования для приложения Třešinky Cetechovice.
Обеспечивает логирование upload операций, обработки изображений и ошибок.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class TresinkylLogger:
    """Централизованный логгер для приложения."""
    
    _instance: Optional['TresinkylLogger'] = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logging()
        return cls._instance
    
    def _setup_logging(self):
        """Настройка системы логирования."""
        # Создаем директорию для логов если не существует
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Базовая конфигурация
        self.log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Детальный формат для ошибок
        self.detailed_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_logger(self, name: str, level: int = logging.INFO) -> logging.Logger:
        """
        Получить логгер с указанным именем.
        
        Args:
            name: Имя логгера
            level: Уровень логирования
            
        Returns:
            Настроенный логгер
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Избегаем дублирования обработчиков
        if not logger.handlers:
            # Обработчик для консоли
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(self.log_format)
            logger.addHandler(console_handler)
            
            # Обработчик для файла с ротацией
            file_handler = logging.handlers.RotatingFileHandler(
                f'logs/{name}.log',
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(self.detailed_format)
            logger.addHandler(file_handler)
            
            # Отдельный обработчик для ошибок
            error_handler = logging.handlers.RotatingFileHandler(
                f'logs/errors.log',
                maxBytes=10*1024*1024,  # 10 MB
                backupCount=10,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.detailed_format)
            logger.addHandler(error_handler)
        
        self._loggers[name] = logger
        return logger


# Создаем экземпляр логгера
logger_instance = TresinkylLogger()

# Предопределенные логгеры для разных компонентов
upload_logger = logger_instance.get_logger('upload')
processing_logger = logger_instance.get_logger('processing')  
validation_logger = logger_instance.get_logger('validation')
app_logger = logger_instance.get_logger('app')
database_logger = logger_instance.get_logger('database')


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Логирует вызов функции с параметрами.
    
    Args:
        logger: Логгер для записи
        func_name: Имя функции
        **kwargs: Параметры функции
    """
    params = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"Calling {func_name}({params})")


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Логирует исключение с контекстом.
    
    Args:
        logger: Логгер для записи
        exception: Исключение
        context: Дополнительный контекст
    """
    error_msg = f"Exception in {context}: {type(exception).__name__}: {str(exception)}"
    logger.error(error_msg, exc_info=True)


def log_file_operation(logger: logging.Logger, operation: str, filename: str, status: str, details: str = ""):
    """
    Логирует операции с файлами.
    
    Args:
        logger: Логгер для записи
        operation: Тип операции (upload, process, delete, etc.)
        filename: Имя файла
        status: Статус операции (success, error, warning)
        details: Дополнительные детали
    """
    msg = f"File {operation}: {filename} - {status.upper()}"
    if details:
        msg += f" - {details}"
    
    if status.lower() == 'error':
        logger.error(msg)
    elif status.lower() == 'warning':
        logger.warning(msg)
    else:
        logger.info(msg) 