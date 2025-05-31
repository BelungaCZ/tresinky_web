import os
from pathlib import Path

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tresinky.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 400 * 1024 * 1024  # 400MB max file size
    
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

class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    DOMAIN = 'sad-tresinky-cetechovice.cz'
    USE_HTTPS = True
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

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