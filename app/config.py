import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_EXPIRATION_SECONDS = 3600  # 1 hour
