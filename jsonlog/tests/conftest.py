import logging
import logging.config

import _pytest.capture
import pytest

import jsonlog.tests.capture


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset the logging configuration every time we run a test."""
    logging.root.handlers = []
    logging.root.manager.loggerDict = {}
    logging.root.setLevel(logging.WARNING)
    logging.setLoggerClass(logging.Logger)


@pytest.fixture()
def record() -> logging.LogRecord:
    return logging.LogRecord(
        name="example",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg="An example log message",
        args={},
        exc_info=None,
    )


@pytest.fixture(autouse=True)
def capture(capsys: _pytest.capture.CaptureResult) -> jsonlog.tests.capture.Capture:
    return jsonlog.tests.capture.Capture(capsys)
