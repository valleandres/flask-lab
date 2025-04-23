from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

# logging.basicConfig(filename='flask.log', level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='supersecretkey',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://user:password@db:3306/mydatabase',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Logging setup
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=3)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("App startup")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    # from .auth import auth
    # app.register_blueprint(auth)

    from .api import api
    app.register_blueprint(api)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .models import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return app