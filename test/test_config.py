import pytest

from app.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    get_config,
    validate_config,
)


def test_get_config_defaults_to_development(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    assert get_config() is DevelopmentConfig


def test_get_config_reads_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", " TESTING ")

    assert get_config() is TestingConfig


def test_get_config_selects_production():
    assert get_config("production") is ProductionConfig


def test_get_config_rejects_unknown_environment():
    with pytest.raises(ValueError, match="Unknown APP_ENV"):
        get_config("missing")


def test_validate_config_allows_non_production():
    validate_config({"APP_ENV": "development"})


def test_validate_config_rejects_missing_production_settings():
    with pytest.raises(ValueError, match="SECRET_KEY, JWT_SECRET_KEY"):
        validate_config(
            {
                "APP_ENV": "production",
                "SECRET_KEY": None,
                "JWT_SECRET_KEY": None,
                "SQLALCHEMY_DATABASE_URI": "mysql://database",
            }
        )


def test_validate_config_accepts_complete_production_settings():
    validate_config(
        {
            "APP_ENV": "production",
            "SECRET_KEY": "secret",
            "JWT_SECRET_KEY": "jwt-secret",
            "SQLALCHEMY_DATABASE_URI": "mysql://database",
        }
    )
