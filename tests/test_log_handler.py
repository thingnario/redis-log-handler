import redis
import pytest

from redis_log_handler.redis_log_handler import RedisLogHandler
from conftest import LogTestHelper


def test_redis_is_running_and_responding(redis_client: redis.Redis):
    assert redis_client.ping() is True


def test_create_handler_by_arguments(redis_host):
    handler = RedisLogHandler('ch:channel', host=redis_host, port=6379)
    assert handler is not None

    try:
        assert handler.redis_client.ping() is not None
    except redis.ConnectionError:
        pytest.fail('Creating handler by connection pool failed.')


def test_create_handler_by_connection_pool(
        redis_connection_pool: redis.ConnectionPool
):
    handler = RedisLogHandler('ch:channel', connection_pool=redis_connection_pool)
    assert handler is not None

    try:
        assert handler.redis_client.ping() is not None
    except redis.ConnectionError:
        pytest.fail('Creating handler by connection pool failed.')

def test_create_handler_for_existing_redis_connection(
        redis_connection_pool: redis.ConnectionPool,
        log_test_helper: LogTestHelper
):
    try:
        handler_with_real_host = RedisLogHandler(
            'channel', connection_pool=redis_connection_pool
        )
        log_test_helper.generate_subscriber_on_channel(
            handler_with_real_host.redis_client, handler_with_real_host.channel
        )
    except redis.ConnectionError:
        pytest.fail('Handler could not be created for existing redis connection.')


def test_create_handler_for_non_existing_redis_connection(
        log_test_helper: LogTestHelper
):
    with pytest.raises(redis.ConnectionError):
        handler_with_fake_host = RedisLogHandler('fake', host='le_cool_host')
        log_test_helper.generate_subscriber_on_channel(
            handler_with_fake_host.redis_client, handler_with_fake_host.channel
        )


def test_unique_channel_per_handler():
    handler_one = RedisLogHandler('ch:channel_01')
    handler_two = RedisLogHandler('ch:channel_02')
    handler_three = RedisLogHandler('ch:channel_03')

    assert handler_one.channel != handler_two.channel != handler_three.channel


def test_send_message_to_redis(
        redis_connection_pool: redis.ConnectionPool,
        log_test_helper: LogTestHelper
):
    handler = RedisLogHandler(
        'ch:test_channel', connection_pool=redis_connection_pool
    )
    logger = log_test_helper.generate_logger('logger', 'INFO', handler.channel)
    subscriber = log_test_helper.generate_subscriber_on_channel(
        handler.redis_client, handler.channel
    )

    message = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)
    assert log_test_helper.is_message_data_empty(message) is True

    logger.info('Test logger')
    message = subscriber.get_message(ignore_subscribe_messages=True, timeout=1)

    assert log_test_helper.is_message_data_empty(message) is False
    assert 'Test logger' in message.get('data').decode('utf-8')

    log_test_helper.close_connection_to_channel(subscriber)


def test_unique_channel_publishing(
        redis_client: redis.Redis, log_test_helper: LogTestHelper
):
    channel_one = 'ch:channel_01'
    channel_two = 'ch:channel_02'
    channel_three = 'ch:channel_03'

    subscriber_one = log_test_helper.generate_subscriber_on_channel(
        redis_client, channel_one
    )
    subscriber_two = log_test_helper.generate_subscriber_on_channel(
        redis_client, channel_two
    )
    subscriber_three = log_test_helper.generate_subscriber_on_channel(
        redis_client, channel_three
    )

    logger_one = log_test_helper.generate_logger(
        'first_logger', 'INFO', channel_one
    )
    logger_two = log_test_helper.generate_logger(
        'second_logger', 'INFO', channel_two
    )

    all_messages = (
        subscriber_one.get_message(ignore_subscribe_messages=True, timeout=1),
        subscriber_two.get_message(ignore_subscribe_messages=True, timeout=1),
        subscriber_three.get_message(ignore_subscribe_messages=True, timeout=1),
    )
    for msg in all_messages:
        assert log_test_helper.is_message_data_empty(msg) is True

    # Publish message to first channel
    logger_one.info('Test message on channel 1.')
    empty_messages = (
        subscriber_two.get_message(ignore_subscribe_messages=True, timeout=1),
        subscriber_three.get_message(ignore_subscribe_messages=True, timeout=1),
    )
    for msg in empty_messages:
        assert log_test_helper.is_message_data_empty(msg) is True

    message_one = subscriber_one.get_message(
        ignore_subscribe_messages=True, timeout=1
    )
    assert log_test_helper.is_message_data_empty(message_one) is False
    assert isinstance(message_one.get('data').decode('utf-8'), str)
    assert 'Test message on channel 1.' in message_one.get('data')\
                                                      .decode('utf-8')

    # Publish message to 2nd channel
    logger_two.info('Test message on channel 2.')
    empty_messages = (
        subscriber_one.get_message(ignore_subscribe_messages=True, timeout=1),
        subscriber_three.get_message(ignore_subscribe_messages=True, timeout=1),
    )
    for msg in empty_messages:
        assert log_test_helper.is_message_data_empty(msg) is True

    message_two = subscriber_two.get_message(
        ignore_subscribe_messages=True, timeout=1
    )
    assert log_test_helper.is_message_data_empty(message_two) is False
    assert isinstance(message_two.get('data').decode('utf-8'), str)
    assert 'Test message on channel 2.' in message_two.get('data')\
                                                      .decode('utf-8')

    log_test_helper.close_connection_to_channel(
        subscriber_one, subscriber_two, subscriber_three
    )
