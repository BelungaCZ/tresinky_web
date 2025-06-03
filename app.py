from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, SubmitField, FileField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import exifread
from PIL import Image
from pathlib import Path
import re
import unicodedata
from sqlalchemy import desc, Column, text
from typing import Any
import subprocess
from wtforms.validators import ValidationError
from flask_sock import Sock
import json
import shutil
from config.config import get_config

# Импорты нашей системы логирования и валидации
from utils import (
    upload_logger, 
    processing_logger, 
    validation_logger, 
    app_logger,
    database_logger,
    log_function_call, 
    log_exception, 
    log_file_operation,
    file_validator
)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load configuration
app.config.from_object(get_config())

# Initialize extensions
db = SQLAlchemy(app)
sock = Sock(app)

# WebSocket connection storage
upload_sockets = set()

def check_system_dependencies():
    """Проверка необходимых системных зависимостей при запуске."""
    log_function_call(app_logger, 'check_system_dependencies')
    
    dependencies = {
        'convert': 'ImageMagick',
        'identify': 'ImageMagick', 
        'heif-convert': 'libheif-tools'
    }
    
    missing_deps = []
    
    for command, package in dependencies.items():
        try:
            result = subprocess.run(['which', command], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                app_logger.info(f"Dependency check passed: {command} found at {result.stdout.strip()}")
            else:
                missing_deps.append(f"{command} ({package})")
                app_logger.warning(f"Dependency check failed: {command} not found")
        except Exception as e:
            log_exception(app_logger, e, f'checking dependency {command}')
            missing_deps.append(f"{command} ({package})")
    
    if missing_deps:
        error_msg = f"Missing system dependencies: {', '.join(missing_deps)}"
        app_logger.error(error_msg)
        app_logger.error("Please install missing dependencies before running the application")
        return False, missing_deps
    
    app_logger.info("All system dependencies check passed")
    return True, []

@sock.route('/ws/upload')
def upload_progress(ws):
    upload_sockets.add(ws)
    try:
        while True:
            # Keep connection alive
            ws.receive()
    except:
        upload_sockets.remove(ws)

def send_progress_update(filename, status='processing'):
    """Send progress update to all connected WebSocket clients for single file"""
    message = json.dumps({
        'type': 'progress',
        'filename': filename,
        'status': status,  # 'processing', 'completed', 'failed'
        'timestamp': datetime.now().isoformat()
    })
    dead_sockets = []
    for ws in upload_sockets:
        try:
            ws.send(message)
        except:
            dead_sockets.append(ws)
    
    # Удаляем мертвые соединения
    for ws in dead_sockets:
        upload_sockets.discard(ws)

# Database Models
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name: str, email: str, message: str):
        self.name = name
        self.email = email
        self.message = message

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    original_date = db.Column(db.DateTime)
    # category = db.Column(db.String(100))  # Temporarily commented out for production compatibility
    display_order = db.Column(db.Integer, default=0)  # For controlling image order within categories

    def __init__(self, filename: str, title: str | None = None, description: str | None = None,
                 date: datetime | None = None, original_date: datetime | None = None,
                 display_order: int = 0):
        self.filename = filename
        self.title = title
        self.description = description
        self.date = date or datetime.now()
        self.original_date = original_date or self.date
        # self.category = category  # Temporarily commented out
        self.display_order = display_order

    def __repr__(self):
        return f'<GalleryImage {self.filename}>'

