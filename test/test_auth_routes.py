from app.auth.jwt_utils import decode_token


def test_login_returns_token_for_valid_admin(client, create_admin, app):
    admin = create_admin()

    res = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data
    with app.app_context():
        assert decode_token(data["token"]) == admin.id


def test_login_rejects_invalid_password(client, create_admin):
    create_admin()

    res = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert res.status_code == 401
    assert res.get_json() == {"error": "Invalid credentials"}


def test_login_rejects_unknown_user(client):
    res = client.post(
        "/auth/login",
        json={"username": "missing", "password": "admin"},
    )

    assert res.status_code == 401
    assert res.get_json() == {"error": "Invalid credentials"}
