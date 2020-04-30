from __future__ import annotations

import dataclasses
import itertools
import json
import typing

from .colours import Colour, ColourMap
from .key import Key
from .record import Record, RecordFormatter, RecordKey, RecordValue
from .text import wrap_and_style_lines

Level = typing.Optional[str]
T = typing.TypeVar("T")


@dataclasses.dataclass(frozen=True)
class Pattern(RecordFormatter):
    colours: ColourMap = dataclasses.field(default=ColourMap.default())
    level_key: Key = dataclasses.field(default=Key("level"))
    multiline_json: bool = dataclasses.field(default=False)
    multiline_keys: typing.Sequence[Key] = dataclasses.field(default=())

    def replace(self: T, **changes: typing.Optional[typing.Any]) -> T:
        """Return a copy of the pattern with fields replaced."""
        changes = {k: v for k, v in changes.items() if v}
        return dataclasses.replace(self, **changes)

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
            value = record.extract(key.name)
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
        level = record.extract(self.level_key.name)
        return self.colours.get(level)


@dataclasses.dataclass(frozen=True)
class RawPattern(Pattern):
    def format_record(self, record: Record) -> str:
        return self.format_message(record)

    def format_message(self, record: Record) -> str:
        return json.dumps(record.data, indent=None)


@dataclasses.dataclass(frozen=True)
class TemplatePattern(Pattern):
    format: str = "{{__message__}}"

    def format_message(self, record: Record) -> str:
        return self.highlight_color(record).style(self.format.format_map(record))


@dataclasses.dataclass(frozen=True)
class KeyValuePattern(Pattern):
    # Priority keys are rendered first, and always rendered.
    priority_keys: typing.Sequence[Key] = ()

    # Removed keys have been removed from 'priority_keys' and 'multiline_keys',
    # but also need to be removed from the unknown keys in each line.
    removed_keys: typing.Sequence[Key] = ()

    def format_message(self, record: Record) -> str:
        colour = self.highlight_color(record)

        known_keys = {
            *self.priority_keys,
            *self.multiline_keys,
            *self.removed_keys,
            self.level_key,
        }

        unknown_keys: typing.Sequence[Key]  # Retain the record's existing order.
        unknown_keys = [Key(k) for k in record.keys() if Key(k) not in known_keys]
        format_keys = itertools.chain(self.priority_keys, unknown_keys)

        pairs = self._record_pairs(record, format_keys)
        formatted_pairs = (k.format_pair(v, colour) for k, v in pairs)
        return " ".join(formatted_pairs)

    def _record_pairs(
        self, record: Record, keys: typing.Iterable[Key]
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
                yield Key(nested_key), v

    @staticmethod
    def format_key(key: str) -> str:
        return f"{key}="

    @staticmethod
    def format_value(value: str) -> str:
        return repr(value)

    def replace_keys(self, **kwargs: typing.Sequence[str]) -> KeyValuePattern:
        changes = {a: Key.from_strings(keys) for a, keys in kwargs.items()}
        return self.replace(**changes)

    def replace_level_key(self, key: typing.Optional[str]):
        return self.replace(level_ley=Key.from_string(key) if key is not None else None)

    def add_multiline_keys(self, keys: typing.Sequence[str]) -> KeyValuePattern:
        multiline_keys = Key.from_strings(keys)
        return self.replace(multiline_keys=(*self.multiline_keys, *multiline_keys))

    def remove_keys(self, keys: typing.Sequence[str]) -> KeyValuePattern:
        removed_keys = Key.from_strings(keys)
        return self.replace(
            removed_keys=[*self.removed_keys, *removed_keys],
            multiline_keys=[k for k in self.multiline_keys if k not in removed_keys],
            priority_keys=[k for k in self.priority_keys if k not in removed_keys],
        )