# Forms
class ContactForm(FlaskForm):
    name = StringField('Jméno', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Zpráva', validators=[DataRequired()])
    submit = SubmitField('Odeslat')

class DonationForm(FlaskForm):
    amount = StringField('Částka', validators=[DataRequired()])
    name = StringField('Jméno')
    email = EmailField('Email')
    message = TextAreaField('Zpráva')
    submit = SubmitField('Přispět')

def get_existing_albums():
    """Get list of existing albums from the gallery directory and remove empty ones"""
    gallery_dir = Path('static/images/gallery')
    if not gallery_dir.exists():
        return []
    
    albums = []
    for folder in gallery_dir.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            # Check if directory is empty
            has_files = False
            for file in folder.iterdir():
                if file.is_file() and file.suffix.lower() in ['.webp', '.mp4']:
                    has_files = True
                    break
            
            if has_files:
                albums.append(folder.name)
            else:
                # Remove empty directory
                try:
                    folder.rmdir()
                except OSError:
                    pass  # Directory might not be empty or already deleted
    
    return sorted(albums)

class ImageUploadForm(FlaskForm):
    image = FileField('Fotografie', validators=[DataRequired()])
    album = SelectField('Album', choices=[], coerce=str)
    new_album = StringField('Nový album')
    title = StringField('Název')
    description = TextAreaField('Popis')
    submit = SubmitField('Nahrát')

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.album.choices = [(album, album) for album in get_existing_albums()]
        self.album.choices.insert(0, ('', '-- Vyberte album nebo vytvořte nový --'))

    def validate_image(self, field):
        if field.data and hasattr(field.data, 'filename'):
            filename = field.data.filename.lower()
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4'}
            ext = os.path.splitext(filename)[1]
            if ext not in allowed_extensions:
                raise ValidationError('Nepodporovaný formát souboru. Povolené formáty: JPG, JPEG, PNG, WebP, HEIC, MP4')

class ImageEditForm(FlaskForm):
    title = StringField('Název', validators=[DataRequired()])
    description = TextAreaField('Popis')
    album = SelectField('Album', choices=[], coerce=str)
    display_order = IntegerField('Pořadí')
    submit = SubmitField('Uložit změny')

    def __init__(self, *args, **kwargs):
        super(ImageEditForm, self).__init__(*args, **kwargs)
        self.album.choices = [(album, album) for album in get_existing_albums()]
        # if 'obj' in kwargs and kwargs['obj']:
        #     self.album.data = kwargs['obj'].category  # Temporarily commented out

def get_image_date(image_path):
    """
    Извлекает дату создания изображения из EXIF или метаданных файла.
    
    Args:
        image_path: Путь к файлу изображения
        
    Returns:
        datetime: Дата создания изображения
    """
    log_function_call(processing_logger, 'get_image_date', image_path=image_path)
    
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            processing_logger.warning(f"Image file not found: {image_path}")
            return datetime.now()
        
        # Специальная обработка для HEIC файлов
        if image_path.lower().endswith(('.heic', '.heif')):
            processing_logger.info(f"HEIC file detected, skipping EXIF parsing: {image_path}")
            try:
                mtime = os.path.getmtime(image_path)
                date_obj = datetime.fromtimestamp(mtime)
                processing_logger.info(f"Using file modification time for HEIC {image_path}: {date_obj}")
                return date_obj
            except Exception as mtime_error:
                log_exception(processing_logger, mtime_error, f'getting modification time for HEIC {image_path}')
                return datetime.now()
        
        # Пытаемся получить дату из EXIF данных для обычных изображений
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
                if 'EXIF DateTimeOriginal' in tags:
                    date_str = str(tags['EXIF DateTimeOriginal'])
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    processing_logger.info(f"EXIF date found for {image_path}: {date_obj}")
                    return date_obj
                else:
                    processing_logger.info(f"No EXIF DateTimeOriginal found in {image_path}")
        except Exception as exif_error:
            log_exception(processing_logger, exif_error, f'reading EXIF from {image_path}')
        
        # Если EXIF не удалось прочитать, пытаемся получить дату модификации файла
        try:
            mtime = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(mtime)
            processing_logger.info(f"Using file modification time for {image_path}: {date_obj}")
            return date_obj
        except Exception as mtime_error:
            log_exception(processing_logger, mtime_error, f'getting modification time for {image_path}')
        
        # Если ничего не получилось, возвращаем текущее время
        processing_logger.warning(f"Could not determine date for {image_path}, using current time")
        return datetime.now()
        
    except Exception as e:
        log_exception(processing_logger, e, f'get_image_date for {image_path}')
        processing_logger.error(f"Critical error in get_image_date for {image_path}, using current time")
        return datetime.now()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/o-nas')
def about():
    return render_template('about.html')

@app.route('/sad')
def orchard():
    return render_template('orchard.html')

@app.route('/gallery')
def gallery():
    # Clean up empty directories
    gallery_path = os.path.join('static', 'images', 'gallery')
    if os.path.exists(gallery_path):
        for folder in os.listdir(gallery_path):
            folder_path = os.path.join(gallery_path, folder)
            if os.path.isdir(folder_path):
                # Check if directory is empty or contains only non-image files
                has_valid_files = False
                for file in os.listdir(folder_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4')):
                        has_valid_files = True
                        break
                
                if not has_valid_files:
                    try:
                        os.rmdir(folder_path)
                    except OSError:
                        pass  # Directory might not be empty or already deleted
    
    # Get existing albums with their images
    albums = []
    gallery_dir = Path('static/images/gallery')
    if gallery_dir.exists():
        for folder in gallery_dir.iterdir():
            if folder.is_dir() and not folder.name.startswith('.'):
                # Get all images in the folder
                images = []
                for file in folder.iterdir():
                    if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4']:
                        images.append(os.path.join('images', 'gallery', folder.name, file.name))
                
                if images:
                    # Get the first image as cover
                    cover_image = images[0]
                    albums.append({
                        'name': folder.name,
                        'cover_image': cover_image,
                        'images': images
                    })
    
    return render_template('gallery.html', folders=albums)

@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Děkujeme za vaši zprávu! Brzy vás budeme kontaktovat.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/podpora', methods=['GET', 'POST'])
def donate():
    form = DonationForm()
    if form.validate_on_submit():
        # Here you would typically integrate with a payment gateway
        flash('Děkujeme za vaši podporu!', 'success')
        return redirect(url_for('donate'))
    return render_template('donate.html', form=form)

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_image():
    """
    Обработка загрузки изображений с полным логированием и exception handling.
    """
    log_function_call(upload_logger, 'upload_image', method=request.method)
    
    if request.method == 'POST':
        try:
            form = ImageUploadForm()
            if form.validate_on_submit():
                upload_logger.info("Form validation passed")
                
                file = request.files.get('image')
                if not file or not file.filename:
                    return jsonify({'success': False, 'error': 'Не выбран файл для загрузки'})
                
                upload_logger.info(f"Received single file: {file.filename}")
                
                # Валидация одного файла
                if file.filename.startswith('.'):
                    return jsonify({'success': False, 'error': 'Скрытые файлы не поддерживаются'})

                try:
                    is_valid, secure_name, error_msg = file_validator.validate_file(file.filename)
                    if not is_valid:
                        return jsonify({'success': False, 'error': f'Недопустимый файл: {error_msg}'})
                    
                    log_file_operation(upload_logger, 'validation', file.filename, 'success', f'Valid file: {secure_name}')
                except Exception as validation_error:
                    log_exception(upload_logger, validation_error, f'validating file {file.filename}')
                    return jsonify({'success': False, 'error': f'Ошибка валидации: {str(validation_error)}'})

                upload_logger.info(f"File validation complete: {secure_name}")
                
                # Валидация и нормализация album name
                try:
                    album_name = form.new_album.data.strip() if form.new_album.data else form.album.data
                    
                    if not album_name:
                        error_msg = 'Vyberte album nebo zadejte název nového alba.'
                        upload_logger.error(error_msg)
                        return jsonify({'success': False, 'error': error_msg})
                    
                    # Нормализуем имя альбома с помощью нашего валидатора
                    album_name = file_validator.normalize_czech_filename(album_name)
                    # Дополнительная очистка для имен директорий
                    album_name = re.sub(r'[<>:"|?*]', '', album_name)  # Удаляем запрещенные символы
                    album_name = album_name.strip()
                    
                    if not album_name:
                        error_msg = 'Недопустимое имя альбома после нормализации.'
                        upload_logger.error(f"Album name normalization failed for: {form.new_album.data}")
                        return jsonify({'success': False, 'error': error_msg})
                    
                    upload_logger.info(f"Album name validated: {album_name}")
                    
                except Exception as album_error:
                    log_exception(upload_logger, album_error, 'validating album name')
                    return jsonify({'success': False, 'error': f'Ошибка валидации имени альбома: {str(album_error)}'})
                
                # Создание директории альбома
                try:
                    album_path = os.path.join('static', 'images', 'gallery', album_name)
                    os.makedirs(album_path, exist_ok=True)
                    upload_logger.info(f"Album directory created/verified: {album_path}")
                except Exception as dir_error:
                    log_exception(upload_logger, dir_error, f'creating album directory {album_path}')
                    return jsonify({'success': False, 'error': f'Не удалось создать директорию альбома: {str(dir_error)}'})
                
                # Обработка единственного файла
                try:
                    upload_logger.info(f"Processing single file: {file.filename}")
                    
                    # Уведомляем о начале обработки
                    send_progress_update(secure_name, 'processing')
                    
                    # Получаем расширение файла
                    _, ext = os.path.splitext(file.filename)
                    ext = ext.lower()
                    
                    # Сохраняем файл временно
                    temp_path = os.path.join(album_path, secure_name)
                    try:
                        file.save(temp_path)
                        log_file_operation(upload_logger, 'save', secure_name, 'success', f'Saved to {temp_path}')
                    except Exception as save_error:
                        log_exception(upload_logger, save_error, f'saving file {secure_name}')
                        send_progress_update(secure_name, 'failed')
                        return jsonify({'success': False, 'error': f'Ошибка сохранения: {str(save_error)}'})
                    
                    try:
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic']:
                            # Обработка изображения
                            try:
                                result = subprocess.run(
                                    ['./scripts/process_image.sh', temp_path, 'gallery'], 
                                    check=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=60  # 60 секунд таймаут
                                )
                                
                                processing_logger.info(f"Image processing completed for {secure_name}")
                                if result.stdout:
                                    processing_logger.info(f"Process output: {result.stdout}")
                                
                            except subprocess.CalledProcessError as proc_error:
                                error_msg = f"Image processing failed: {proc_error}"
                                if proc_error.stderr:
                                    error_msg += f" - {proc_error.stderr}"
                                log_exception(processing_logger, proc_error, f'processing image {secure_name}')
                                
                                # Удаляем временный файл при ошибке
                                try:
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)
                                except:
                                    pass
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': error_msg})
                                
                            except subprocess.TimeoutExpired as timeout_error:
                                error_msg = f"Image processing timeout: {timeout_error}"
                                log_exception(processing_logger, timeout_error, f'processing image {secure_name}')
                                
                                # Удаляем временный файл при таймауте
                                try:
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)
                                except:
                                    pass
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': error_msg})
                            
                            # Получаем имя обработанного файла
                            processed_filename = os.path.splitext(secure_name)[0] + '.webp'
                            
                            # Получаем дату изображения
                            try:
                                image_date = get_image_date(temp_path)
                            except Exception as date_error:
                                log_exception(processing_logger, date_error, f'getting image date for {secure_name}')
                                image_date = datetime.now()
                            
                            # Создаем запись в БД
                            try:
                                gallery_image = GalleryImage(
                                    filename=os.path.join('images', 'gallery', album_name, processed_filename),
                                    title=form.title.data or os.path.splitext(secure_name)[0],
                                    description=form.description.data,
                                    date=image_date,
                                    original_date=image_date,
                                    # category=album_name  # Temporarily commented out
                                )
                                
                                db.session.add(gallery_image)
                                database_logger.info(f"Added gallery image to session: {processed_filename}")
                                
                            except Exception as db_add_error:
                                log_exception(database_logger, db_add_error, f'creating GalleryImage for {secure_name}')
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': f"Database error: {str(db_add_error)}"})
                            
                        elif ext == '.mp4':
                            # Обработка видео файла
                            try:
                                final_path = os.path.join(album_path, secure_name)
                                if temp_path != final_path:
                                    os.rename(temp_path, final_path)
                                
                                log_file_operation(upload_logger, 'move', secure_name, 'success', f'Video moved to {final_path}')
                                
                                # Создаем запись в БД для видео
                                gallery_image = GalleryImage(
                                    filename=os.path.join('images', 'gallery', album_name, secure_name),
                                    title=form.title.data or os.path.splitext(secure_name)[0],
                                    description=form.description.data,
                                    date=datetime.now(),
                                    original_date=datetime.now(),
                                    # category=album_name  # Temporarily commented out
                                )
                                
                                db.session.add(gallery_image)
                                database_logger.info(f"Added video to session: {secure_name}")
                                
                            except Exception as video_error:
                                log_exception(upload_logger, video_error, f'processing video {secure_name}')
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': f"Video processing error: {str(video_error)}"})
                        
                        # Удаляем временный файл если он все еще существует
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except Exception as cleanup_error:
                            log_exception(upload_logger, cleanup_error, f'cleaning up temp file {temp_path}')
                        
                        log_file_operation(upload_logger, 'process', secure_name, 'success', f'Completed processing')
                        
                    except Exception as file_process_error:
                        log_exception(upload_logger, file_process_error, f'processing file {secure_name}')
                        
                        # Очистка при ошибке
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except:
                            pass
                        send_progress_update(secure_name, 'failed')
                        return jsonify({'success': False, 'error': f'Ошибка обработки: {str(file_process_error)}'})
                        
                except Exception as outer_file_error:
                    log_exception(upload_logger, outer_file_error, f'outer processing for {file.filename}')
                    send_progress_update(secure_name, 'failed')
                    return jsonify({'success': False, 'error': f'Unexpected error: {str(outer_file_error)}'})
                
                # Фиксируем изменения в БД для одного файла
                try:
                    db.session.commit()
                    database_logger.info(f"Successfully committed single file to database: {secure_name}")
                    upload_logger.info(f"Single file upload completed successfully: {secure_name}")
                    
                    send_progress_update(secure_name, 'completed')
                    
                    return jsonify({
                        'success': True, 
                        'filename': secure_name,
                        'message': f'Файл {secure_name} успешно загружен'
                    })
                    
                except Exception as commit_error:
                    log_exception(database_logger, commit_error, 'committing single file upload')
                    
                    # Откат транзакции
                    try:
                        db.session.rollback()
                        database_logger.info("Database rollback completed")
                    except Exception as rollback_error:
                        log_exception(database_logger, rollback_error, 'rolling back database session')
                    
                    send_progress_update(secure_name, 'failed')
                    return jsonify({'success': False, 'error': f'Ошибка сохранения: {str(commit_error)}'})
            
            else:
                # Ошибки валидации формы
                upload_logger.warning("Form validation failed")
                if form.errors:
                    error_message = 'Form validation failed: '
                    for field, errors in form.errors.items():
                        error_message += f'{field}: {", ".join(errors)}; '
                        upload_logger.warning(f"Form field error - {field}: {', '.join(errors)}")
                    return jsonify({'success': False, 'error': error_message.strip()})
                
                return jsonify({'success': False, 'error': 'Form validation failed'})
                
        except Exception as upload_error:
            log_exception(upload_logger, upload_error, 'upload_image POST request')
            return jsonify({'success': False, 'error': f'Критическая ошибка загрузки: {str(upload_error)}'})
    
    # GET request - показываем форму
    try:
        form = ImageUploadForm()
        upload_logger.info("Upload form rendered for GET request")
        return render_template('upload.html', form=form)
    except Exception as form_error:
        log_exception(upload_logger, form_error, 'rendering upload form')
        return render_template('upload.html', form=None)

