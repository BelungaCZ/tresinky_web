from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
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
import random
from config.config import get_config

# Imports of our logging and validation system
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

# Configure Flask for HTTPS behind proxy
if app.config.get('USE_HTTPS'):
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
mail = Mail(app)
sock = Sock(app)

# Context processor to make config available in templates
@app.context_processor
def inject_config():
    return dict(config=app.config)

# WebSocket connection storage
upload_sockets = set()

def check_system_dependencies():
    """Check required system dependencies on startup."""
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
        warning_msg = f"Missing system dependencies: {', '.join(missing_deps)}"
        app_logger.warning(warning_msg)
        app_logger.warning("Application will start, but image upload functionality may not work properly")
        print(f"WARNING: Missing dependencies: {', '.join(missing_deps)}")
        print("Application will start, but image upload functionality may not work properly")
        return True, missing_deps
    
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
    
    # Remove dead connections
    for ws in dead_sockets:
        upload_sockets.discard(ws)

def send_contact_email(contact_message):
    """Send email notification about new contact message"""
    log_function_call(app_logger, 'send_contact_email', 
                     name=contact_message.name, 
                     email=contact_message.email)
    
    try:
        # Create email message
        msg = Message(
            subject='Nová zpráva z kontaktního formuláře - Třešinky Cetechovice',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[app.config['ADMIN_EMAIL']]
        )
        
        # HTML content of email
        msg.html = f"""
        <html>
        <body>
            <h2>Nová zpráva z kontaktního formuláře</h2>
            <p><strong>Odesláno:</strong> {contact_message.date.strftime('%d.%m.%Y %H:%M')}</p>
            <p><strong>Jméno:</strong> {contact_message.name}</p>
            <p><strong>Email:</strong> {contact_message.email}</p>
            <p><strong>Zpráva:</strong></p>
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0d6efd;">
                {contact_message.message.replace('\n', '<br>')}
            </div>
            <hr>
            <p><small>Tato zpráva byla automaticky odeslána z webu Třešinky Cetechovice</small></p>
        </body>
        </html>
        """
        
        # Text content of email
        msg.body = f"""
        Nová zpráva z kontaktního formuláře - Třešinky Cetechovice
        
        Odesláno: {contact_message.date.strftime('%d.%m.%Y %H:%M')}
        Jméno: {contact_message.name}
        Email: {contact_message.email}
        
        Zpráva:
        {contact_message.message}
        
        ---
        Tato zpráva byla automaticky odeslána z webu Třešinky Cetechovice
        """
        
        # Send email
        mail.send(msg)
        app_logger.info(f"Contact email sent successfully to {app.config['ADMIN_EMAIL']}")
        return True
        
    except Exception as e:
        log_exception(app_logger, e, 'sending contact email')
        return False

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

class Album(db.Model):
    """Album model for storing normalized and display names."""
    id = db.Column(db.Integer, primary_key=True)
    normalized_name = db.Column(db.String(100), unique=True, nullable=False)  # For file system
    display_name = db.Column(db.String(100), nullable=False)  # For user display
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with images
    images = db.relationship('GalleryImage', backref='album', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, normalized_name: str, display_name: str):
        self.normalized_name = normalized_name
        self.display_name = display_name
    
    def __repr__(self):
        return f'<Album {self.display_name} ({self.normalized_name})>'

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    original_date = db.Column(db.DateTime)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)
    display_order = db.Column(db.Integer, default=0)

    def __init__(self, filename: str, title: str | None = None, description: str | None = None,
                 date: datetime | None = None, original_date: datetime | None = None,
                 album_id: int | None = None, display_order: int = 0):
        self.filename = filename
        self.title = title
        self.description = description
        self.date = date or datetime.now()
        self.original_date = original_date or self.date
        self.album_id = album_id
        self.display_order = display_order

    def __repr__(self):
        return f'<GalleryImage {self.filename}>'

