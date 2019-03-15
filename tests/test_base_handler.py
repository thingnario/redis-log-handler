from typing import Any
import logging

import pytest

from redis_log_handler import RedisBaseHandler
from tests.helper_functions import generate_logger


def test_base_handler_without_emit_cannot_be_used():
    with pytest.raises(NotImplementedError):
        base_handler = RedisBaseHandler()
        logger = generate_logger("test_logger", "WARNING", base_handler)
        logger.warning("Using the abstract non-implemented emit method.")


def test_base_handler_derivative_with_custom_emit(redis_host):
    class DerivativeHandler(RedisBaseHandler):
        def __init__(self, **kwargs: Any):
            super().__init__(**kwargs)

        def emit(self, message: logging.LogRecord):
            self.redis_client.set("DERIVATIVE_KEY", "DERIVATIVE_VALUE")

    handler = DerivativeHandler(host=redis_host, port=6379)
    logger = generate_logger("derivative_logger", "WARNING", handler)
    logger.warning("Some trigger for the emit method.")

    assert b"DERIVATIVE_VALUE" in handler.redis_client.get("DERIVATIVE_KEY")
