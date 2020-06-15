import logging

import jsonlog
import jsonlog.formatter
import jsonlog.tests.capture
import jsonlog.tests.records


def test_base(record: logging.LogRecord):
    assert jsonlog.formatter.BaseJSONFormatter().format(record)


def test_base_indent(record: logging.LogRecord) -> None:
    assert jsonlog.formatter.BaseJSONFormatter(indent=2).format(record)


def test_json_format(record: logging.LogRecord) -> None:
    assert jsonlog.formatter.JSONFormatter().format(record)


def test_json_indent(record: logging.LogRecord) -> None:
    formatter = jsonlog.formatter.JSONFormatter(keys=["level"], indent=2)
    assert formatter.format(record).startswith('{\n  "level": "INFO"')


def test_json_keys(record: logging.LogRecord) -> None:
    line = jsonlog.formatter.JSONFormatter(keys=["level", "message"]).format(record)
    assert line.startswith('{"level": "INFO", "message": "')


def test_json_args(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    logging.warning("%s %s", "Hello", "World")
    assert "Hello World" in capture


def test_json_args_map(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    logging.warning("%(action)s %(thing)s", {"action": "Hello", "thing": "World"})
    assert "Hello World" in capture


def test_json_extra(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    logging.warning("Hello world", extra={"key": "value"})
    assert '"key": "value"' in capture


def test_json_error(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    try:
        raise jsonlog.tests.records.ExampleException
    except jsonlog.tests.records.ExampleException as exc_info:
        logging.error("An exception occurred", exc_info=exc_info)
    assert '"traceback": ' in capture


def test_json_exception(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    try:
        raise jsonlog.tests.records.ExampleException
    except jsonlog.tests.records.ExampleException:
        logging.exception("An exception occurred")
    assert '"traceback": ' in capture


def test_json_null(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    jsonlog.warning("No exc_info, traceback should be hidden")
    assert '"traceback": ' not in capture


def test_adaptor(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    log = logging.getLogger(__name__)
    adaptor = logging.LoggerAdapter(log, {"hello": "world"})
    adaptor.warning("Message with extra attributes from an adaptor")
    assert '"hello": "world"' in capture
