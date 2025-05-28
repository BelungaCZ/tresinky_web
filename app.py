from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, SubmitField, FileField, IntegerField
from wtforms.validators import DataRequired, Email
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import exifread
from PIL import Image
from pathlib import Path
import re
import unicodedata

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tresinky.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['STATIC_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 400 * 1024 * 1024  # 400MB max file size
db = SQLAlchemy(app)

# Database Models
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    original_date = db.Column(db.DateTime)
    category = db.Column(db.String(100))  # New field for categories like "květen 2019"
    display_order = db.Column(db.Integer, default=0)  # For controlling image order within categories

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

class ImageUploadForm(FlaskForm):
    image = FileField('Fotografie', validators=[DataRequired()])
    title = StringField('Název')
    description = TextAreaField('Popis')
    category = StringField('Kategorie (např. "květen 2019")')
    submit = SubmitField('Nahrát')

class ImageEditForm(FlaskForm):
    title = StringField('Název', validators=[DataRequired()])
    description = TextAreaField('Popis')
    category = StringField('Kategorie')
    display_order = IntegerField('Pořadí')
    submit = SubmitField('Uložit změny')

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
    uploads_dir = Path('static/uploads')
    debug_info = {
        'exists': uploads_dir.exists(),
        'is_dir': uploads_dir.is_dir(),
        'children': [str(p) for p in uploads_dir.iterdir()] if uploads_dir.exists() else []
    }
    test_folder = uploads_dir / 'Třešinky'
    test_files = []
    if test_folder.exists() and test_folder.is_dir():
        test_files = [str(f) for f in test_folder.iterdir()]
    all_folders_files = {}
    for folder in uploads_dir.iterdir() if uploads_dir.exists() else []:
        if folder.is_dir() and not folder.name.startswith('.'):
            all_folders_files[folder.name] = [str(f) for f in folder.iterdir()]
    folders = []
    for folder in uploads_dir.iterdir() if uploads_dir.exists() else []:
        if folder.is_dir() and not folder.name.startswith('.'):
            images = []
            for file in folder.iterdir():
                if file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    images.append(str(file.relative_to('static')))
            if images:
                images.sort(key=lambda x: os.path.getsize(os.path.join('static', x)), reverse=True)
                folders.append({
                    'name': folder.name,
                    'cover_image': images[0],
                    'images': images
                })

    # --- Сортировка папок по правилам ---
    def normalize(s):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', s)
            if not unicodedata.combining(c)
        ).lower().strip()

    folders_special = []
    folders_rest = []

    for f in folders:
        norm_name = normalize(f['name'])
        if norm_name.startswith('stare a nove mapy'):
            folders_special.append((0, f))
        elif norm_name.startswith('puvodni stav'):
            folders_special.append((1, f))
        else:
            folders_rest.append(f)

    def parse_folder(folder_name):
        norm_name = normalize(folder_name)
        m = re.search(
            r'(leden|unor|brezen|duben|kveten|cerven|cervenec|srpen|zari|rijen|listopad|prosinec)\s+(\d{4})',
            norm_name
        )
        if m:
            month = [
                'leden', 'unor', 'brezen', 'duben', 'kveten', 'cerven',
                'cervenec', 'srpen', 'zari', 'rijen', 'listopad', 'prosinec'
            ].index(m.group(1))
            year = int(m.group(2))
            return (year, month, folder_name)
        return (9999, 99, folder_name)

    folders_rest.sort(key=lambda f: parse_folder(f['name']))
    folders_special.sort()
    folders = [f for _, f in folders_special] + folders_rest
    print('FOLDER ORDER:', [f['name'] for f in folders])
    # --- конец сортировки ---

    return render_template('gallery.html', folders=folders, debug_info=debug_info, test_files=test_files, all_folders_files=all_folders_files)

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
    form = ImageUploadForm()
    if form.validate_on_submit():
        files = request.files.getlist('image')
        
        for file in files:
            if file.filename:
                # Get the file extension and convert to lowercase
                _, ext = os.path.splitext(file.filename)
                ext = ext.lower()
                
                # Generate a secure filename
                filename = secure_filename(file.filename)
                
                # Save the file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Get image date from EXIF or file metadata
                image_date = get_image_date(file_path)
                
                # Create new gallery image
                gallery_image = GalleryImage(
                    filename=filename,
                    title=form.title.data,
                    description=form.description.data,
                    date=image_date,
                    original_date=image_date,
                    category=form.category.data
                )
                
                db.session.add(gallery_image)
        
        db.session.commit()
        flash('Fotografie byly úspěšně nahrány.', 'success')
        return redirect(url_for('manage_gallery'))
    
    return render_template('upload.html', form=form)

@app.route('/admin/gallery')
def manage_gallery():
    images = GalleryImage.query.order_by(GalleryImage.date.desc()).all()
    return render_template('manage_gallery.html', images=images)

@app.route('/admin/gallery/<int:id>/edit', methods=['GET', 'POST'])
def edit_image(id):
    image = GalleryImage.query.get_or_404(id)
    form = ImageEditForm(obj=image)
    
    if form.validate_on_submit():
        image.title = form.title.data
        image.description = form.description.data
        image.category = form.category.data
        image.display_order = form.display_order.data
        db.session.commit()
        flash('Fotografie byla úspěšně upravena!', 'success')
        return redirect(url_for('manage_gallery'))
    
    return render_template('edit_image.html', form=form, image=image)

@app.route('/admin/gallery/<int:id>/delete', methods=['POST'])
def delete_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    # Delete the file
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
    except OSError:
        pass
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
    
    flash('Fotografie byla úspěšně smazána!', 'success')
    return redirect(url_for('manage_gallery'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 