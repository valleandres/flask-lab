from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

import logging

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

logging.basicConfig(filename='flask.log', level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='supersecretkey',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://user:password@db:3306/mydatabase',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)

    from .api import api
    app.register_blueprint(api)

    from .models import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return app