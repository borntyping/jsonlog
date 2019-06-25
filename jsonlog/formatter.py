import collections.abc
import dataclasses
import datetime
import json
import logging
import traceback
import typing
import types

JSONValue = typing.Union[str, int, float, None]
JSON = typing.Mapping[str, JSONValue]

ExcInfo = typing.Union[
    typing.Tuple[type, BaseException, typing.Optional[types.TracebackType]],
    typing.Tuple[None, None, None],
]


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

    # Passed to `json.dumps()` to format JSON objects.
    indent: typing.Optional[int] = dataclasses.field(default=DEFAULT_INDENT)

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
        keys = self.RECORD_ATTRIBUTES
        attrs: JSON = {k: v for k, v in items if k in keys and k != "exc_info"}
        extra: JSON = {k: v for k, v in items if k not in keys}

        # This adds some attributes generated from the record, all of which are
        # processed by a `format_*` method that can be overridden by a subclass. The
        # "message" attribute is normally provided by `record.getMessage()`, which our
        # default implementation of `format_message` uses.
        attrs = {
            **attrs,
            "timestamp": self.format_time(record.created),
            "level": self.format_level(record.levelno, record.levelname),
            "message": self.format_message(record),
            "traceback": self.format_tb(record.exc_info) if record.exc_info else None,
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
        payload = self.filter_payload({**attrs, **extra})

        return json.dumps(payload, indent=self.indent)

    def format_level(self, _levelno: int, levelname: str) -> JSONValue:
        """Format a value describing the log level of the record."""
        return levelname

    def format_time(self, time: float) -> JSONValue:
        """Format a timestamp describing the moment the record was created."""
        return time

    def format_message(self, record: logging.LogRecord) -> JSONValue:
        return record.getMessage()

    def format_tb(self, exc_info: ExcInfo) -> str:
        """Format an `exc_info` tuple."""
        lines = traceback.format_exception(*exc_info)
        return "".join(lines).strip()

    def extra_attributes(self, record: logging.LogRecord) -> JSON:
        """Hook for subclasses to add extra attributes."""
        return {}

    def filter_attrs(self, attrs: JSON) -> JSON:
        """Hook for subclasses to filter the records's attributes."""
        return attrs

    def filter_extra(self, extra: JSON) -> JSON:
        """Hook for subclasses to filter the record's extra attributes."""
        return extra

    def filter_payload(self, payload: JSON) -> JSON:
        """Hook for subclasses to filter the final record attributes."""
        return payload


@dataclasses.dataclass()
class JSONFormatter(BaseJSONFormatter):
    """
    Formats Python log messages as JSON.

    Standard record attributes are filtered by the `keys=` argument. All extra record
    attributes are included.

    Timestamps are printed as ISO 8601 representations. The `timespec=` argument can be
    used to control the format - see `datetime.datetime.isoformat()` for valid values.

    The `traceback` attribute is only included when the record has attacked exception
    information - any null attributes are stripped from the JSON object.
    """

    DEFAULT_KEYS: typing.ClassVar[typing.Sequence[str]] = (
        "timestamp",
        "level",
        "name",
        "message",
        "traceback",
    )
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
        """Filter the attributes to the specific keys we want."""
        return {k: attrs[k] for k in self.keys}

    def filter_payload(self, payload: JSON) -> JSON:
        """Items with a value of `None` are removed from the output."""
        return {k: v for k, v in payload.items() if v is not None}
