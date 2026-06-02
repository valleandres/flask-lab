import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_migrate import Migrate

from app.auth.routes import auth_bp
from app.config import Config
from app.extensions import cache, csrf, db, login_manager
from app.models import Admin

from .api import api
from .files import files
from .routes import main
from .storage import create_storage

logging.basicConfig(filename="flask.log", level=logging.DEBUG)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=Config.SECRET_KEY,
        SQLALCHEMY_DATABASE_URI=Config.SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL=Config.CACHE_REDIS_URL,
        STORAGE_BACKEND=Config.STORAGE_BACKEND,
        LOCAL_UPLOAD_FOLDER=Config.LOCAL_UPLOAD_FOLDER,
        AWS_PROFILE=Config.AWS_PROFILE,
        AWS_REGION=Config.AWS_REGION,
        S3_BUCKET_NAME=Config.S3_BUCKET_NAME,
        S3_UPLOAD_PREFIX=Config.S3_UPLOAD_PREFIX,
        S3_PRESIGNED_URL_EXPIRATION=Config.S3_PRESIGNED_URL_EXPIRATION,
    )

    if test_config:
        app.config.update(test_config)

    # Logging setup
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=3)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("App startup")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    cache.init_app(app)

    Migrate(app, db)

    app.extensions["storage"] = create_storage(app.config)

    app.register_blueprint(main)

    app.register_blueprint(api)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    app.register_blueprint(files)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    return app
