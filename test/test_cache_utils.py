from unittest.mock import Mock

from redis.exceptions import RedisError

from app.cache_utils import (
    cache_readiness_status,
    delete_cache_keys,
    delete_cached_route,
    delete_matching_keys,
    is_redis_cache_enabled,
    redis_client_from_config,
    redis_connection_options,
    route_cache_pattern,
)


class FakeRedis:
    def __init__(self, keys=None, ping_error=None):
        self.keys_result = keys or []
        self.ping_error = ping_error
        self.deleted = None
        self.pattern = None
        self.ping_called = False

    def scan_iter(self, match):
        self.pattern = match
        yield from self.keys_result

    def delete(self, *keys):
        self.deleted = (self.deleted or []) + [keys]
        return len(keys)

    def ping(self):
        self.ping_called = True
        if self.ping_error:
            raise self.ping_error
        return True


class FailingRedis(FakeRedis):
    def scan_iter(self, match):
        self.pattern = match
        raise RedisError("cache down")


def test_route_cache_pattern_includes_prefix_and_route():
    assert route_cache_pattern("/api/users", "flask-lab:") == "*flask-lab:*api/users*"


def test_route_cache_pattern_allows_empty_prefix():
    assert route_cache_pattern("/api/users") == "*api/users*"


def test_is_redis_cache_enabled():
    assert is_redis_cache_enabled({"CACHE_TYPE": "RedisCache"})
    assert is_redis_cache_enabled({"CACHE_TYPE": " rediscache "})
    assert not is_redis_cache_enabled({"CACHE_TYPE": "SimpleCache"})


def test_redis_connection_options_includes_timeouts():
    assert redis_connection_options(
        {
            "CACHE_REDIS_SOCKET_CONNECT_TIMEOUT": 1,
            "CACHE_REDIS_SOCKET_TIMEOUT": 2,
        }
    ) == {"socket_connect_timeout": 1, "socket_timeout": 2}


def test_redis_client_from_config_requires_url():
    try:
        redis_client_from_config({"CACHE_REDIS_URL": ""})
    except RuntimeError as error:
        assert "CACHE_REDIS_URL" in str(error)
    else:
        raise AssertionError("Expected RuntimeError")


def test_redis_client_from_config_uses_url_and_options(monkeypatch):
    fake_client = object()

    def fake_from_url(url, **options):
        assert url == "redis://cache:6379/0"
        assert options == {"socket_connect_timeout": 1, "socket_timeout": 2}
        return fake_client

    monkeypatch.setattr("app.cache_utils.redis.Redis.from_url", fake_from_url)

    assert (
        redis_client_from_config(
            {
                "CACHE_REDIS_URL": "redis://cache:6379/0",
                "CACHE_REDIS_SOCKET_CONNECT_TIMEOUT": 1,
                "CACHE_REDIS_SOCKET_TIMEOUT": 2,
            }
        )
        is fake_client
    )


def test_delete_cache_keys_skips_non_redis_cache(app, monkeypatch):
    fake_from_url = Mock()
    monkeypatch.setattr("app.cache_utils.redis.Redis.from_url", fake_from_url)
    app.config["CACHE_TYPE"] = "SimpleCache"

    with app.app_context():
        assert delete_cache_keys("*api/users*") == 0

    fake_from_url.assert_not_called()


def test_delete_cache_keys_deletes_matching_keys(app, monkeypatch):
    fake_redis = FakeRedis(keys=["flask-lab:view//api/users"])
    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config["CACHE_TYPE"] = "RedisCache"

    with app.app_context():
        assert delete_cache_keys("*api/users*") == 1

    assert fake_redis.pattern == "*api/users*"
    assert fake_redis.deleted == [("flask-lab:view//api/users",)]


def test_delete_cached_route_uses_configured_key_prefix(app, monkeypatch):
    fake_redis = FakeRedis(keys=["flask-lab:view//api/users"])
    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config["CACHE_TYPE"] = "RedisCache"

    with app.app_context():
        assert delete_cached_route("/api/users") == 1

    assert fake_redis.pattern == "*flask-lab:*api/users*"


def test_delete_matching_keys_batches_large_matches():
    fake_redis = FakeRedis(keys=["one", "two", "three"])

    assert delete_matching_keys(fake_redis, "*", batch_size=2) == 3

    assert fake_redis.deleted == [("one", "two"), ("three",)]


def test_delete_cache_keys_handles_empty_match(app, monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config["CACHE_TYPE"] = "RedisCache"

    with app.app_context():
        assert delete_cache_keys("*api/users*") == 0

    assert fake_redis.deleted is None


def test_delete_cache_keys_handles_redis_error(app, monkeypatch):
    fake_redis = FailingRedis()

    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config["CACHE_TYPE"] = "RedisCache"

    with app.app_context():
        assert delete_cache_keys("*api/users*") == 0


def test_cache_readiness_status_skips_when_disabled(app):
    with app.app_context():
        assert cache_readiness_status(app.config) == "skipped"


def test_cache_readiness_status_skips_non_redis_cache(app):
    app.config.update(READINESS_CHECK_CACHE=True, CACHE_TYPE="SimpleCache")

    with app.app_context():
        assert cache_readiness_status(app.config) == "skipped"


def test_cache_readiness_status_reports_ok(app, monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config.update(READINESS_CHECK_CACHE=True, CACHE_TYPE="RedisCache")

    with app.app_context():
        assert cache_readiness_status(app.config) == "ok"

    assert fake_redis.ping_called


def test_cache_readiness_status_reports_error(app, monkeypatch):
    fake_redis = FakeRedis(ping_error=RedisError("cache down"))
    monkeypatch.setattr(
        "app.cache_utils.redis.Redis.from_url", lambda _url, **_options: fake_redis
    )
    app.config.update(READINESS_CHECK_CACHE=True, CACHE_TYPE="RedisCache")

    with app.app_context():
        assert cache_readiness_status(app.config) == "error"
