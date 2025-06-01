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
from config.config import get_config

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Load configuration
app.config.from_object(get_config())

# Initialize extensions
db = SQLAlchemy(app)
sock = Sock(app)

# WebSocket connection storage
upload_sockets = set()

@sock.route('/ws/upload')
def upload_progress(ws):
    upload_sockets.add(ws)
    try:
        while True:
            # Keep connection alive
            ws.receive()
    except:
        upload_sockets.remove(ws)

def send_progress_update(current_file, progress):
    """Send progress update to all connected WebSocket clients"""
    message = json.dumps({
        'type': 'progress',
        'current_file': current_file,
        'progress': progress
    })
    for ws in upload_sockets:
        try:
            ws.send(message)
        except:
            upload_sockets.remove(ws)

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
    category = db.Column(db.String(100))  # New field for categories like "květen 2019"
    display_order = db.Column(db.Integer, default=0)  # For controlling image order within categories

    def __init__(self, filename: str, title: str | None = None, description: str | None = None,
                 date: datetime | None = None, original_date: datetime | None = None,
                 category: str | None = None, display_order: int = 0):
        self.filename = filename
        self.title = title
        self.description = description
        self.date = date or datetime.now()
        self.original_date = original_date or self.date
        self.category = category
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
        if field.data:
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
        if 'obj' in kwargs and kwargs['obj']:
            self.album.data = kwargs['obj'].category

def get_image_date(image_path):
    try:
        # Try to get date from EXIF data
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            if 'EXIF DateTimeOriginal' in tags:
                date_str = str(tags['EXIF DateTimeOriginal'])
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except:
        pass

    try:
        # If no EXIF data, get file creation/modification time
        return datetime.fromtimestamp(os.path.getmtime(image_path))
    except:
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
    if request.method == 'POST':
        form = ImageUploadForm()
        if form.validate_on_submit():
            files = request.files.getlist('image')
            
            # Filter out hidden files and ensure only supported file types
            valid_files = [
                file for file in files 
                if file.filename and not file.filename.startswith('.') 
                and file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4'))
            ]
            
            total_files = len(valid_files)
            processed_files = 0
            
            # Determine album name
            album_name = form.new_album.data if form.new_album.data else form.album.data
            if not album_name:
                return jsonify({'success': False, 'error': 'Vyberte album nebo zadejte název nového alba.'})
            
            # Create album directory if it doesn't exist
            album_path = os.path.join('static', 'images', 'gallery', album_name)
            os.makedirs(album_path, exist_ok=True)
            
            for file in valid_files:
                if file.filename:
                    # Get the file extension and convert to lowercase
                    _, ext = os.path.splitext(file.filename)
                    ext = ext.lower()
                    
                    # Generate a secure filename
                    filename = secure_filename(file.filename)
                    
                    # Update progress
                    send_progress_update(filename, int((processed_files / total_files) * 100))
                    
                    # Save the file temporarily in the album directory
                    temp_path = os.path.join(album_path, filename)
                    file.save(temp_path)
                    
                    try:
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic']:
                            # Process as image
                            subprocess.run(['./scripts/process_image.sh', temp_path, 'gallery'], check=True)
                            
                            # Get the processed filename (same name but .webp extension)
                            processed_filename = os.path.splitext(filename)[0] + '.webp'
                            
                            # Get image date from EXIF or file metadata
                            image_date = get_image_date(temp_path)
                            
                            # Create new gallery image with correct path
                            gallery_image = GalleryImage(
                                filename=os.path.join('images', 'gallery', album_name, processed_filename),
                                title=form.title.data or os.path.splitext(filename)[0],
                                description=form.description.data,
                                date=image_date,
                                original_date=image_date,
                                category=album_name
                            )
                            
                            db.session.add(gallery_image)
                            
                        elif ext == '.mp4':
                            # Handle video file
                            # For now, just move it to the album directory
                            final_path = os.path.join(album_path, filename)
                            os.rename(temp_path, final_path)
                            
                            # Create gallery entry for video with correct path
                            gallery_image = GalleryImage(
                                filename=os.path.join('images', 'gallery', album_name, filename),
                                title=form.title.data or os.path.splitext(filename)[0],
                                description=form.description.data,
                                date=datetime.now(),
                                original_date=datetime.now(),
                                category=album_name
                            )
                            
                            db.session.add(gallery_image)
                        
                        # Remove the temporary file if it still exists
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                    except subprocess.CalledProcessError as e:
                        return jsonify({'success': False, 'error': f'Error processing file {filename}: {str(e)}'})
                    
                    processed_files += 1
            
            db.session.commit()
            return jsonify({'success': True})
        
        # If form validation fails, return the specific error
        if form.errors:
            error_message = 'Form validation failed: '
            for field, errors in form.errors.items():
                error_message += f'{field}: {", ".join(errors)}; '
            return jsonify({'success': False, 'error': error_message.strip()})
        
        return jsonify({'success': False, 'error': 'Form validation failed'})
    
    form = ImageUploadForm()
    return render_template('upload.html', form=form)

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
        # Get old and new album paths
        old_album = image.category
        new_album = form.album.data
        
        # Update image details
        image.title = form.title.data
        image.description = form.description.data
        image.category = new_album
        image.display_order = form.display_order.data
        
        # If album changed, move the file
        if old_album != new_album:
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
                ).params(pattern=f'%{old_album}%').count()
                
                # Remove old album directory if empty
                old_album_dir = os.path.join('static', 'images', 'gallery', old_album)
                if remaining_images == 0 and os.path.exists(old_album_dir):
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
    with app.app_context():
        db.create_all()
    
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    print(f"Debug mode: {debug_mode}")

    if os.getenv('FLASK_ENV') == 'development':
        # Only use Flask development server in development
        # flask run --host=0.0.0.0 --port=5000
        print("Development mode: Use 'flask run --host=0.0.0.0 --port=5000' to start the server")
        app.run(host="0.0.0.0", port=5000, debug=debug_mode)
    else:
        # In production, this should be run with gunicorn
        # gunicorn app:app --bind 0.0.0.0:5000
        print("Production mode: Use 'gunicorn app:app --bind 0.0.0.0:5000' to start the server")
        app.run(host="0.0.0.0", port=5000, debug=debug_mode)
