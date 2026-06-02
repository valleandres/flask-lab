import pytest

from app.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    env_bool,
    get_config,
    validate_config,
)


def test_get_config_defaults_to_development(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    assert get_config() is DevelopmentConfig


def test_env_bool_reads_truthy_values(monkeypatch):
    monkeypatch.setenv("FEATURE_FLAG", "true")

    assert env_bool("FEATURE_FLAG")


def test_get_config_reads_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", " TESTING ")

    assert get_config() is TestingConfig


def test_get_config_selects_production():
    assert get_config("production") is ProductionConfig


def test_development_config_uses_local_storage():
    assert DevelopmentConfig.STORAGE_BACKEND == "local"
    assert DevelopmentConfig.AWS_PROFILE is None
    assert DevelopmentConfig.S3_BUCKET_NAME is None


def test_production_config_defaults_to_aws_storage_and_cache_readiness():
    assert ProductionConfig.STORAGE_BACKEND == "s3"
    assert ProductionConfig.READINESS_CHECK_CACHE


def test_get_config_rejects_unknown_environment():
    with pytest.raises(ValueError, match="Unknown APP_ENV"):
        get_config("missing")


def test_validate_config_allows_non_production():
    validate_config({"APP_ENV": "development"})


def test_validate_config_rejects_missing_production_settings():
    with pytest.raises(
        ValueError,
        match="SECRET_KEY, JWT_SECRET_KEY, CACHE_REDIS_URL, AWS_REGION, S3_BUCKET_NAME",
    ):
        validate_config(
            {
                "APP_ENV": "production",
                "SECRET_KEY": None,
                "JWT_SECRET_KEY": None,
                "SQLALCHEMY_DATABASE_URI": "mysql://database",
                "CACHE_TYPE": "RedisCache",
                "CACHE_REDIS_URL": None,
                "STORAGE_BACKEND": "s3",
            }
        )


def test_validate_config_accepts_complete_production_settings():
    validate_config(
        {
            "APP_ENV": "production",
            "SECRET_KEY": "secret",
            "JWT_SECRET_KEY": "jwt-secret",
            "SQLALCHEMY_DATABASE_URI": "mysql://database",
            "CACHE_TYPE": "RedisCache",
            "CACHE_REDIS_URL": "redis://cache",
            "STORAGE_BACKEND": "s3",
            "AWS_REGION": "us-east-2",
            "S3_BUCKET_NAME": "bucket",
        }
    )


def test_validate_config_allows_production_without_redis_cache():
    validate_config(
        {
            "APP_ENV": "production",
            "SECRET_KEY": "secret",
            "JWT_SECRET_KEY": "jwt-secret",
            "SQLALCHEMY_DATABASE_URI": "mysql://database",
            "CACHE_TYPE": "SimpleCache",
        }
    )
