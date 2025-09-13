from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from app.config import config_by_name
import os
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap5()

def create_app():
    """Application factory to create and configure the Flask app."""
    app = Flask(__name__)

    # Load configuration based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)



    with app.app_context():
        db.create_all()
    # Configure Flask-Login
    login_manager.login_view = 'main.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Custom Jinja2 filter for date formatting (used in templates like attendance.html, payments.html)
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d'):
        if value == 'now':
            return datetime.utcnow().strftime(format)
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return value

    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Import models to ensure they are registered with SQLAlchemy
    from app import models

    return app