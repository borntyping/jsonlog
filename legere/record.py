import dataclasses
import json
import textwrap
import typing

import click

from legere.colors import color

RecordJSONValue = typing.Union[str, int, float, bool, typing.Sequence, typing.Mapping]


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
        record: str = format_string.format_map(self.data)
        blocks: typing.Tuple[str, ...] = tuple(self.blocks(multiline_keys))

        # Extract a level and use it to color the record if possible.
        level_value = self.extract(level_key) if level_key else None
        record = color(level_value, record) if level_value else record

        if blocks:
            lines = "\n\n".join(blocks)
            return f"{record}\n\n{lines}\n"

        return record

    def extract(self, key: str) -> RecordJSONValue:
        result = self.data
        for k in key.split("."):
            result = result[k]
        return result

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
