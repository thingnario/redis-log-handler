# redis-log-handler
Handler for the std logging module which puts logs through to Redis.

## How to use
Each handler needs a channel name, and where needed a specified port, password or host.  
Handlers open a connection to a channel, so they need to be closed after use or the channel will continue to exist.

Logging can be configured globally:
```python
    log_handler = RedisLogHandler('ch:channel')
    logging.basicConfig(handlers=(log_handler,), level=logging.INFO)
    logging.info('Test-message on channel.')

    log_handler.close()
```

Or as a specific standalone logger:
```python
    log_handler = RedisLogHandler('ch:channel')
    logger = logging.getLogger('name')
    logger.addHandler(log_handler)
    logger.setLevel('WARNING')
    
    logger.warning('Warning message')
    
    log_handler.close()
```
