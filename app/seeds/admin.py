from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Admin
from app import create_app

def create_default_admin():
    app = create_app()
    with app.app_context():
        if not Admin.query.filter_by(username="admin").first():
            admin = Admin(username="admin", password=generate_password_hash("admin"))
            db.session.add(admin)
            db.session.commit()
            print("[SEED] Default admin user created.")
        else:
            print("[SEED] Admin user already exists.")
