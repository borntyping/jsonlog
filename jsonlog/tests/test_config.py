import logging
import logging.config
import pathlib
import sys
import tempfile

import pytest

import jsonlog
import jsonlog.tests.capture


def test_basic_config(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    jsonlog.warning("Hello world")
    assert '"message": "Hello world"' in capture


def test_already_configured():
    with pytest.warns(UserWarning):
        logging.basicConfig()
        jsonlog.basicConfig()


def test_basic_config_filename():
    with tempfile.TemporaryDirectory() as tempdir:
        jsonlog.basicConfig(filename=pathlib.Path(tempdir) / "test.log")


def test_basic_config_kwargs():
    with pytest.raises(ValueError):
        jsonlog.basicConfig(stream=sys.stderr, filename="test.log")


def test_ensure_config(capture: jsonlog.tests.capture.Capture):
    jsonlog.warning("Hello world")
    assert '"message": "Hello world"' in capture


def test_dict_config(capture: jsonlog.tests.capture.Capture):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {"json": {"()": "jsonlog.JSONFormatter"}},
            "handlers": {
                "stream": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": "DEBUG",
                }
            },
            "loggers": {"": {"handlers": ["stream"], "level": "DEBUG"}},
        }
    )
    logging.warning("Hello world")
    assert '"message": "Hello world"' in capture
