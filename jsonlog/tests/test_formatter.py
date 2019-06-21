import logging

import jsonlog
import jsonlog.formatter
import jsonlog.tests.capture


class TestBaseFormatter:
    def test(self, record: logging.LogRecord):
        assert jsonlog.formatter.BaseJSONFormatter().format(record)

    def test_indent(self, record: logging.LogRecord) -> None:
        assert jsonlog.formatter.BaseJSONFormatter(indent=2).format(record)


class TestJSONFormatter:
    def test_format(self, record: logging.LogRecord) -> None:
        assert jsonlog.formatter.JSONFormatter().format(record)

    def test_indent(self, record: logging.LogRecord) -> None:
        formatter = jsonlog.formatter.JSONFormatter(keys=["level"], indent=2)
        assert formatter.format(record) == '{\n  "level": "INFO"\n}'

    def test_keys(self, record: logging.LogRecord) -> None:
        line = jsonlog.formatter.JSONFormatter(keys=["level", "message"]).format(record)
        assert line == '{"level": "INFO", "message": "An example log message"}'

    def test_args(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.basicConfig()
        logging.warning("%s %s", "Hello", "World")
        assert f"Hello World" in capture

    def test_args_map(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.basicConfig()
        logging.warning("%(action)s %(thing)s", {"action": "Hello", "thing": "World"})
        assert f"Hello World" in capture
        assert f'"action": "Hello"' in capture
        assert f'"thing": "World"' in capture

    def test_extra(self, capture: jsonlog.tests.capture.Capture):
        jsonlog.basicConfig()
        logging.warning("Hello world", extra={"key": "value"})
        assert '"key": "value"' in capture


def test_adaptor(capture: jsonlog.tests.capture.Capture):
    jsonlog.basicConfig()
    log = logging.getLogger(__name__)
    adaptor = logging.LoggerAdapter(log, {"hello": "world"})
    adaptor.warning("Message with extra attributes from an adaptor")
    assert '"hello": "world"' in capture
