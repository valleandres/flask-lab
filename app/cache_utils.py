import redis
from flask import current_app
from redis.exceptions import RedisError


def is_redis_cache_enabled(config):
    return str(config.get("CACHE_TYPE", "")).strip().lower() == "rediscache"


def redis_connection_options(config):
    options = {}
    socket_connect_timeout = config.get("CACHE_REDIS_SOCKET_CONNECT_TIMEOUT")
    socket_timeout = config.get("CACHE_REDIS_SOCKET_TIMEOUT")

    if socket_connect_timeout is not None:
        options["socket_connect_timeout"] = socket_connect_timeout
    if socket_timeout is not None:
        options["socket_timeout"] = socket_timeout

    return options


def redis_client_from_config(config):
    redis_url = config.get("CACHE_REDIS_URL")
    if not redis_url:
        raise RuntimeError("CACHE_REDIS_URL is required when CACHE_TYPE=RedisCache")
    return redis.Redis.from_url(redis_url, **redis_connection_options(config))


def route_cache_pattern(route_path, key_prefix=""):
    route_fragment = route_path.lstrip("/")
    if not key_prefix:
        return f"*{route_fragment}*"
    return f"*{key_prefix}*{route_fragment}*"


def delete_cached_route(route_path):
    cache_key_prefix = current_app.config.get("CACHE_KEY_PREFIX", "")
    return delete_cache_keys(route_cache_pattern(route_path, cache_key_prefix))


def delete_cache_keys(pattern):
    if not is_redis_cache_enabled(current_app.config):
        return 0

    try:
        redis_client = redis_client_from_config(current_app.config)
        return delete_matching_keys(redis_client, pattern)
    except (RedisError, RuntimeError) as error:
        current_app.logger.warning("Redis cache invalidation failed: %s", error)
        return 0


def delete_matching_keys(redis_client, pattern, batch_size=500):
    deleted_count = 0
    keys = []

    for key in redis_client.scan_iter(match=pattern):
        keys.append(key)
        if len(keys) >= batch_size:
            deleted_count += redis_client.delete(*keys)
            keys = []

    if keys:
        deleted_count += redis_client.delete(*keys)

    return deleted_count


def cache_readiness_status(config):
    if not config.get("READINESS_CHECK_CACHE"):
        return "skipped"
    if not is_redis_cache_enabled(config):
        return "skipped"

    try:
        redis_client_from_config(config).ping()
    except (RedisError, RuntimeError) as error:
        current_app.logger.warning("Readiness cache check failed: %s", error)
        return "error"

    return "ok"
