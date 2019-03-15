import os

import pytest
import redis

from redis_log_handler import RedisChannelHandler


def test_get_environment_var():
    assert os.getenv("REDIS_HOST") is not None


def test_valid_environment_var_host_for_redis():
    host = os.getenv("REDIS_HOST")

    try:
        r = redis.StrictRedis(host=host)
        assert r.ping() is not None
    except redis.ConnectionError:
        pytest.fail("Cannot create redis client from environment variables.")


def test_handler_uses_environment_var_by_default():
    host = os.getenv("REDIS_HOST")
    handler = RedisChannelHandler("ch:channel", host=host)

    assert host is handler.redis_client.connection_pool.connection_kwargs.get("host")


def test_redis_is_running_and_responding(redis_client: redis.StrictRedis):
    assert redis_client.ping() is True
