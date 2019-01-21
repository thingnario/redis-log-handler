import logging

import redis


class RedisLogHandler(logging.StreamHandler):
    def __init__(
            self, channel: str, host: str = None, port: int = None,
            password: str = None, redis_client: redis.Redis = None
    ):
        super().__init__()

        self.channel = channel
        self.host = host or 'localhost'
        self.port = port or 6379
        self.password = password
        self.redis_client = redis_client or self._initialize_redis_connection()

    def _initialize_redis_connection(self):
        return redis.Redis(
            host=self.host, port=self.port, password=self.password
        )

    def emit(self, message: logging.LogRecord):
        self.redis_client.publish(self.channel, str(message))
