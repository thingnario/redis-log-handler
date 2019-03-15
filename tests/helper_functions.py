import logging

import redis

from redis_log_handler import RedisBaseHandler


def generate_logger(name: str, level: str, handler: RedisBaseHandler) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger


def generate_subscriber_on_channel(
    redis_client: redis.StrictRedis, channel: str
) -> redis.client.PubSub:
    r = redis_client.pubsub()
    r.subscribe(channel)
    return r


def close_connection_to_channel(*args: redis.client.PubSub):
    for connection in args:
        connection.close()


def is_subscriber_message_empty(message: dict) -> bool:
    is_empty = True
    if message is None:
        return is_empty

    is_empty = message.get("data", False) == 1
    return is_empty
