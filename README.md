# redis_log_handler
Handler for the standard `logging` module which puts logs through to Redis.

## How to use
You can either publish your logs to a channel, `rpush` them onto a key with an optional `ttl`
or implement the desired behaviour by deriving from the base class.

To add a handler to the python logger is very simple:

```python
import logging


from redis_log_handler import RedisKeyHandler

example_handler = RedisKeyHandler('example_key')  # Default parameters for Redis connection are used

logger = logging.getLogger()  # No name gives you the root logger
logger.setLevel("WARNING")
logger.addHandler(example_handler)

logger.warning("This will rpush this message to the 'example_key' in Redis.")
```

### Configuring Redis Connection
By default each handler will create a `StrictRedis` instance, passing on each argument from their `__init(**kwargs)` to the StrictRedis instantiation.
This means you can configure the connection as specific as you'd like, but every argument needs to have its keyword (`(host=localhost)` instead of `(localhost)`.
All available configuration options are available in te [python-redis documentation](https://redis-py.readthedocs.io/en/latest/).

```python
handler = RedisKeyHandler("key", host="localhost", port=6379, password=None)

connection_pool = redis.ConnectionPool(host="localhost")
handler = RedisKeyHandler("key", connection_pool=connection_pool)
```

### 1. RedisChannelHandler
This opens a connection to a redis channel, allowing subscribers to pickup new messages in realtime.
Every message triggered by the logging instance, will get published to the specified channel.
```python
handler = RedisChannelHandler("channelname")
```

### 2. RedisKeyHandler
This creates/pushes onto the provided key, whatever message the logging instance will emit.
By default every message will be sent via `rpush`, so that when the list is retrieved using `lrange $key 0 -1`, all messages are returned in the order they were sent.
Optionally a `ttl` (time to live) can be provided which will be a counter that **will be set each time** a message is sent, essentially **refreshing the duration** of the time to live for this key.
```python
handler = RedisKeyHandler("some_key_name", ttl=60)
```

### 3. Custom Redis Handler
We also provide the ability to write custom emit functions, which get picked up by the logging instance, by inheriting the Base class.
If none of the provided Redis implementations rock you boat, simply inherit the Base class and overwrite the emit() method.

In the following example we will write an example of a CustomRedisHandler which overwrites the value of the key it already exists.
```python
class CustomRedisHandler(RedisBaseHandler):
    def __init__(self, key: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.key = key

    def emit(self, message: logging.LogRecord):
        self.redis_client.set(self.key, str(message))
```