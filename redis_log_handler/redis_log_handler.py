import os
import logging

from redis import ConnectionPool, StrictRedis


class RedisBaseHandler(logging.StreamHandler):
    default_host: str = os.getenv("REDIS_HOST") or "localhost"
    default_port: int = 6379

    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        connection_pool: ConnectionPool = None,
    ):
        super().__init__()

        self.host = host or self.default_host
        self.port = port or self.default_port
        self.password = password
        self.redis_client = self._initialize_redis_client(connection_pool)

    def _create_redis_connection_pool(self) -> ConnectionPool:
        return ConnectionPool(host=self.host, port=self.port, password=self.password)

    def _initialize_redis_client(
        self, connection_pool: ConnectionPool = None
    ) -> StrictRedis:
        if not connection_pool:
            connection_pool = self._create_redis_connection_pool()

        self.host = connection_pool.connection_kwargs.get("host")
        self.port = connection_pool.connection_kwargs.get("port")
        self.password = connection_pool.connection_kwargs.get("password")

        return StrictRedis(connection_pool=connection_pool)

    def emit(self, message: logging.LogRecord):
        raise NotImplementedError("Emit functionality from base class not overridden.")


class RedisChannelHandler(RedisBaseHandler):
    def __init__(
        self,
        channel: str,
        host: str = None,
        port: int = None,
        password: str = None,
        connection_pool: ConnectionPool = None,
    ):
        super().__init__(host, port, password, connection_pool)

        self.channel = channel

    def emit(self, message: logging.LogRecord):
        self.redis_client.publish(self.channel, str(message))


class RedisKeyHandler(RedisBaseHandler):
    def __init__(
        self,
        key: str,
        ttl: int = None,
        host: str = None,
        port: int = None,
        password: str = None,
        connection_pool: ConnectionPool = None,
    ):
        super().__init__(host, port, password, connection_pool)

        self.key = key
        self.ttl = ttl

        if self.ttl:
            self.redis_client.expire(self.key, self.ttl)

    def emit(self, message: logging.LogRecord):
        self.redis_client.rpush(self.key, str(message))
