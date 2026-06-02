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
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
    LOCAL_UPLOAD_FOLDER = os.getenv("LOCAL_UPLOAD_FOLDER", "uploads")
    AWS_PROFILE = os.getenv("AWS_PROFILE")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    S3_UPLOAD_PREFIX = os.getenv("S3_UPLOAD_PREFIX", "files")
    S3_PRESIGNED_URL_EXPIRATION = int(os.getenv("S3_PRESIGNED_URL_EXPIRATION", "3600"))
