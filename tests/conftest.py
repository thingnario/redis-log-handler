import pytest
import logging

import redis
from redis_log_handler.RedisLogHandler import RedisLogHandler


@pytest.fixture
def redis_client():
    return redis.Redis(host='localhost', port=6379, password=None)


class LogTestHelper(object):
    """Used to distribute helper methods through a fixture."""
    @staticmethod
    def generate_logger(name: str, level: str, channel: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.addHandler(RedisLogHandler(channel))
        logger.setLevel(level)

        return logger

    @staticmethod
    def generate_subscriber_on_channel(redis_client: redis.Redis, channel: str) -> redis.client.PubSub:
        r = redis_client.pubsub()
        r.subscribe(channel)
        return r

    @staticmethod
    def close_connection_to_channel(*args: redis.client.PubSub):
        for connection in args:
            connection.close()

    @staticmethod
    def is_message_data_empty(message: dict) -> bool:
        is_empty = True
        if message is None:
            return is_empty

        is_empty = message.get('data', False) == 1
        return is_empty


@pytest.fixture
def log_test_helper() -> LogTestHelper:
    return LogTestHelper()
