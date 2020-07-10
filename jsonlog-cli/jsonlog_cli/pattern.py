import itertools
import json
import typing

import pydantic

from .colours import Colour
from .record import Record
from .text import wrap_and_style_lines
from .types import Value

Level = typing.Optional[str]
P = typing.TypeVar("P", bound="Pattern")


class Pattern(pydantic.BaseModel):
    colours: typing.Mapping[Value, Colour] = {
        "info": Colour(fg="cyan"),
        "warning": Colour(fg="yellow"),
        "warn": Colour(fg="yellow"),
        "error": Colour(fg="red"),
        "critical": Colour(fg="red", bold=True),
        "fatal": Colour(fg="red", bold=True),
    }
    level_key: str = "level"
    multiline_json: bool = False
    multiline_keys: typing.Sequence[str] = ()

    def replace(self: P, **changes: typing.Optional[typing.Any]) -> P:
        """Return a copy of the pattern with fields replaced."""
        return self.copy(update={k: v for k, v in changes.items() if v})

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
    def format_multiline_value(value: Value) -> str:
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
        return self.colour(record.extract(self.level_key))

    def add_multiline_keys(self: P, multiline_keys: typing.Sequence[str]) -> P:
        return self.replace(multiline_keys=(*self.multiline_keys, *multiline_keys))

    def is_multiline_json(self) -> bool:
        return self.multiline_json

    def colour(self, value: Value) -> Colour:
        if value in self.colours:
            return self.colours[value]

        if isinstance(value, str):
            normalised = value.casefold()
            if normalised in self.colours:
                return self.colours[normalised]

        return Colour()


class RawPattern(Pattern):
    def format_record(self, record: Record) -> str:
        return self.format_message(record)

    def format_message(self, record: Record) -> str:
        return json.dumps(record.data, indent=None)


class TemplatePattern(Pattern):
    format: str = "{{__message__}}"

    def format_message(self, record: Record) -> str:
        return self.highlight_color(record).style(self.format.format_map(record))


class KeyValuePattern(Pattern):
    # Priority keys are rendered first, and always rendered.
    priority_keys: typing.Sequence[str] = ()

    # Removed keys have been removed from 'priority_keys' and 'multiline_keys',
    # but also need to be removed from the unknown keys in each line.
    removed_keys: typing.Sequence[str] = ()

    def format_message(self, record: Record) -> str:
        colour = self.highlight_color(record)

        known_keys = {
            *self.priority_keys,
            *self.multiline_keys,
            *self.removed_keys,
            self.level_key,
        }

        unknown_keys: typing.Sequence[str]  # Retain the record's existing order.
        unknown_keys = [k for k in record.ordered_keys() if k not in known_keys]
        format_keys = itertools.chain(self.priority_keys, unknown_keys)

        pairs = self._record_pairs(record, format_keys)
        formatted_pairs = (self._format_pair(k, v, colour) for k, v in pairs)
        return " ".join(formatted_pairs)

    @staticmethod
    def _format_pair(key: str, value: Value, colour: Colour) -> str:
        k = f"{key}="
        v = repr(value)

        if colour:
            k = Colour(fg="white").style(k)
            v = colour.style(v)

        return f"{k}{v}"

    def _record_pairs(
        self, record: Record, keys: typing.Iterable[str]
    ) -> typing.Iterable[typing.Tuple[str, Value]]:
        """
        Iterate over key=value pairs for specific keys in a record.

        A single key might return multiple pairs if it's value is a mapping.
        """
        for key in keys:
            value = record.extract(key)
            if isinstance(value, dict):
                yield from self._nested_pairs(parent=key, data=value)
            elif value is not None:
                yield key, value

    def _nested_pairs(
        self, parent: str, data: typing.Mapping[str, Value]
    ) -> typing.Iterable[typing.Tuple[str, Value]]:
        """Iterate over pairs in a mapping, prefixing each key with a "parent" key."""
        for k, v in data.items():
            nested_key = ".".join((parent, k))
            if isinstance(v, dict):
                yield from self._nested_pairs(nested_key, v)
            elif v is not None:
                yield nested_key, v

    def remove_keys(self, keys: typing.Sequence[str]) -> "KeyValuePattern":
        return self.replace(
            removed_keys=[*self.removed_keys, *keys],
            multiline_keys=[k for k in self.multiline_keys if k not in keys],
            priority_keys=[k for k in self.priority_keys if k not in keys],
        )
