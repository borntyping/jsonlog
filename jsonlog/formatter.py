import datetime
import collections.abc
import json
import logging
import typing

JSONValue = typing.Union[str, int, float, None]
JSON = typing.Mapping[str, JSONValue]


class BaseJSONFormatter:
    """
    This class handles the basic translation of a LogRecord to JSON.

    This class is abstract, intended for use in creating customised formatters that
    format JSON log messages. If you are not extending it, use `JSONFormatter` instead.

    This partially replicates the API of `logging.Formatter`, but features like message
    formatting and date formatting are removed.
    """

    def __init__(self, *, indent: typing.Optional[int] = None):
        """
        Create a BaseJSONFormatter instance. Only keyword arguments are provided.

        * `indent` is passed to `json.dumps()` to format JSON objects.
        """
        self.indent = indent

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a LogRecord as JSON.

        See `Formatter` for a full list of supported attributes. In addition to those
        attributes, `BaseJSONFormatter` modifies, removes or includes these attributes:

        * `asctime` - removed as we don't support the `datefmt` parameter.
        * `level` - log level processed by `format_level()`.
        * `time` - record creation time processed by `format_time()`.
        """

        payload: JSON = {
            # LogRecord attributes.
            "name": record.name,
            "msg": record.msg,
            "levelname": record.levelname,
            "levelno": record.levelno,
            "pathname": record.pathname,
            "filename": record.filename,
            "module": record.module,
            "exc_info": None,
            "stack_info": None,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "created": record.created,
            "msecs": record.msecs,
            "relativeCreated": record.relativeCreated,
            "thread": record.thread,
            "threadName": record.threadName,
            "processName": record.processName,
            "process": record.process,
            # LogRecord processed values.
            "message": record.getMessage(),
            # BaseJSONFormatter attributes.
            "time": self.format_time(record.created),
            "level": self.format_level(record.levelno, record.levelname),
        }

        payload = self.payload_filter(payload)
        payload = self.payload_post_process(payload, record)
        return json.dumps(payload, indent=self.indent)

    def format_level(self, levelno: int, levelname: str) -> JSONValue:
        return levelname

    def format_time(self, time: float) -> JSONValue:
        return time

    def payload_filter(self, payload: JSON) -> JSON:
        """Hook for subclasses to filter the payload's attributes."""
        return payload

    def payload_post_process(self, payload: JSON, record: logging.LogRecord) -> JSON:
        """Hook for subclasses to add attributes after filtering."""
        return payload


class JSONFormatter(BaseJSONFormatter):
    """
    Formats Python log messages as JSON.

    Timestamps are printed as ISO 8601 representations.

    Mapping arguments are included as additional attributes in the JSON object. Any
    other type of `args` value is ignored, but can still be used with `%s` style
    formatting in the message (this is done by `LogRecord.formatMessage()`.
    """

    DEFAULT_KEYS = ("time", "level", "message")

    def __init__(
        self,
        *,
        keys: typing.Sequence[str] = DEFAULT_KEYS,
        timespec: str = "auto",
        indent: typing.Optional[int] = None
    ):
        """
        * `keys` is used to select the keys that should appear in the output.
        * `timespec` is passed to `datetime.datetime.isoformat()` to format timestamps.
        * `indent` is passed to `json.dumps()` to format JSON objects.
        """
        super().__init__(indent=indent)
        self.keys = keys
        self.timespec = timespec

    def format_time(self, time: float) -> JSONValue:
        """Timestamps are printed as ISO 8601 representations."""
        return datetime.datetime.fromtimestamp(time).isoformat(timespec=self.timespec)

    def payload_filter(self, payload: JSON) -> JSON:
        """Filter the payload to the specific keys we want."""
        return {k: payload[k] for k in self.keys}

    def payload_post_process(self, payload: JSON, record: logging.LogRecord) -> JSON:
        """If `record.args` is a mapping, we add the values from it to the payload."""
        if isinstance(record.args, collections.abc.Mapping):
            return {**payload, **record.args}
        return payload
