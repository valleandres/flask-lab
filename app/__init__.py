import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_migrate import Migrate

from app import models
from app.auth.routes import auth_bp
from app.extensions import cache, csrf, db, login_manager
from app.models import Admin, Dummy, User

from .api import api
from .models import Admin
from .routes import main

logging.basicConfig(filename="flask.log", level=logging.DEBUG)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="supersecretkey",
        SQLALCHEMY_DATABASE_URI="mysql+pymysql://user:password@db:3306/mydatabase",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="RedisCache",
        CACHE_REDIS_URL="redis://redis:6379/0",
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

    # migrate = Migrate(app, db)
    Migrate(app, db)

    app.register_blueprint(main)

    # from .auth import auth
    # app.register_blueprint(auth)
    app.register_blueprint(api)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # with app.app_context():
    #     db.create_all()

    return app
