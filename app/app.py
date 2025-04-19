from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

import logging

# db = SQLAlchemy()
# csrf = CSRFProtect()
# login_manager = LoginManager()

logging.basicConfig(filename='flask.log', level=logging.DEBUG)