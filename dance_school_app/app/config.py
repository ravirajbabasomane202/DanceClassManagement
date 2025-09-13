import os
from datetime import timedelta

class Config:
    """Base configuration for the Flask dance school management application."""
    
    # Flask core settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-please-change-this-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dance_school.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logging in development

    # Flask-Login settings
    SESSION_COOKIE_SECURE = True  # Use HTTPS in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session timeout after 30 minutes

    # Flask-WTF settings (CSRF enabled by default)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF token valid for 1 hour

    # Flask-Bootstrap settings
    BOOTSTRAP_SERVE_LOCAL = True  # Serve Bootstrap files locally for offline development

    # Optional: Flask-Mail settings (for future email reminders)
    # MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@danceschool.com')

    # Optional: File upload settings (for profile pictures, if implemented)
    # UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit uploads to 16MB

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries for debugging

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Enforce HTTPS
    SQLALCHEMY_ECHO = False

    # Ensure SECRET_KEY and DATABASE_URL are set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY')  # No fallback in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/dance_school'

# Map configurations to environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}