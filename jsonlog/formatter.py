import collections.abc
import dataclasses
import datetime
import json
import logging
import typing

JSONValue = typing.Union[str, int, float, None]
JSON = typing.Mapping[str, JSONValue]


@dataclasses.dataclass()
class BaseJSONFormatter:
    """
    This class handles the basic translation of a LogRecord to JSON.

    This class is abstract, intended for use in creating customised formatters that
    format JSON log messages. If you are not extending it, use `JSONFormatter` instead.

    This partially replicates the API of `logging.Formatter`, but features like message
    formatting and date formatting are removed.
    """

    DEFAULT_INDENT: typing.ClassVar[typing.Optional[int]] = None

    # Passed to `json.dumps()` to format JSON objects.
    indent: typing.Optional[int] = dataclasses.field(default=DEFAULT_INDENT)

    RECORD_ATTRIBUTES: typing.ClassVar[typing.Set[str]] = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a LogRecord as JSON.

        See `Formatter` for a full list of supported attributes. In addition to those
        attributes, `BaseJSONFormatter` modifies, removes or includes these attributes:

        * `asctime` - removed as we don't support the `datefmt` parameter.
        * `level` - log level processed by `format_level()`.
        * `time` - record creation time processed by `format_time()`.
        """

        # Partition a LogRecords attributes into standard attributes and attributes
        # added using the `extra` argument. Attributes from `extra` are placed into a
        # LogRecords's `__dict__` by the `Logger.makeRecord` method, which makes it
        # difficult to discover and use them in a log message.
        items = record.__dict__.items()
        extra: JSON = {k: v for k, v in items if k not in self.RECORD_ATTRIBUTES}
        attrs: JSON = {k: v for k, v in items if k in self.RECORD_ATTRIBUTES}

        # Add our generated standard attributes:
        #   * `message` is created by interpolating `msg % args`.
        #   * `time` is a value returned by `format_time()`.
        #   * `level` is a value returned by `format_level()`.
        attrs = {
            **attrs,
            "message": record.getMessage(),
            "time": self.format_time(record.created),
            "level": self.format_level(record.levelno, record.levelname),
        }

        # Add generated extra attributes - this does nothing by default, but allows
        # subclasses to add their own attributes to the extra mapping.
        extra = {**extra, **self.extra_attributes(record)}

        # These functions do nothing in BaseJSONFormatter, but subclasses can use them
        # to perform filtering on the attributes that will be included in the output.
        #
        # Without an implementation for these methods, every attribute of the record
        # will be included in the JSON object (including attributes from `extra`).
        attrs = self.filter_attrs(attrs)
        extra = self.filter_extra(extra)

        # The final payload merges both sets of attributes again.
        return json.dumps({**attrs, **extra}, indent=self.indent)

    def format_level(self, levelno: int, levelname: str) -> JSONValue:
        return levelname

    def format_time(self, time: float) -> JSONValue:
        return time

    def extra_attributes(self, record: logging.LogRecord) -> JSON:
        """Hook for subclasses to add extra attributes."""
        return {}

    def filter_attrs(self, attrs: JSON) -> JSON:
        """Hook for subclasses to filter the records's attributes."""
        return attrs

    def filter_extra(self, extra: JSON) -> JSON:
        """Hook for subclasses to filter the record's extra attributes."""
        return extra


@dataclasses.dataclass()
class JSONFormatter(BaseJSONFormatter):
    """
    Formats Python log messages as JSON.

    Timestamps are printed as ISO 8601 representations.

    Mapping arguments are included as additional attributes in the JSON object. Any
    other type of `args` value is ignored, but can still be used with `%s` style
    formatting in the message (this is done by `LogRecord.formatMessage()`.
    """

    DEFAULT_KEYS: typing.ClassVar[typing.Sequence[str]] = ("time", "level", "message")
    DEFAULT_TIMESPEC: typing.ClassVar[str] = "auto"

    # Selects the keys that are included in the JSON object
    keys: typing.Sequence[str] = dataclasses.field(default=DEFAULT_KEYS)

    # Passed to `datetime.datetime.isoformat()` to format timestamps.
    timespec: str = dataclasses.field(default=DEFAULT_TIMESPEC)

    def extra_attributes(self, record: logging.LogRecord) -> JSON:
        """If `record.args` is a mapping, we add the attributes to the payload."""
        return record.args if isinstance(record.args, collections.abc.Mapping) else {}

    def format_time(self, time: float) -> JSONValue:
        """Timestamps are printed as ISO 8601 representations."""
        return datetime.datetime.fromtimestamp(time).isoformat(timespec=self.timespec)

    def filter_attrs(self, attrs: JSON) -> JSON:
        """Filter the payload to the specific keys we want."""
        return {k: attrs[k] for k in self.keys}