def sync_gallery_with_disk():
    """Synchronize database with files on disk"""
    # Get all gallery images from database
    db_images = GalleryImage.query.all()
    
    # Create a set of existing files on disk
    existing_files = set()
    gallery_dir = Path('static/images/gallery')
    
    if gallery_dir.exists():
        for album_dir in gallery_dir.iterdir():
            if album_dir.is_dir() and not album_dir.name.startswith('.'):
                for file in album_dir.iterdir():
                    if file.is_file() and file.suffix.lower() in ['.webp', '.mp4']:
                        # Convert to relative path from static
                        rel_path = os.path.join('images', 'gallery', album_dir.name, file.name)
                        existing_files.add(rel_path)
    
    # Remove database entries for missing files
    for db_image in db_images:
        if db_image.filename not in existing_files:
            db.session.delete(db_image)
    
    db.session.commit()

@app.route('/admin/gallery')
def manage_gallery():
    # Sync database with files on disk
    sync_gallery_with_disk()
    
    # Get updated list of images
    images = GalleryImage.query.order_by(desc(GalleryImage.date)).all()  # type: ignore
    return render_template('manage_gallery.html', images=images)

@app.route('/admin/gallery/<int:id>/edit', methods=['GET', 'POST'])
def edit_image(id):
    image = GalleryImage.query.get_or_404(id)
    form = ImageEditForm(obj=image)
    
    if form.validate_on_submit():
        # Get current album from filename
        current_album = os.path.dirname(image.filename).split('/')[-1] if '/' in image.filename else ''
        new_album = form.album.data
        
        # Update image properties
        image.title = form.title.data
        image.description = form.description.data
        image.display_order = form.display_order.data
        
        # If album changed, move the file
        if current_album != new_album and new_album:
            old_path = os.path.join('static', image.filename)
            new_dir = os.path.join('static', 'images', 'gallery', new_album)
            new_filename = os.path.join('images', 'gallery', new_album, os.path.basename(image.filename))
            
            # Create new album directory if it doesn't exist
            os.makedirs(new_dir, exist_ok=True)
            
            # Move the file
            if os.path.exists(old_path):
                new_path = os.path.join('static', new_filename)
                os.rename(old_path, new_path)
                image.filename = new_filename
                
                # Check if old album is now empty
                remaining_images = db.session.query(GalleryImage).filter(
                    text("filename LIKE :pattern")
                ).params(pattern=f'%{current_album}%').count()
                
                # Remove old album directory if empty
                old_album_dir = os.path.join('static', 'images', 'gallery', current_album)
                if remaining_images == 1 and os.path.exists(old_album_dir):  # 1 because current image still matches
                    try:
                        os.rmdir(old_album_dir)
                    except OSError:
                        pass
        
        db.session.commit()
        flash('Fotografie byla úspěšně upravena!', 'success')
        return redirect(url_for('manage_gallery'))
    
    return render_template('edit_image.html', form=form, image=image)

