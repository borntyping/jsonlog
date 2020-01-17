from __future__ import annotations

import dataclasses
import itertools
import json
import typing

from .colours import Colour, ColourMap
from .record import Record, RecordJSONValue
from .text import wrap_and_style_lines

Level = typing.Optional[str]


@dataclasses.dataclass()
class Pattern:
    level_key: typing.Optional[str] = "level"
    multiline_keys: typing.Sequence[str] = ()
    multiline_json: bool = False
    colours: ColourMap = dataclasses.field(default_factory=ColourMap.empty)

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
    def format_multiline_value(value: RecordJSONValue) -> str:
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
    keys: typing.Sequence[str] = ("__message__",)

    def format_message(self, record: Record) -> str:
        colour = self.highlight_color(record)
        pairs = (self.format_pair(record, key, colour) for key in self.keys)
        return " ".join(pairs)

    def format_pair(self, record: Record, key: str, colour: Colour) -> str:
        value = record.extract(key)

        k = self.format_key(key)
        v = self.format_value(value)

        if colour:
            k = Colour(fg="white").style(self.format_key(key))
            v = colour.style(self.format_value(record.extract(key)))

        return f"{k}{v}"

    @staticmethod
    def format_key(key: str) -> str:
        return f"{key}="

    @staticmethod
    def format_value(value: str) -> str:
        return repr(value)
