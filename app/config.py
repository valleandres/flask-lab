import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-at-least-32-bytes-long")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://user:password@db:3306/mydatabase",
    )
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://redis:6379/0")
    JWT_EXPIRATION_SECONDS = 3600  # 1 hour