@app.route('/admin/gallery/<int:id>/delete', methods=['POST'])
def delete_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    # Get the album directory path
    album_dir = os.path.dirname(os.path.join('static', image.filename))
    album_name = os.path.basename(album_dir)
    
    # Delete the file
    try:
        file_path = os.path.join('static', image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
    
    # Check if this was the last image in the album
    remaining_images = db.session.query(GalleryImage).filter(
        text("filename LIKE :pattern")
    ).params(pattern=f'%{album_name}%').count()
    
    # If no images left in the album, remove the directory
    if remaining_images == 0 and os.path.exists(album_dir):
        try:
            os.rmdir(album_dir)
        except OSError:
            pass  # Directory might not be empty or already deleted
    
    flash('Fotografie byla úspěšně smazána!', 'success')
    return redirect(url_for('manage_gallery'))

if __name__ == '__main__':
    # Проверяем системные зависимости при запуске
    deps_ok, missing = check_system_dependencies()
    if not deps_ok:
        app_logger.error("Cannot start application due to missing dependencies")
        app_logger.error(f"Please install: {', '.join(missing)}")
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print("Please install the missing dependencies before running the application")
        exit(1)
    
    # Создаем таблицы БД
    with app.app_context():
        try:
            db.create_all()
            app_logger.info("Database tables created/verified successfully")
        except Exception as db_error:
            log_exception(app_logger, db_error, 'creating database tables')
            print(f"ERROR: Failed to create database tables: {str(db_error)}")
            exit(1)
    
    app_logger.info("Starting Třešinky Cetechovice application")
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    print(f"Debug mode: {debug_mode}")

    if os.getenv('FLASK_ENV') == 'development':
        # Only use Flask development server in development
        # flask run --host=0.0.0.0 --port=5000
        print("Development mode: Use 'flask run --host=0.0.0.0 --port=5000' to start the server")
        app.run(host="0.0.0.0", port=5000, debug=debug_mode)
    else:
        # In production, this should be run with gunicorn using config file
        # gunicorn app:app -c gunicorn.conf.py
        print("Production mode: Use 'gunicorn app:app -c gunicorn.conf.py' to start the server")
        app.run(host="0.0.0.0", port=5000, debug=debug_mode)
