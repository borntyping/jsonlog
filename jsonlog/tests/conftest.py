import logging
import logging.config

import _pytest.capture
import pytest

import jsonlog.tests.capture
import jsonlog.tests.records


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset the logging configuration every time we run a test."""
    logging.root.handlers = []
    logging.root.manager.loggerDict = {}
    logging.root.setLevel(logging.WARNING)
    logging.setLoggerClass(logging.Logger)


@pytest.fixture(
    params=[
        jsonlog.tests.records.simple_record,
        jsonlog.tests.records.error_record,
        jsonlog.tests.records.extra_record,
    ]
)
def record(request) -> logging.LogRecord:
    return request.param()


@pytest.fixture(autouse=True)
def capture(capsys: _pytest.capture.CaptureResult) -> jsonlog.tests.capture.Capture:
    return jsonlog.tests.capture.Capture(capsys)
