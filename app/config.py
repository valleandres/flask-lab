import os
from pathlib import Path


def load_env_file(env_file=None):
    selected_env_file = env_file or os.getenv("ENV_FILE")
    if not selected_env_file:
        return None

    path = Path(selected_env_file)
    if not path.exists():
        return None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)

    return path


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


load_env_file()


class Config:
    APP_ENV = "base"
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://user:password@db:3306/mydatabase",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://redis:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "60"))
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "flask-lab:")
    CACHE_REDIS_SOCKET_CONNECT_TIMEOUT = float(
        os.getenv("CACHE_REDIS_SOCKET_CONNECT_TIMEOUT", "1")
    )
    CACHE_REDIS_SOCKET_TIMEOUT = float(os.getenv("CACHE_REDIS_SOCKET_TIMEOUT", "1"))
    CACHE_OPTIONS = {
        "socket_connect_timeout": CACHE_REDIS_SOCKET_CONNECT_TIMEOUT,
        "socket_timeout": CACHE_REDIS_SOCKET_TIMEOUT,
    }
    READINESS_CHECK_CACHE = env_bool("READINESS_CHECK_CACHE", False)
    JWT_EXPIRATION_SECONDS = 3600  # 1 hour
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
    LOCAL_UPLOAD_FOLDER = os.getenv("LOCAL_UPLOAD_FOLDER", "uploads")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    S3_UPLOAD_PREFIX = os.getenv("S3_UPLOAD_PREFIX", "files")
    S3_PRESIGNED_URL_EXPIRATION = int(os.getenv("S3_PRESIGNED_URL_EXPIRATION", "3600"))
    OTEL_ENABLED = env_bool("OTEL_ENABLED", True)
    OTEL_EXCLUDED_URLS = os.getenv("OTEL_EXCLUDED_URLS", "health,ready")


class DevelopmentConfig(Config):
    APP_ENV = "development"
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-at-least-32-bytes-long")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    STORAGE_BACKEND = "local"
    AWS_PROFILE = None
    S3_BUCKET_NAME = None
    READINESS_CHECK_CACHE = env_bool("READINESS_CHECK_CACHE", False)


class TestingConfig(Config):
    APP_ENV = "testing"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = DevelopmentConfig.SECRET_KEY
    JWT_SECRET_KEY = DevelopmentConfig.JWT_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"
    READINESS_CHECK_CACHE = False
    STORAGE_BACKEND = "local"
    OTEL_ENABLED = False


class ProductionConfig(Config):
    APP_ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")
    READINESS_CHECK_CACHE = env_bool("READINESS_CHECK_CACHE", True)
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "s3")


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
    cache_type = str(config.get("CACHE_TYPE", "")).strip().lower()
    storage_backend = str(config.get("STORAGE_BACKEND", "")).strip().lower()

    if cache_type == "rediscache":
        required_settings += ("CACHE_REDIS_URL",)
    if storage_backend == "s3":
        required_settings += ("AWS_REGION", "S3_BUCKET_NAME")

    missing_settings = [name for name in required_settings if not config.get(name)]
    if missing_settings:
        missing_names = ", ".join(missing_settings)
        raise ValueError(f"Missing production configuration: {missing_names}")
