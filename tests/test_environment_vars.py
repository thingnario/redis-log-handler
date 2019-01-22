import os

import pytest
import redis

from redis_log_handler.redis_log_handler import RedisLogHandler


def test_get_environment_var():
    assert os.getenv('REDIS_HOST') is not None


def test_valid_environment_var_host_for_redis():
    host = os.getenv('REDIS_HOST')

    try:
        r = redis.Redis(host=host)
        assert r.ping() is not None
    except redis.ConnectionError:
        pytest.fail('Cannot create redis client from environment variables.')


def test_handler_uses_environment_var_by_default():
    host = os.getenv('REDIS_HOST')
    handler = RedisLogHandler('ch:channel', host=host)

    assert handler.host is host
