import pytest
import redis

from redis_log_handler import RedisKeyHandler
from tests.helper_functions import generate_logger


def test_connecting_key_handler_by_arguments(redis_host):
    handler = RedisKeyHandler("some_key", host=redis_host, port=6379)
    assert handler is not None

    try:
        assert handler.redis_client.ping() is not None
    except redis.ConnectionError:
        pytest.fail("Creating handler by connection pool failed.")


def test_create_handler_by_connection_pool(redis_connection_pool: redis.ConnectionPool):
    handler = RedisKeyHandler("some_key", connection_pool=redis_connection_pool)
    assert handler is not None

    try:
        assert handler.redis_client.ping() is not None
    except redis.ConnectionError:
        pytest.fail("Creating handler by connection pool failed.")


def test_create_handler_for_existing_redis_connection(
    redis_connection_pool: redis.ConnectionPool,
):
    try:
        handler_with_real_host = RedisKeyHandler(
            "some_key", connection_pool=redis_connection_pool
        )
        handler_with_real_host.redis_client.set(
            "some_test_key", "some_test_value", ex=1
        )
    except redis.ConnectionError:
        pytest.fail("Handler could not be created for existing redis connection.")


def test_create_handler_for_non_existing_redis_connection():
    with pytest.raises(redis.ConnectionError):
        handler_with_fake_host = RedisKeyHandler("fake", host="le_cool_host")
        handler_with_fake_host.redis_client.set(
            "some_test_key", "some_test_value", ex=1
        )


def test_send_message_to_redis(redis_connection_pool: redis.ConnectionPool,):
    handler = RedisKeyHandler("some_test_key", connection_pool=redis_connection_pool)
    logger = generate_logger("logger", "INFO", handler)

    message = handler.redis_client.lrange("some_test_key", 0, -1)
    assert len(message) is 0

    logger.info("Test logger")

    message = handler.redis_client.lrange("some_test_key", 0, -1)
    assert message is not None
    assert len(message) > 0


def test_read_pure_message(redis_connection_pool: redis.ConnectionPool,):
    handler = RedisKeyHandler("some_test_key", connection_pool=redis_connection_pool)
    logger = generate_logger("logger", "INFO", handler)

    message = handler.redis_client.lrange("some_test_key", 0, -1)
    assert len(message) is 0

    logger.info("Test logger")

    message = handler.redis_client.lrange("some_test_key", 0, -1)
    assert message is not None
    assert len(message) > 0
    assert message[0] == b"Test logger"


def test_read_raw_message(redis_connection_pool: redis.ConnectionPool,):
    handler = RedisKeyHandler(
        "another_test_key", raw_logging=True, connection_pool=redis_connection_pool
    )
    logger = generate_logger("another_logger", "INFO", handler)

    message = handler.redis_client.lrange("another_test_key", 0, -1)
    assert len(message) is 0

    logger.info("Test logger")

    message = handler.redis_client.lrange("another_test_key", 0, -1)
    assert message is not None
    assert len(message) > 0
    assert message[0] != b"Test logger"
    assert b"Test logger" in message[0]


def test_logging_sends_messages(redis_connection_pool: redis.ConnectionPool):
    handler = RedisKeyHandler("test_key", connection_pool=redis_connection_pool)

    message = handler.redis_client.lrange("test_key", 0, -1)
    assert len(message) is 0

    logger = generate_logger("logger", "INFO", handler)
    logger.info("This is a tester message")

    message = handler.redis_client.lrange("test_key", 0, -1)
    assert len(message) is 1
    assert b"This is a tester message" in message.pop()
