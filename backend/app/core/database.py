"""Database initialization and configuration."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import all models here to ensure they are registered with SQLAlchemy
        from app.models import user, prediction, consultation
        
        # Create tables
        db.create_all()
        
        print("✅ Database initialized successfully")
