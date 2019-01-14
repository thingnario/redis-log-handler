import redis

from redis_log_handler.RedisLogHandler import RedisLogHandler
from conftest import LogTestHelper


def test_ping_redis(redis_client: redis.Redis):
    assert redis_client.ping() is True


def test_send_message_to_redis(redis_client: redis.Redis, log_test_helper: LogTestHelper):
    handler = RedisLogHandler('ch:test_channel')
    logger = log_test_helper.generate_logger('logger', 'INFO', handler.channel)
    subscriber = log_test_helper.generate_subscriber_on_channel(redis_client, handler.channel)

    message = subscriber.get_message()
    assert log_test_helper.is_message_data_empty(message) is True

    logger.info('Test logger')
    message = subscriber.get_message()

    assert log_test_helper.is_message_data_empty(message) is False
    assert 'Test logger' in message.get('data').decode('utf-8')

    log_test_helper.close_connection_to_channel(subscriber)


def test_unique_channel_per_handler():
    handler_one = RedisLogHandler('ch:channel_01')
    handler_two = RedisLogHandler('ch:channel_02')
    handler_three = RedisLogHandler('ch:channel_03')

    assert handler_one.channel != handler_two.channel != handler_three.channel


def test_unique_channel_publishing(redis_client: redis.Redis, log_test_helper: LogTestHelper):
    channel_one = 'ch:channel_01'
    channel_two = 'ch:channel_02'
    channel_three = 'ch:channel_03'

    subscriber_one = log_test_helper.generate_subscriber_on_channel(redis_client, channel_one)
    subscriber_two = log_test_helper.generate_subscriber_on_channel(redis_client, channel_two)
    subscriber_three = log_test_helper.generate_subscriber_on_channel(redis_client, channel_three)

    logger_one = log_test_helper.generate_logger('first_logger', 'INFO', channel_one)
    logger_two = log_test_helper.generate_logger('second_logger', 'INFO', channel_two)

    for msg in (subscriber_one.get_message(), subscriber_two.get_message(), subscriber_three.get_message()):
        assert log_test_helper.is_message_data_empty(msg) is True

    # Publish message to first channel
    logger_one.info('Test message on channel 1.')
    for msg in (subscriber_two.get_message(), subscriber_three.get_message()):
        assert log_test_helper.is_message_data_empty(msg) is True

    message_one = subscriber_one.get_message()
    assert log_test_helper.is_message_data_empty(message_one) is False
    assert isinstance(message_one.get('data').decode('utf-8'), str)
    assert 'Test message on channel 1.' in message_one.get('data').decode('utf-8')

    # Publish message to 2nd channel
    logger_two.info('Test message on channel 2.')
    for msg in (subscriber_one.get_message(), subscriber_three.get_message()):
        assert log_test_helper.is_message_data_empty(msg) is True

    message_two = subscriber_two.get_message()
    assert log_test_helper.is_message_data_empty(message_two) is False
    assert isinstance(message_two.get('data').decode('utf-8'), str)
    assert 'Test message on channel 2.' in message_two.get('data').decode('utf-8')

    log_test_helper.close_connection_to_channel(subscriber_one, subscriber_two, subscriber_three)

