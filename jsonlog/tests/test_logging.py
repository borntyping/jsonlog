import logging
import logging.config

import pytest

import jsonlog


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset the logging configuration every time we run a test."""
    logging.config._clearExistingHandlers()


def test_basic_config():
    jsonlog.basicConfig()
    jsonlog.critical("Hello world")


def test_dict_config():
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {"json": {"()": "jsonlog.JSONFormatter"}},
            "handlers": {
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "DEBUG",
                }
            },
            "loggers": {"root": {"handlers": ["stream"], "level": "DEBUG"}},
        }
    )
    logging.critical("Hello world")
