import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Admin


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "CACHE_TYPE": "SimpleCache",
            "WTF_CSRF_ENABLED": False,
            "LOCAL_UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_admin():
    def _create_admin(username="admin", password="admin"):
        admin = Admin(username=username, password=generate_password_hash(password))
        db.session.add(admin)
        db.session.commit()
        return admin

    return _create_admin


@pytest.fixture
def create_user(client):
    def _create_user(name="Ana"):
        response = client.post("/api/users", json={"name": name})
        assert response.status_code == 201
        return response.get_json()

    return _create_user


@pytest.fixture
def create_users(create_user):
    def _create_users(*names):
        return [create_user(name) for name in names]

    return _create_users
