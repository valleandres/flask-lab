import os

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Admin
from app.seeds import admin as admin_seed


def test_create_app_creates_logs_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    app = create_app({"TESTING": True, "CACHE_TYPE": "SimpleCache"})

    assert app.testing
    assert os.path.isdir("logs")


def test_dashboard_uses_logged_in_admin(client):
    admin = Admin(username="admin", password=generate_password_hash("admin"))
    db.session.add(admin)
    db.session.commit()

    with client.session_transaction() as session:
        session["_user_id"] = str(admin.id)
        session["_fresh"] = True

    res = client.get("/dashboard")

    assert res.status_code == 200
    assert res.text == "Welcome, admin!"


def test_seed_creates_default_admin(app, monkeypatch, capsys):
    monkeypatch.setattr(admin_seed, "create_app", lambda: app)

    admin_seed.create_default_admin()

    assert Admin.query.filter_by(username="admin").one()
    assert "[SEED] Default admin user created." in capsys.readouterr().out


def test_seed_skips_existing_default_admin(app, monkeypatch, capsys):
    db.session.add(Admin(username="admin", password="hash"))
    db.session.commit()
    monkeypatch.setattr(admin_seed, "create_app", lambda: app)

    admin_seed.create_default_admin()

    assert Admin.query.filter_by(username="admin").count() == 1
    assert "[SEED] Admin user already exists." in capsys.readouterr().out
