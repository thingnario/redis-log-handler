from setuptools import setup


setup(
    name="redis_log_handler",
    version="0.1",
    description="A log handler for the Python logging module, emitting all logs to specific Redis channels.",
    packages=["redis_log_handler"],
)