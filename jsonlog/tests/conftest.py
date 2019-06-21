import pytest
import logging


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
