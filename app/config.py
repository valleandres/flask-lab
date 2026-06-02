import os


class Config:
    APP_ENV = "base"
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://user:password@db:3306/mydatabase",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://redis:6379/0")
    JWT_EXPIRATION_SECONDS = 3600  # 1 hour
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
    LOCAL_UPLOAD_FOLDER = os.getenv("LOCAL_UPLOAD_FOLDER", "uploads")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    S3_UPLOAD_PREFIX = os.getenv("S3_UPLOAD_PREFIX", "files")
    S3_PRESIGNED_URL_EXPIRATION = int(os.getenv("S3_PRESIGNED_URL_EXPIRATION", "3600"))


class DevelopmentConfig(Config):
    APP_ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-at-least-32-bytes-long")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)


class TestingConfig(Config):
    APP_ENV = "testing"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = DevelopmentConfig.SECRET_KEY
    JWT_SECRET_KEY = DevelopmentConfig.JWT_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"
    STORAGE_BACKEND = "local"


class ProductionConfig(Config):
    APP_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


CONFIG_BY_ENV = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name=None):
    selected_config = (
        (config_name or os.getenv("APP_ENV", "development")).strip().lower()
    )
    try:
        return CONFIG_BY_ENV[selected_config]
    except KeyError as error:
        raise ValueError(f"Unknown APP_ENV: {selected_config}") from error


def validate_config(config):
    if config["APP_ENV"] != "production":
        return

    required_settings = ("SECRET_KEY", "JWT_SECRET_KEY", "SQLALCHEMY_DATABASE_URI")
    missing_settings = [name for name in required_settings if not config.get(name)]
    if missing_settings:
        missing_names = ", ".join(missing_settings)
        raise ValueError(f"Missing production configuration: {missing_names}")
