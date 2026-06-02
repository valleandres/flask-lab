from importlib import import_module
from unittest.mock import Mock

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_readiness_check(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "checks": {"database": "ok"}}


def test_readiness_check_reports_database_failure(client, monkeypatch):
    session = Mock()
    session.execute.side_effect = SQLAlchemyError("database unavailable")
    monkeypatch.setattr(db, "session", session)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "unavailable",
        "checks": {"database": "error"},
    }
    session.rollback.assert_called_once_with()


def test_readiness_check_reports_cache_ok(client, app, monkeypatch):
    health_module = import_module("app.health")
    monkeypatch.setattr(health_module, "cache_readiness_status", lambda _config: "ok")
    app.config["READINESS_CHECK_CACHE"] = True

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "checks": {"database": "ok", "cache": "ok"},
    }


def test_readiness_check_reports_cache_failure(client, app, monkeypatch):
    health_module = import_module("app.health")
    monkeypatch.setattr(
        health_module, "cache_readiness_status", lambda _config: "error"
    )
    app.config["READINESS_CHECK_CACHE"] = True

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "unavailable",
        "checks": {"database": "ok", "cache": "error"},
    }
