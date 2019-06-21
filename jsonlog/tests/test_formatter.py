import logging

import jsonlog.formatter


def test_base(record: logging.LogRecord):
    assert jsonlog.formatter.BaseJSONFormatter().format(record)


def test_base_indent(record: logging.LogRecord) -> None:
    assert jsonlog.formatter.BaseJSONFormatter(indent=2).format(record)


def test_format(record: logging.LogRecord) -> None:
    assert jsonlog.formatter.JSONFormatter().format(record)


def test_indent(record: logging.LogRecord) -> None:
    formatter = jsonlog.formatter.JSONFormatter(keys=["level"], indent=2)
    assert formatter.format(record) == '{\n  "level": "INFO"\n}'


def test_keys(record: logging.LogRecord) -> None:
    line = jsonlog.formatter.JSONFormatter(keys=["level", "message"]).format(record)
    assert line == '{"level": "INFO", "message": "An example log message"}'
