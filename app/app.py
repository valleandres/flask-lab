from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import logging

db = SQLAlchemy()
csrf = CSRFProtect()
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

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app