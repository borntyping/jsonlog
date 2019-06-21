import logging

import pytest

import jsonlog
import jsonlog.logger
import jsonlog.tests.capture


def test_config():
    jsonlog.basicConfig()
    assert logging._loggerClass == jsonlog.logger.JSONLogger


def test_args(capture: jsonlog.tests.capture.Capture):
    jsonlog.warning("User logged in", {"user": 123})
    assert '"user": 123' in capture


def test_kwargs(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    log = logging.getLogger(__name__)
    log.warning("User logged in", user=123)
    assert '"user": 123' in capture


def test_without_config():
    assert logging._loggerClass == logging.Logger


def test_kwargs_without_config():
    with pytest.raises(TypeError):
        log = logging.getLogger(__name__)
        log.warning("User logged in", user=123)


def test_invalid():
    with pytest.raises(ValueError):
        log = jsonlog.getLogger(__name__)
        log.warning("User logged in", {"user": 123}, user=123)
