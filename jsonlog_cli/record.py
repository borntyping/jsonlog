import dataclasses
import json
import textwrap
import typing

import click

from jsonlog_cli.colors import color

RecordJSONValue = typing.Union[
    None, str, int, float, bool, typing.Sequence, typing.Mapping
]


class RecordDict(dict, typing.Mapping[str, RecordJSONValue]):
    """A mapping that allows access to values as if they were attributes."""

    def __getattr__(self, item) -> typing.Any:
        return self[item]


@dataclasses.dataclass()
class Record:
    data: RecordDict

    @classmethod
    def from_string(cls, value: str):
        return cls(json.loads(value, object_hook=RecordDict))

    def format(
        self,
        format_string: str,
        *,
        level_key: typing.Optional[str] = None,
        multiline_keys: typing.Sequence[str] = (),
    ) -> str:
        message = format_string.format_map(self.data)
        message = self.color(message, level_key)

        # We add extra whitespace to a record if it has multiline strings.
        blocks: typing.Tuple[str, ...] = tuple(self.blocks(multiline_keys))
        if blocks:
            lines = "\n\n".join(blocks)
            return f"{message}\n\n{lines}\n"

        return message

    def extract(self, key: typing.Optional[str]) -> RecordJSONValue:
        if key is None:
            return None

        result = self.data
        for k in key.split("."):
            try:
                result = result[k]
            except KeyError:
                return None
        return result

    def color(self, message: str, level_key: typing.Optional[str]) -> str:
        """Extract a level and use it to color the record if possible."""
        level_value = self.extract(level_key)

        if not isinstance(level_value, str):
            return message

        return color(level_value, message)

    def blocks(self, multiline_keys: typing.Sequence[str]) -> typing.Iterator[str]:
        indent = " " * 4
        width, _ = click.get_terminal_size()
        width = width - 2 * len(indent)

        for key in multiline_keys:
            value = self.extract(key)

            if value:
                string = self.value_to_string(value)
                lines = self.wrap_lines(string, width)
                lines = (click.style(l, dim=True) for l in lines)
                lines = (indent + l for l in lines)
                yield "\n".join(lines)

    @staticmethod
    def value_to_string(value: RecordJSONValue) -> str:
        """
        Transform a JSON value into something we can display in a multiline block.

        Strings are left alone (as we don't want to add quotes) and any other values are
        dumped as indented JSON.
        """
        if isinstance(value, str):
            return value

        return json.dumps(value, indent=2)

    @staticmethod
    def wrap_lines(lines: str, width: int) -> typing.Iterable[str]:
        for line in lines.splitlines():
            if len(line) < width:
                yield line
            else:
                yield from textwrap.wrap(line, width=width)