# Forms
class ContactForm(FlaskForm):
    name = StringField('Jméno', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Zpráva', validators=[DataRequired()])
    submit = SubmitField('Odeslat')

def create_album_if_not_exists(normalized_name: str, display_name: str) -> Album:
    """
    Creates album if it doesn't exist, otherwise returns existing one.
    
    Args:
        normalized_name: Normalized name for file system
        display_name: Name for user display
        
    Returns:
        Album: Created or found album
    """
    log_function_call(database_logger, 'create_album_if_not_exists', 
                     normalized_name=normalized_name, display_name=display_name)
    
    try:
        # Search by normalized name
        album = Album.query.filter_by(normalized_name=normalized_name).first()
        
        if album:
            # If album exists, do NOT overwrite display_name
            # This allows preserving beautiful names with diacritics
            database_logger.info(f"Album already exists: {normalized_name} -> {album.display_name}")
            return album
        else:
            # Create new album
            album = Album(normalized_name=normalized_name, display_name=display_name)
            db.session.add(album)
            db.session.commit()
            database_logger.info(f"Created new album: {display_name} ({normalized_name})")
            return album
            
    except Exception as e:
        log_exception(database_logger, e, f'creating album {normalized_name}')
        db.session.rollback()
        raise

def get_album_by_normalized_name(normalized_name: str) -> Album | None:
    """
    Finds album by normalized name.
    
    Args:
        normalized_name: Normalized album name
        
    Returns:
        Album | None: Found album or None
    """
    return Album.query.filter_by(normalized_name=normalized_name).first()

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
                # Search for album in database by normalized name
                album = get_album_by_normalized_name(folder.name)
                if album:
                    albums.append(album)
                else:
                    # If album not found in DB, create it with beautiful name
                    # Convert normalized_name to beautiful display_name
                    display_name = folder.name
                    # Add diacritics for known names
                    if folder.name == 'Tresinky':
                        display_name = 'Třešinky'
                    elif folder.name == 'Mapy':
                        display_name = 'Mapy a plány'
                    elif folder.name == '2023 unor':
                        display_name = '2023 - Únor'
                    elif folder.name == '2021 unor':
                        display_name = '2021 - Únor'
                    elif folder.name == '2021 duben prace v lese':
                        display_name = '2021 - Duben - Práce v lese'
                    elif folder.name == '2020 zari vymerovani':
                        display_name = '2020 - Září - Vyměřování'
                    elif folder.name == '2020 rijen vysadba':
                        display_name = '2020 - Říjen - Výsadba'
                    elif folder.name == '2020 kveten':
                        display_name = '2020 - Květen'
                    elif folder.name == '2020 cerven':
                        display_name = '2020 - Červen'
                    elif folder.name == '2019 kveten':
                        display_name = '2019 - Květen'
                    elif folder.name == '2019 unor':
                        display_name = '2019 - Únor'
                    elif folder.name == '2019 brezen duben':
                        display_name = '2019 - Březen, duben'
                    elif folder.name == '2018 zari, rijen, listopad':
                        display_name = '2018 - Září, říjen, listopad'
                    elif folder.name == '2017 Obrazky':
                        display_name = '2017 - Obrázky'
                    elif folder.name == '2015 puvodni stav pred zahajenim obnovy sadu':
                        display_name = '2015 - Původní stav před zahájením obnovy sadu'
                    elif folder.name == '2020':
                        display_name = '2020 - Celkový přehled'
                    elif folder.name == '2025':
                        display_name = '2025 - Nové fotky'
                    elif folder.name == '1950.LEITA':
                        display_name = '1950 - Letecký snímek'
                    
                    album = create_album_if_not_exists(folder.name, display_name)
                    albums.append(album)
            else:
                # Remove empty directory
                try:
                    folder.rmdir()
                except OSError:
                    pass  # Directory might not be empty or already deleted
    
    return sorted(albums, key=lambda x: x.display_name)

class ImageUploadForm(FlaskForm):
    image = FileField('Fotografie', validators=[DataRequired()])
    album = SelectField('Album', choices=[], coerce=str)
    new_album = StringField('Nový album')
    title = StringField('Název')
    description = TextAreaField('Popis')
    submit = SubmitField('Nahrát')

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        albums = get_existing_albums()
        self.album.choices = [(album.display_name, album.display_name) for album in albums]
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
        albums = get_existing_albums()
        self.album.choices = [(album.display_name, album.display_name) for album in albums]
        if 'obj' in kwargs and kwargs['obj'] and kwargs['obj'].album:
            self.album.data = kwargs['obj'].album.display_name

def get_image_date(image_path):
    """
    Extracts image creation date from EXIF or file metadata.
    
    Args:
        image_path: Path to image file
        
    Returns:
        datetime: Image creation date
    """
    log_function_call(processing_logger, 'get_image_date', image_path=image_path)
    
    try:
        # Check file existence
        if not os.path.exists(image_path):
            processing_logger.warning(f"Image file not found: {image_path}")
            return datetime.now()
        
        # Special handling for HEIC files
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
        
        # Try to get date from EXIF data for regular images
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
        
        # If EXIF couldn't be read, try to get file modification date
        try:
            mtime = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(mtime)
            processing_logger.info(f"Using file modification time for {image_path}: {date_obj}")
            return date_obj
        except Exception as mtime_error:
            log_exception(processing_logger, mtime_error, f'getting modification time for {image_path}')
        
        # If nothing worked, return current time
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

@app.route('/les')
def forest():
    return render_template('forest.html')

@app.route('/gallery')
def gallery():
    # Synchronize database with file system
    try:
        sync_gallery_with_disk()
    except Exception as e:
        # Log error but don't interrupt gallery display
        app_logger.warning(f"Failed to sync database with filesystem: {e}")
    
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
                # Get all images in the folder and sort by modification time (oldest first)
                images = []
                file_info = []
                for file in folder.iterdir():
                    if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4']:
                        file_path = os.path.join('images', 'gallery', folder.name, file.name)
                        # Get file modification time for sorting
                        try:
                            mtime = file.stat().st_mtime
                            # Add cache-busting parameter to prevent browser caching
                            file_path_with_cache_bust = f"{file_path}?v={int(mtime)}"
                            file_info.append((file_path_with_cache_bust, mtime))
                        except OSError:
                            # If we can't get mtime, use current time
                            file_info.append((file_path, 0))
                
                # Sort by modification time (oldest first)
                file_info.sort(key=lambda x: x[1])
                images = [file_path for file_path, _ in file_info]
                
                if images:
                    # Get a random image as cover
                    cover_image = random.choice(images)
                    
                    # Search for album in database
                    album = get_album_by_normalized_name(folder.name)
                    if album:
                        display_name = album.display_name
                    else:
                        # If album not found, create it with beautiful name
                        display_name = folder.name
                        # Add diacritics for known names
                        if folder.name == 'Tresinky':
                            display_name = 'Třešinky'
                        elif folder.name == 'Mapy':
                            display_name = 'Mapy a plány'
                        elif folder.name == '2023 unor':
                            display_name = '2023 - Únor'
                        elif folder.name == '2021 unor':
                            display_name = '2021 - Únor'
                        elif folder.name == '2021 duben prace v lese':
                            display_name = '2021 - Duben - Práce v lese'
                        elif folder.name == '2020 zari vymerovani':
                            display_name = '2020 - Září - Vyměřování'
                        elif folder.name == '2020 rijen vysadba':
                            display_name = '2020 - Říjen - Výsadba'
                        elif folder.name == '2020 kveten':
                            display_name = '2020 - Květen'
                        elif folder.name == '2020 cerven':
                            display_name = '2020 - Červen'
                        elif folder.name == '2019 kveten':
                            display_name = '2019 - Květen'
                        elif folder.name == '2019 unor':
                            display_name = '2019 - Únor'
                        elif folder.name == '2019 brezen duben':
                            display_name = '2019 - Březen, duben'
                        elif folder.name == '2018 zari, rijen, listopad':
                            display_name = '2018 - Září, říjen, listopad'
                        elif folder.name == '2017 Obrazky':
                            display_name = '2017 - Obrázky'
                        elif folder.name == '2015 puvodni stav pred zahajenim obnovy sadu':
                            display_name = '2015 - Původní stav před zahájením obnovy sadu'
                        elif folder.name == '2020':
                            display_name = '2020 - Celkový přehled'
                        elif folder.name == '2025':
                            display_name = '2025 - Nové fotky'
                        elif folder.name == '1950.LEITA':
                            display_name = '1950 - Letecký snímek'
                        elif folder.name == 'Pamětní kniha Cetechovice 1927':
                            display_name = 'Pamětní kniha Cetechovice 1927'
                        
                        album = create_album_if_not_exists(folder.name, display_name)
                        display_name = album.display_name
                    
                    albums.append({
                        'name': display_name,  # Use display_name for display
                        'normalized_name': folder.name,  # Keep normalized name
                        'cover_image': cover_image,
                        'images': images
                    })
    
    # Sort albums by date: Pamětní kniha first, then by year (oldest first)
    def sort_key(album):
        if album['name'] == 'Pamětní kniha Cetechovice 1927':
            return (0, 0)  # Always first
        
        # Extract year from album name for sorting
        import re
        year_match = re.search(r'(\d{4})', album['name'])
        if year_match:
            year = int(year_match.group(1))
            # For months, extract month number for proper calendar order
            month_order = {
                'leden': 1, 'únor': 2, 'březen': 3, 'duben': 4, 'květen': 5, 'červen': 6,
                'červenec': 7, 'srpen': 8, 'září': 9, 'říjen': 10, 'listopad': 11, 'prosinec': 12,
                'unor': 2, 'brezen': 3, 'duben': 4, 'kveten': 5, 'cerven': 6,
                'cervenec': 7, 'srpen': 8, 'zari': 9, 'rijen': 10, 'listopad': 11, 'prosinec': 12,
                'januar': 1, 'februar': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            
            # Check for month in name
            month = 0
            for month_name, month_num in month_order.items():
                if month_name in album['name'].lower():
                    month = month_num
                    break
            
            return (1, year, month)  # 1 for regular albums, then year, then month
        
        # For albums without clear year, put them at the end
        return (2, 9999, 0)
    
    albums = sorted(albums, key=sort_key)
    
    return render_template('gallery.html', folders=albums)

@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    log_function_call(app_logger, 'contact', method=request.method)
    
    # Debug information
    app_logger.info(f"Request URL: {request.url}")
    app_logger.info(f"Request scheme: {request.scheme}")
    app_logger.info(f"Request headers: {dict(request.headers)}")
    
    form = ContactForm()
    
    if request.method == 'POST':
        app_logger.info("Contact form POST request received")
        app_logger.info(f"Form data: name={form.name.data}, email={form.email.data}, message_length={len(form.message.data) if form.message.data else 0}")
        
        if form.validate_on_submit():
            app_logger.info("Contact form validation passed")
            try:
                message = ContactMessage(
                    name=form.name.data,
                    email=form.email.data,
                    message=form.message.data
                )
                db.session.add(message)
                db.session.commit()
                app_logger.info(f"Contact message saved successfully from {form.email.data}")
                
                # Send email notification
                email_sent = send_contact_email(message)
                if email_sent:
                    app_logger.info("Contact email notification sent successfully")
                else:
                    app_logger.warning("Failed to send contact email notification")
                
                flash('Děkujeme za vaši zprávu! Brzy vás budeme kontaktovat.', 'success')
                return redirect(url_for('contact'))
            except Exception as e:
                log_exception(app_logger, e, 'saving contact message')
                db.session.rollback()
                flash('Došlo k chybě při odesílání zprávy. Zkuste to prosím znovu.', 'error')
        else:
            app_logger.warning("Contact form validation failed")
            app_logger.warning(f"Form errors: {form.errors}")
            flash('Zkontrolujte prosím vyplněné údaje a zkuste znovu.', 'error')
    
    return render_template('contact.html', form=form)

@app.route('/podpora')
def donate():
    return render_template('donate.html')

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_image():
    """
    Image upload processing with full logging and exception handling.
    """
    log_function_call(upload_logger, 'upload_image', method=request.method)
    
    if request.method == 'POST':
        # Check dependencies only when attempting upload
        deps_ok, missing = check_system_dependencies()
        if not deps_ok:
            error_msg = f"Image processing dependencies are missing: {', '.join(missing)}"
            upload_logger.error(error_msg)
            return jsonify({'success': False, 'error': f'Image processing error: {error_msg}. Please install required dependencies.'})
        
        try:
            upload_logger.info("Received POST request to /admin/upload")
            upload_logger.info(f"Request headers: {dict(request.headers)}")
            upload_logger.info(f"Request form data: {dict(request.form)}")
            upload_logger.info(f"Request files: {dict(request.files)}")
            
            form = ImageUploadForm()
            if form.validate_on_submit():
                upload_logger.info("Form validation passed")
                
                file = request.files.get('image')
                if not file or not file.filename:
                    upload_logger.error("No file selected")
                    return jsonify({'success': False, 'error': 'No file selected for upload'})
                
                upload_logger.info(f"Received single file: {file.filename}")
                
                # Single file validation
                if file.filename.startswith('.'):
                    upload_logger.error(f"Hidden file rejected: {file.filename}")
                    return jsonify({'success': False, 'error': 'Hidden files are not supported'})

                try:
                    is_valid, secure_name, error_msg = file_validator.validate_file(file.filename)
                    if not is_valid:
                        upload_logger.error(f"File validation failed: {error_msg}")
                        return jsonify({'success': False, 'error': f'Invalid file: {error_msg}'})
                    
                    log_file_operation(upload_logger, 'validation', file.filename, 'success', f'Valid file: {secure_name}')
                except Exception as validation_error:
                    log_exception(upload_logger, validation_error, f'validating file {file.filename}')
                    return jsonify({'success': False, 'error': f'Validation error: {str(validation_error)}'})

                upload_logger.info(f"File validation complete: {secure_name}")
                
                # Album name validation and normalization
                try:
                    album_name = form.new_album.data.strip() if form.new_album.data else form.album.data
                    
                    if not album_name:
                        error_msg = 'Vyberte album nebo zadejte název nového alba.'
                        upload_logger.error(error_msg)
                        return jsonify({'success': False, 'error': error_msg})
                    
                    # Normalize album name using our validator
                    album_name = file_validator.normalize_czech_filename(album_name)
                    # Additional cleanup for directory names
                    album_name = re.sub(r'[<>:"|?*]', '', album_name)  # Remove forbidden characters
                    album_name = album_name.strip()
                    
                    if not album_name:
                        error_msg = 'Invalid album name after normalization.'
                        upload_logger.error(f"Album name normalization failed for: {form.new_album.data}")
                        return jsonify({'success': False, 'error': error_msg})
                    
                    upload_logger.info(f"Album name validated: {album_name}")
                    
                except Exception as album_error:
                    log_exception(upload_logger, album_error, 'validating album name')
                    return jsonify({'success': False, 'error': f'Album name validation error: {str(album_error)}'})
                
                # Create album directory
                try:
                    album_path = os.path.join('static', 'images', 'gallery', album_name)
                    os.makedirs(album_path, exist_ok=True)
                    upload_logger.info(f"Album directory created/verified: {album_path}")
                except Exception as dir_error:
                    log_exception(upload_logger, dir_error, f'creating album directory {album_path}')
                    return jsonify({'success': False, 'error': f'Failed to create album directory: {str(dir_error)}'})
                
                # Single file processing
                try:
                    upload_logger.info(f"Processing single file: {file.filename}")
                    
                    # Notify about processing start
                    send_progress_update(secure_name, 'processing')
                    
                    # Get file extension
                    _, ext = os.path.splitext(file.filename)
                    ext = ext.lower()
                    
                    # Save file temporarily
                    temp_path = os.path.join(album_path, secure_name)
                    try:
                        file.save(temp_path)
                        log_file_operation(upload_logger, 'save', secure_name, 'success', f'Saved to {temp_path}')
                    except Exception as save_error:
                        log_exception(upload_logger, save_error, f'saving file {secure_name}')
                        send_progress_update(secure_name, 'failed')
                        return jsonify({'success': False, 'error': f'Save error: {str(save_error)}'})
                    
                    try:
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic']:
                            # Image processing
                            try:
                                result = subprocess.run(
                                    ['./scripts/process_image.sh', temp_path, 'gallery'], 
                                    check=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=60  # 60 sekund timeout
                                )
                                
                                processing_logger.info(f"Image processing completed for {secure_name}")
                                if result.stdout:
                                    processing_logger.info(f"Process output: {result.stdout}")
                                
                            except subprocess.CalledProcessError as proc_error:
                                error_msg = f"Image processing failed: {proc_error}"
                                if proc_error.stderr:
                                    error_msg += f" - {proc_error.stderr}"
                                log_exception(processing_logger, proc_error, f'processing image {secure_name}')
                                
                                # Remove temporary file on error
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
                                
                                # Remove temporary file on timeout
                                try:
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)
                                except:
                                    pass
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': error_msg})
                            
                            # Get processed file name
                            processed_filename = os.path.splitext(secure_name)[0] + '.webp'
                            
                            # Get image date
                            try:
                                image_date = get_image_date(temp_path)
                            except Exception as date_error:
                                log_exception(processing_logger, date_error, f'getting image date for {secure_name}')
                                image_date = datetime.now()
                            
                            # Create database record
                            try:
                                # Create or get album
                                album = create_album_if_not_exists(album_name, form.new_album.data.strip() if form.new_album.data else form.album.data)
                                
                                gallery_image = GalleryImage(
                                    filename=os.path.join('images', 'gallery', album_name, processed_filename),
                                    title=form.title.data or os.path.splitext(secure_name)[0],
                                    description=form.description.data,
                                    date=image_date,
                                    original_date=image_date,
                                    album_id=album.id,
                                )
                                
                                db.session.add(gallery_image)
                                database_logger.info(f"Added gallery image to session: {processed_filename}")
                                
                            except Exception as db_add_error:
                                log_exception(database_logger, db_add_error, f'creating GalleryImage for {secure_name}')
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': f"Database error: {str(db_add_error)}"})
                            
                        elif ext == '.mp4':
                            # Video file processing
                            try:
                                final_path = os.path.join(album_path, secure_name)
                                if temp_path != final_path:
                                    os.rename(temp_path, final_path)
                                
                                log_file_operation(upload_logger, 'move', secure_name, 'success', f'Video moved to {final_path}')
                                
                                # Create database record for video
                                # Create or get album
                                album = create_album_if_not_exists(album_name, form.new_album.data.strip() if form.new_album.data else form.album.data)
                                
                                gallery_image = GalleryImage(
                                    filename=os.path.join('images', 'gallery', album_name, secure_name),
                                    title=form.title.data or os.path.splitext(secure_name)[0],
                                    description=form.description.data,
                                    date=datetime.now(),
                                    original_date=datetime.now(),
                                    album_id=album.id,
                                )
                                
                                db.session.add(gallery_image)
                                database_logger.info(f"Added video to session: {secure_name}")
                                
                            except Exception as video_error:
                                log_exception(upload_logger, video_error, f'processing video {secure_name}')
                                send_progress_update(secure_name, 'failed')
                                return jsonify({'success': False, 'error': f"Video processing error: {str(video_error)}"})
                        
                        # Remove temporary file if it still exists
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except Exception as cleanup_error:
                            log_exception(upload_logger, cleanup_error, f'cleaning up temp file {temp_path}')
                        
                        log_file_operation(upload_logger, 'process', secure_name, 'success', f'Completed processing')
                        
                    except Exception as file_process_error:
                        log_exception(upload_logger, file_process_error, f'processing file {secure_name}')
                        
                        # Cleanup on error
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except:
                            pass
                        send_progress_update(secure_name, 'failed')
                        return jsonify({'success': False, 'error': f'Processing error: {str(file_process_error)}'})
                        
                except Exception as outer_file_error:
                    log_exception(upload_logger, outer_file_error, f'outer processing for {file.filename}')
                    send_progress_update(secure_name, 'failed')
                    return jsonify({'success': False, 'error': f'Unexpected error: {str(outer_file_error)}'})
                
                # Commit database changes for single file
                try:
                    db.session.commit()
                    database_logger.info(f"Successfully committed single file to database: {secure_name}")
                    upload_logger.info(f"Single file upload completed successfully: {secure_name}")
                    
                    send_progress_update(secure_name, 'completed')
                    
                    return jsonify({
                        'success': True, 
                        'filename': secure_name,
                        'message': f'Soubor {secure_name} úspěšně nahrán'
                    })
                    
                except Exception as commit_error:
                    log_exception(database_logger, commit_error, 'committing single file upload')
                    
                    # Rollback transakce
                    try:
                        db.session.rollback()
                        database_logger.info("Database rollback completed")
                    except Exception as rollback_error:
                        log_exception(database_logger, rollback_error, 'rolling back database session')
                    
                    send_progress_update(secure_name, 'failed')
                    return jsonify({'success': False, 'error': f'Save error: {str(commit_error)}'})
            else:
                # Form validation failed
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f"{field}: {error}")
                upload_logger.error(f"Form validation failed: {errors}")
                return jsonify({'success': False, 'error': 'Validation error: ' + '; '.join(errors)})
        except Exception as e:
            log_exception(upload_logger, e, 'upload_image')
            return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'})
    else:
        # GET request - show upload form
        upload_logger.info("Received GET request to /admin/upload")
        form = ImageUploadForm()
        return render_template('upload.html', form=form)

