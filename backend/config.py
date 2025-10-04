import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-super-secret-key-change-this"

    # JWT Configuration
    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key-change-this"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # Token expires in 1 day
    JWT_ALGORITHM = "HS256"

    # Database configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or "localhost"
    MYSQL_USER = os.environ.get("MYSQL_USER") or "root"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or "your_mysql_password"
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE") or "bookstore"
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT") or 3306)

    # SQLAlchemy configuration - NOW USING MYSQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0,
        "echo": True,  # Set to True for SQL query debugging
    }

    # CORS configuration
    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Pagination
    POSTS_PER_PAGE = 12

    # File upload configuration (for future book cover uploads)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static", "uploads"
    )
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"

    # Use more secure settings in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)  # Shorter token life in production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 0,
        "echo": False,  # Disable SQL echoing in production
    }


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}

# Get config based on environment
Config = config.get(os.environ.get("FLASK_ENV", "development"), DevelopmentConfig)
