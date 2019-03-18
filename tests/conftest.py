import os

from redis import StrictRedis, ConnectionPool
import pytest


@pytest.fixture
def redis_client():
    return StrictRedis(host=os.getenv("REDIS_HOST"))


@pytest.fixture
def redis_connection_pool():
    return ConnectionPool(host=os.getenv("REDIS_HOST"))


@pytest.fixture
def redis_host():
    return os.getenv("REDIS_HOST")


@pytest.fixture(autouse=True)
def clean_redis_test_keys():
    yield
    redis = StrictRedis(host=os.getenv("REDIS_HOST"))
    for key in redis.keys("*test*"):
        redis.delete(key)
