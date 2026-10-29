import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'autopdi-dev-secret-key-2026-fallback')
    
    # Database Configuration
    # Supports MySQL with PyMySQL and SQLite fallback
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///autopdi.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    } if 'mysql' in DATABASE_URL else {}

    # File Uploads
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    INSPECTIONS_UPLOAD_FOLDER = UPLOAD_FOLDER / 'inspections'
    PROFILES_UPLOAD_FOLDER = UPLOAD_FOLDER / 'profiles'
    DOCUMENTS_UPLOAD_FOLDER = UPLOAD_FOLDER / 'documents'
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'pdf'}

    # AI Configuration
    AI_API_KEY = os.getenv('AI_API_KEY', '')

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
