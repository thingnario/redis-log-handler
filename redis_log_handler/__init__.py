import logging
from typing import Any

from redis import StrictRedis


class RedisBaseHandler(logging.StreamHandler):
    def __init__(self, raw_logging: bool = False, **kwargs: Any):
        super().__init__()
        self.raw_logging = raw_logging
        self.redis_client = StrictRedis(**kwargs)

    def emit(self, message: logging.LogRecord):
        content = self.format(message)
        if not isinstance(content, str):
            content = content.decode('utf8')
        if self.raw_logging:
            content += "{} - {}".format(message.lineno, message.pathname)
        
        self._send(content)

    def _send(self, content):
        raise NotImplementedError("Emit functionality from base class not overridden.")


class RedisChannelHandler(RedisBaseHandler):
    def __init__(self, channel: str, **kwargs: Any):
        super().__init__(**kwargs)

        self.channel = channel

    def _send(self, content):
        self.redis_client.publish(self.channel, content)


class RedisKeyHandler(RedisBaseHandler):
    def __init__(self, key: str, ttl: int = None, **kwargs):
        super().__init__(**kwargs)

        self.key = key
        self.ttl = ttl

        if self.ttl:
            self.redis_client.expire(self.key, self.ttl)

    def _send(self, content):
        self.redis_client.rpush(self.key, content)