def sync_gallery_with_disk():
    """Synchronize database with files on disk"""
    log_function_call(database_logger, 'sync_gallery_with_disk')
    
    try:
        # Get all gallery images from database
        db_images = GalleryImage.query.all()
        database_logger.info(f"Found {len(db_images)} images in database")
        
        # Create a set of existing files on disk
        existing_files = set()
        gallery_dir = Path('static/images/gallery')
        
        if gallery_dir.exists():
            for album_dir in gallery_dir.iterdir():
                if album_dir.is_dir() and not album_dir.name.startswith('.'):
                    album_files = 0
                    for file in album_dir.iterdir():
                        if file.is_file() and file.suffix.lower() in ['.webp', '.mp4']:
                            # Convert to relative path from static
                            rel_path = os.path.join('images', 'gallery', album_dir.name, file.name)
                            existing_files.add(rel_path)
                            album_files += 1
                    
                    if album_files == 0:
                        # Remove empty album directories
                        try:
                            album_dir.rmdir()
                            database_logger.info(f"Removed empty album directory: {album_dir.name}")
                        except OSError:
                            pass  # Directory might not be empty or already deleted
        else:
            database_logger.warning("Gallery directory does not exist: static/images/gallery")
        
        database_logger.info(f"Found {len(existing_files)} files on disk")
        
        # Remove database entries for missing files
        removed_count = 0
        for db_image in db_images:
            if db_image.filename not in existing_files:
                database_logger.info(f"Removing database entry for missing file: {db_image.filename}")
                db.session.delete(db_image)
                removed_count += 1
        
        if removed_count > 0:
            db.session.commit()
            database_logger.info(f"Removed {removed_count} database entries for missing files")
        else:
            database_logger.info("No database entries to remove - all files exist on disk")
        
        # Clean up empty albums in database
        albums = Album.query.all()
        for album in albums:
            if not album.images:
                database_logger.info(f"Removing empty album from database: {album.display_name}")
                db.session.delete(album)
        
        db.session.commit()
        
    except Exception as e:
        log_exception(database_logger, e, 'sync_gallery_with_disk')
        raise

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
        # Get old and new album paths
        old_album = image.album.display_name if image.album else None
        new_album = form.album.data
        
        # Update image details
        image.title = form.title.data
        image.description = form.description.data
        
        # Aktualizace alba
        if new_album:
            # Vytvoření nebo získání nového alba
            album = create_album_if_not_exists(
                file_validator.normalize_czech_filename(new_album),
                new_album
            )
            image.album_id = album.id
        else:
            image.album_id = None
            
        image.display_order = form.display_order.data
        
        # If album changed, move the file
        if old_album != new_album and old_album:
            old_path = os.path.join('static', image.filename)
            new_dir = os.path.join('static', 'images', 'gallery', album.normalized_name)
            new_filename = os.path.join('images', 'gallery', album.normalized_name, os.path.basename(image.filename))
            
            # Create new album directory if it doesn't exist
            os.makedirs(new_dir, exist_ok=True)
            
            # Move the file
            if os.path.exists(old_path):
                new_path = os.path.join('static', new_filename)
                os.rename(old_path, new_path)
                image.filename = new_filename
                
                # Check if old album is now empty
                old_album_obj = get_album_by_normalized_name(file_validator.normalize_czech_filename(old_album))
                if old_album_obj:
                    remaining_images = db.session.query(GalleryImage).filter_by(album_id=old_album_obj.id).count()
                    
                    # Remove old album directory if empty
                    old_album_dir = os.path.join('static', 'images', 'gallery', old_album_obj.normalized_name)
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
    if image.album:
        remaining_images = db.session.query(GalleryImage).filter_by(album_id=image.album.id).count()
        
        # If no images left in the album, remove the directory
        if remaining_images == 0 and os.path.exists(album_dir):
            try:
                os.rmdir(album_dir)
            except OSError:
                pass  # Directory might not be empty or already deleted
    
    flash('Fotografie byla úspěšně smazána!', 'success')
    return redirect(url_for('manage_gallery'))

if __name__ == '__main__':
    # Kontrola systémových závislostí při spuštění
    deps_ok, missing = check_system_dependencies()
    if not deps_ok:
        app_logger.warning("Some dependencies are missing, but application will continue")
        app_logger.warning(f"Missing: {', '.join(missing)}")
        print(f"WARNING: Missing dependencies: {', '.join(missing)}")
        print("Application will continue, but image upload functionality may not work properly")
    
    # Vytvoření tabulek DB
    with app.app_context():
        try:
            db.create_all()
            app_logger.info("Database tables created/verified successfully")
            
            # Automatická synchronizace DB s файловой системой při spuštění
            try:
                sync_gallery_with_disk()
                app_logger.info("Database synchronized with filesystem on startup")
            except Exception as sync_error:
                log_exception(app_logger, sync_error, 'synchronizing database with filesystem on startup')
                print(f"WARNING: Failed to sync database with filesystem: {str(sync_error)}")
                
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
