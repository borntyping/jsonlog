import logging

import pytest

import jsonlog
import jsonlog.logger
import jsonlog.tests.capture


def test_get_logger(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    log = jsonlog.getLogger(__name__)
    log.warning("User logged in", user=123)
    assert '"user": 123' in capture


class TestLogger:
    def test_class(self):
        jsonlog.basicConfig()
        assert logging._loggerClass == jsonlog.logger.JSONLogger

    def test_args(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.warning("User logged in", {"user": 123})
        assert '"user": 123' in capture

    def test_extra(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.warning("User logged in", extra={"user": 123})
        assert '"user": 123' in capture

    def test_kwargs(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.basicConfig()
        log = logging.getLogger(__name__)
        log.warning("User logged in", user=123)
        assert '"user": 123' in capture


class TestLoggerNoConfig:
    def test_class(self):
        assert logging._loggerClass == logging.Logger

    def test_kwargs(self):
        with pytest.raises(TypeError):
            log = logging.getLogger(__name__)
            log.warning("User logged in", user=123)
