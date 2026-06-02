import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_migrate import Migrate

from app.auth.routes import auth_bp
from app.config import get_config, validate_config
from app.extensions import cache, csrf, db, login_manager
from app.models import Admin

from .api import api
from .files import files
from .health import health
from .routes import main
from .storage import create_storage

logging.basicConfig(filename="flask.log", level=logging.DEBUG)


def create_app(config_name=None, test_config=None):
    if isinstance(config_name, dict):
        test_config = config_name
        config_name = None

    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    if test_config:
        app.config.update(test_config)

    validate_config(app.config)

    if app.config.get("CACHE_TYPE") != "RedisCache":
        app.config["CACHE_OPTIONS"] = {}

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

    app.register_blueprint(health)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    return app
