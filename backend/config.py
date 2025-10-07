import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_ALGORITHM = "HS256"

    # Database configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or "localhost"
    MYSQL_USER = os.environ.get("MYSQL_USER") or "parth"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD") or "password"
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE") or "bookstore"
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT") or 3306)

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "echo": False,  # Set to True for debugging SQL
    }

    # IMPORTANT: Disable autoflush to prevent premature commits
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False

    # CORS configuration
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600

    # Pagination
    POSTS_PER_PAGE = 12

    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static", "uploads"
    )
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    SQLALCHEMY_ENGINE_OPTIONS = {
        **Config.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": True,  # Enable SQL logging in development
    }


class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

Config = config.get(os.environ.get("FLASK_ENV", "development"), DevelopmentConfig)
