import os
import logging

import redis


class RedisLogHandler(logging.StreamHandler):
    default_host: str = os.getenv('REDIS_HOST') or 'localhost'
    default_port: int = 6379

    def __init__(
            self, channel: str, host: str = None, port: int = None,
            password: str = None, connection_pool: redis.ConnectionPool = None
    ):
        super().__init__()

        self.host = host or self.default_host
        self.port = port or self.default_port
        self.channel = channel
        self.password = password
        self.redis_client = self._initialize_redis_client(connection_pool)

    def _create_redis_connection_pool(self) -> redis.ConnectionPool:
        return redis.ConnectionPool(
            host=self.host, port=self.port, password=self.password
        )

    def _initialize_redis_client(
        self, connection_pool: redis.ConnectionPool = None
    ) -> redis.Redis:
        if not connection_pool:
            connection_pool = self._create_redis_connection_pool()

        self.host = connection_pool.connection_kwargs.get('host')
        self.port = connection_pool.connection_kwargs.get('port')
        self.password = connection_pool.connection_kwargs.get('password')

        return redis.Redis(connection_pool=connection_pool)

    def emit(self, message: logging.LogRecord):
        self.redis_client.publish(self.channel, str(message))
