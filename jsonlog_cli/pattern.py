from __future__ import annotations

import dataclasses
import itertools
import json
import typing

from .colours import Colour, ColourMap
from .record import Record, RecordKey, RecordValue
from .text import wrap_and_style_lines
from .errorhandler import ErrorHandler
from .multiline import BufferedJSONStream

Level = typing.Optional[str]


@dataclasses.dataclass()
class Key:
    name: RecordKey
    template: typing.Optional[str] = None

    def format_key(self) -> str:
        return f"{self.name}="

    def format_value(self, value: RecordValue) -> str:
        if self.template is not None:
            return self.template.format(value)

        return repr(value)

    def format_pair(self, value: str, colour: Colour) -> str:
        k = self.format_key()
        v = self.format_value(value)

        if colour:
            k = Colour(fg="white").style(k)
            v = colour.style(v)

        return f"{k}{v}"


@dataclasses.dataclass()
class Pattern:
    level_key: typing.Optional[str] = "level"
    multiline_keys: typing.Sequence[str] = ()
    multiline_json: bool = False
    colours: ColourMap = dataclasses.field(default=ColourMap.default())

    def stream(self, stream: typing.TextIO) -> None:
        if self.multiline_json:
            stream = BufferedJSONStream(stream)

        with ErrorHandler() as state:
            for line in stream:
                state.echo(line, self, color=True)

    def format_record(self, record: Record) -> str:
        message = self.format_message(record)

        # We add extra whitespace to a record if it has multiline strings.
        blocks: typing.Tuple[str, ...] = tuple(self.format_multiline(record))
        if blocks:
            lines = "\n\n".join(blocks)
            return f"{message}\n\n{lines}\n"

        return message

    def format_message(self, record: Record) -> str:
        raise NotImplementedError

    def format_multiline(self, record: Record) -> typing.Iterator[str]:
        for key in self.multiline_keys:
            value = record.extract(key)
            if value:
                string = self.format_multiline_value(value)
                yield wrap_and_style_lines(string, dim=True)

    @staticmethod
    def format_multiline_value(value: RecordValue) -> str:
        """
        Transform a JSON value into something we can display in a multiline block.

        Strings are left alone (as we don't want to add quotes), lists are treated as
        individual lines, and any other values are dumped as indented JSON.
        """
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            return "\n".join(value)

        return json.dumps(value, indent=2)

    def highlight_color(self, record: Record) -> Colour:
        level = record.extract(self.level_key)
        return self.colours.get(level)

    def replace(self, **changes: typing.Any) -> Pattern:
        changes = {k: v for k, v in changes.items() if v}
        return dataclasses.replace(self, **changes)

    def add_multiline_keys(
        self, multiline_keys: typing.Sequence[str], reset_multiline_keys: bool = False
    ) -> Pattern:
        if not reset_multiline_keys:
            multiline_keys = list(itertools.chain(self.multiline_keys, multiline_keys))
        return dataclasses.replace(self, multiline_keys=multiline_keys)


@dataclasses.dataclass()
class TemplatePattern(Pattern):
    template: str = "{{__message__}}"

    def format_message(self, record: Record) -> str:
        return self.highlight_color(record).style(self.template.format_map(record.json))


@dataclasses.dataclass()
class KeyValuePattern(Pattern):
    # Priority keys are rendered first, and always rendered.
    priority_keys: typing.Sequence[Key] = ()

    def format_message(self, record: Record) -> str:
        colour = self.highlight_color(record)

        known_keys = {*self.priority_keys, *self.multiline_keys, self.level_key}
        unknown_keys = (Key(k) for k in record.keys() if k not in known_keys)
        format_keys = list(itertools.chain(self.priority_keys, unknown_keys))

        pairs = self._record_pairs(record, format_keys)
        formatted_pairs = (k.format_pair(v, colour) for k, v in pairs)
        return " ".join(formatted_pairs)

    def _record_pairs(
        self, record: Record, keys: typing.Sequence[Key]
    ) -> typing.Iterable[typing.Tuple[Key, RecordValue]]:
        """
        Iterate over key=value pairs for specific keys in a record.

        A single key might return multiple pairs if it's value is a mapping.
        """
        for key in keys:
            value = record.extract(key.name)
            if isinstance(value, dict):
                yield from self._nested_pairs(parent=key.name, data=value)
            elif value is not None:
                yield key, value

    def _nested_pairs(
        self, parent: str, data: typing.Mapping[RecordKey, RecordValue]
    ) -> typing.Iterable[typing.Tuple[Key, RecordValue]]:
        """Iterate over pairs in a mapping, prefixing each key with a "parent" key."""
        for k, v in data.items():
            nested_key = ".".join((parent, k))
            if isinstance(v, dict):
                yield from self._nested_pairs(nested_key, v)
            elif v is not None:
                yield nested_key, v

    @staticmethod
    def format_key(key: str) -> str:
        return f"{key}="

    @staticmethod
    def format_value(value: str) -> str:
        return repr(value)
