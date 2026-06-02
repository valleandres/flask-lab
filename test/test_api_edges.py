from importlib import import_module

import jwt

from app.api import invalidate_users_cache
from app.auth.jwt_utils import decode_token, generate_token
from app.extensions import db
from app.models import User


class FakeRedis:
    deleted = None

    def scan_iter(self, match):
        assert match == "*flask-lab:*api/users*"
        yield "api/users"

    def delete(self, *keys):
        self.deleted = keys
        return len(keys)


def test_get_users_supports_filter_sort_and_pagination(client, create_users):
    create_users("Ana", "Bruno", "Anabel")

    res = client.get("/api/users?name=Ana&sort=name&order=desc&limit=1")

    assert res.status_code == 200
    assert res.get_json()["data"] == [{"id": 3, "name": "Anabel"}]


def test_get_single_user(client, create_user):
    created = create_user("Ana")

    res = client.get(f"/api/users/{created['id']}")

    assert res.status_code == 200
    assert res.get_json() == {"id": created["id"], "name": "Ana"}


def test_create_user_requires_name(client):
    res = client.post("/api/users", json={})

    assert res.status_code == 400
    assert res.get_json() == {"error": "Missing name"}


def test_update_user(client, create_user):
    created = create_user("Ana")

    res = client.put(f"/api/users/{created['id']}", json={"name": "Bruna"})

    assert res.status_code == 200
    assert res.get_json() == {"id": created["id"], "name": "Bruna"}


def test_update_user_requires_name(client, create_user):
    created = create_user("Ana")

    res = client.put(f"/api/users/{created['id']}", json={})

    assert res.status_code == 400
    assert res.get_json() == {"error": "Missing name"}


def test_delete_user(client, create_user):
    created = create_user("Ana")

    res = client.delete(f"/api/users/{created['id']}")

    assert res.status_code == 204
    assert db.session.get(User, created["id"]) is None


def test_invalidate_users_cache_deletes_matching_redis_keys(app, monkeypatch):
    fake_redis = FakeRedis()
    cache_utils_module = import_module("app.cache_utils")
    monkeypatch.setattr(
        cache_utils_module.redis.Redis, "from_url", lambda url, **_: fake_redis
    )
    app.config["CACHE_TYPE"] = "RedisCache"

    with app.app_context():
        invalidate_users_cache()

    assert fake_redis.deleted == ("api/users",)


def test_protected_requires_token(client):
    res = client.get("/auth/protected")

    assert res.status_code == 401
    assert res.get_json() == {"error": "Missing token"}


def test_protected_rejects_invalid_token(client):
    res = client.get("/auth/protected", headers={"Authorization": "Bearer nope"})

    assert res.status_code == 401
    assert res.get_json() == {"error": "Invalid or expired token"}


def test_protected_accepts_valid_token(client, app):
    with app.app_context():
        token = generate_token(42)

    res = client.get("/auth/protected", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    assert res.get_json() == {"message": "Access granted for user 42."}


def test_decode_token_rejects_expired_token(app):
    with app.app_context():
        token = jwt.encode(
            {"user_id": 1, "exp": 0},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

        assert decode_token(token) is None


def test_index_creates_user(client):
    res = client.post("/", data={"name": "Ana"})

    assert res.status_code == 302
    assert db.session.query(User).filter_by(name="Ana").one()


def test_index_renders_form(client):
    res = client.get("/")

    assert res.status_code == 200
    assert b'<form method="POST">' in res.data
