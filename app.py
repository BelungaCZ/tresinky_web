from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, TextAreaField, EmailField, SubmitField, FileField, PasswordField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import exifread
from PIL import Image
import requests

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tresinky.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['STATIC_FOLDER'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 400 * 1024 * 1024  # 400MB max file size

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = '760242332676-s2k9jofepkefvllaie5p40o7us283roh.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'

# Facebook OAuth Configuration
app.config['FACEBOOK_APP_ID'] = 'ваш_app_id'
app.config['FACEBOOK_APP_SECRET'] = 'ваш_app_secret'

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return f'<User {self.email or self.phone}>'

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
    submit = SubmitField('Nahrát')

class ImageEditForm(FlaskForm):
    title = StringField('Název', validators=[DataRequired()])
    description = TextAreaField('Popis')
    submit = SubmitField('Uložit změny')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefonní číslo', validators=[Optional()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    remember = BooleanField('Zapamatovat si mě')
    submit = SubmitField('Přihlásit se')

    def validate(self):
        if not super().validate():
            return False
        
        # At least one of email or phone must be provided
        if not self.email.data and not self.phone.data:
            self.email.errors.append('Musíte zadat buď email nebo telefonní číslo')
            return False
        
        return True

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefonní číslo', validators=[Optional()])
    password = PasswordField('Heslo', validators=[
        DataRequired(),
        Length(min=8, message='Heslo musí mít alespoň 8 znaků')
    ])
    confirm_password = PasswordField('Potvrzení hesla', validators=[
        DataRequired(),
        EqualTo('password', message='Hesla se neshodují')
    ])
    accept_terms = BooleanField('Souhlasím s podmínkami', validators=[DataRequired()])
    submit = SubmitField('Registrovat se')

    def validate(self):
        if not super().validate():
            return False
        
        # At least one of email or phone must be provided
        if not self.email.data and not self.phone.data:
            self.email.errors.append('Musíte zadat buď email nebo telefonní číslo')
            return False
        
        return True

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Obnovit heslo')

class ProfileForm(FlaskForm):
    name = StringField('Jméno', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Telefonní číslo', validators=[Optional()])
    avatar = FileField('Profilová fotografie')
    current_password = PasswordField('Aktuální heslo', validators=[Optional()])
    new_password = PasswordField('Nové heslo', validators=[
        Optional(),
        Length(min=8, message='Heslo musí mít alespoň 8 znaků')
    ])
    confirm_password = PasswordField('Potvrzení nového hesla', validators=[
        Optional(),
        EqualTo('new_password', message='Hesla se neshodují')
    ])
    submit = SubmitField('Uložit změny')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        
        # At least one of email or phone must be provided
        if not self.email.data and not self.phone.data:
            self.email.errors.append('Musíte zadat buď email nebo telefonní číslo')
            return False
        
        # If changing password, current password is required
        if self.new_password.data and not self.current_password.data:
            self.current_password.errors.append('Pro změnu hesla musíte zadat aktuální heslo')
            return False
        
        return True

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

@app.route('/galerie')
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.date.desc()).all()
    return render_template('gallery.html', images=images)

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
                
                # Generate a secure filename with timestamp to avoid duplicates
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_filename = secure_filename(os.path.splitext(file.filename)[0])
                filename = f"{base_filename}_{timestamp}{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                file.save(file_path)
                
                # If the file is HEIC, convert it to JPEG
                if ext == '.heic':
                    try:
                        with Image.open(file_path) as img:
                            jpeg_path = os.path.splitext(file_path)[0] + '.jpg'
                            img.convert('RGB').save(jpeg_path, 'JPEG')
                        # Update filename to use JPEG version
                        filename = os.path.splitext(filename)[0] + '.jpg'
                        # Remove the original HEIC file
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error converting HEIC to JPEG: {e}")
                        continue
                
                # Get image date
                image_date = get_image_date(file_path if ext != '.heic' else jpeg_path)
                
                # Create database entry
                image = GalleryImage(
                    filename=filename,
                    title=form.title.data,
                    description=form.description.data,
                    date=image_date,
                    original_date=image_date
                )
                db.session.add(image)
        
        db.session.commit()
        flash('Fotografie byly úspěšně nahrány!', 'success')
        return redirect(url_for('gallery'))
    
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Here you would typically validate the user's credentials
        flash('Přihlášení proběhlo úspěšně!', 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/login/identita')
def login_identita():
    # Redirect to MojeID login
    return redirect('https://mojeid.cz/oidc/authorize')

@app.route('/login/google')
def login_google():
    # Google OAuth configuration
    client_id = app.config['GOOGLE_CLIENT_ID']
    redirect_uri = 'http://127.0.0.1:5001/login/google/callback'  # Hardcoded to match Google Cloud Console
    scope = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
    
    # Construct Google OAuth URL
    auth_url = (
        'https://accounts.google.com/o/oauth2/auth'
        '?client_id={}'
        '&redirect_uri={}'
        '&scope={}'
        '&response_type=code'
        '&access_type=offline'
        '&prompt=consent'
    ).format(client_id, redirect_uri, scope)
    
    return redirect(auth_url)

@app.route('/login/google/callback')
def google_callback():
    if 'error' in request.args:
        flash('Přihlášení přes Google selhalo. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))
    
    if 'code' not in request.args:
        flash('Chybí autorizační kód. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))
    
    # Get the authorization code
    code = request.args.get('code')
    
    # Exchange the code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': 'http://127.0.0.1:5001/login/google/callback',
        'grant_type': 'authorization_code'
    }
    
    try:
        # Get the tokens
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        userinfo_response = requests.get(
            userinfo_url,
            headers={'Authorization': f"Bearer {tokens['access_token']}"}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # Check if user exists
        user = User.query.filter_by(email=userinfo['email']).first()
        if not user:
            # Create new user
            user = User(
                email=userinfo['email'],
                password='google_oauth'  # We'll set a random password since they'll use Google to login
            )
            db.session.add(user)
            db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)  # Added remember=True to keep the session
        flash('Přihlášení přes Google proběhlo úspěšně!', 'success')
        return redirect(url_for('profile'))  # Changed to redirect to profile instead of home
        
    except Exception as e:
        flash('Nastala chyba při přihlašování přes Google. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))

@app.route('/login/facebook')
def login_facebook():
    # Facebook OAuth configuration
    app_id = app.config['FACEBOOK_APP_ID']
    redirect_uri = 'https://statex.cz/login/facebook/callback'
    scope = 'email,public_profile'
    
    # Construct Facebook OAuth URL
    auth_url = (
        'https://www.facebook.com/v18.0/dialog/oauth'
        '?client_id={}'
        '&redirect_uri={}'
        '&scope={}'
        '&response_type=code'
    ).format(app_id, redirect_uri, scope)
    
    return redirect(auth_url)

@app.route('/login/facebook/callback')
def facebook_callback():
    if 'error' in request.args:
        flash('Přihlášení přes Facebook selhalo. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))
    
    if 'code' not in request.args:
        flash('Chybí autorizační kód. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))
    
    # Get the authorization code
    code = request.args.get('code')
    
    # Exchange the code for access token
    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    token_data = {
        'client_id': app.config['FACEBOOK_APP_ID'],
        'client_secret': app.config['FACEBOOK_APP_SECRET'],
        'redirect_uri': 'https://statex.cz/login/facebook/callback',
        'code': code
    }
    
    try:
        # Get the access token
        token_response = requests.get(token_url, params=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info
        userinfo_url = 'https://graph.facebook.com/me'
        userinfo_params = {
            'fields': 'id,email,name',
            'access_token': tokens['access_token']
        }
        userinfo_response = requests.get(userinfo_url, params=userinfo_params)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # Check if user exists
        user = User.query.filter_by(email=userinfo['email']).first()
        if not user:
            # Create new user
            user = User(
                email=userinfo['email'],
                password='facebook_oauth'  # We'll set a random password since they'll use Facebook to login
            )
            db.session.add(user)
            db.session.commit()
        
        # Log the user in
        login_user(user, remember=True)
        flash('Přihlášení přes Facebook proběhlo úspěšně!', 'success')
        return redirect(url_for('profile'))
        
    except Exception as e:
        flash('Nastala chyba při přihlašování přes Facebook. Prosím, zkuste to znovu.', 'error')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Here you would typically create a new user
        flash('Registrace proběhla úspěšně! Nyní se můžete přihlásit.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Здесь будет логика отправки email для сброса пароля
            flash('Pokud existuje účet s tímto emailem, byl vám odeslán email s instrukcemi pro obnovení hesla.', 'info')
        else:
            # Для безопасности показываем одинаковое сообщение даже если email не найден
            flash('Pokud existuje účet s tímto emailem, byl vám odeslán email s instrukcemi pro obnovení hesla.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        # Update name
        if form.name.data != current_user.name:
            current_user.name = form.name.data
        # Update email
        if form.email.data != current_user.email:
            current_user.email = form.email.data
        # Update phone
        if form.phone.data != current_user.phone:
            current_user.phone = form.phone.data
        # Update password
        if form.new_password.data:
            current_user.password = form.new_password.data
        # Handle avatar upload
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars', filename)
            os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
            file.save(avatar_path)
            current_user.avatar = os.path.relpath(avatar_path, app.static_folder)
        db.session.commit()
        flash('Profil byl úspěšně aktualizován!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(
            email='admin@example.com',
            password='admin123',  # В реальном приложении пароль должен быть хеширован
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        
    app.run(debug=True, port=5001) 