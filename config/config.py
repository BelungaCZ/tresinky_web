import os
from pathlib import Path

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tresinky.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 400 * 1024 * 1024  # 400MB max file size
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit
    
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'stashok@speakasap.com')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'stashok@speakasap.com')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join('static', 'images', 'gallery')
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.mp4'}
    
    # Domain settings
    DOMAIN = os.getenv('DOMAIN', 'localhost:5000')
    USE_HTTPS = os.getenv('USE_HTTPS', 'false').lower() == 'true'
    
    # SSL settings
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH', 'ssl/cert.pem')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH', 'ssl/key.pem')
    
    # Debug settings
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DOMAIN = 'localhost:5000'
    USE_HTTPS = False
    TEMPLATES_AUTO_RELOAD = True
    # CSRF enabled for development
    WTF_CSRF_ENABLED = True
    
    # Security settings - disabled for development (HTTP environment)
    SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP in development
    REMEMBER_COOKIE_SECURE = False  # Allow remember cookies over HTTP in development
    SESSION_COOKIE_HTTPONLY = True  # Still protect against XSS
    REMEMBER_COOKIE_HTTPONLY = True  # Still protect against XSS

class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    DOMAIN = 'sad-tresinky-cetechovice.cz'
    USE_HTTPS = True
    
    # Let ProxyFix handle HTTPS detection from X-Forwarded-Proto header
    # PREFERRED_URL_SCHEME = 'https'  # Removed to avoid conflicts with ProxyFix
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # CSRF enabled for production
    WTF_CSRF_ENABLED = True
    
    # Security settings - enabled for production HTTPS environment
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    REMEMBER_COOKIE_SECURE = True  # Only send remember cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # CSRF disabled for testing
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default']) 