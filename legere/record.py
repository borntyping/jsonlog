import dataclasses
import textwrap
import typing

import click

from legere.colors import color


@dataclasses.dataclass()
class Record:
    data: typing.Dict[str, str]

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
        level_value = self.data.get(level_key) if level_key else None
        record = color(level_value, record) if level_value else record

        if blocks:
            lines = "\n\n".join(blocks)
            return f"{record}\n\n{lines}\n"

        return record

    @staticmethod
    def color(level, message):
        if level.casefold() == "info".casefold():
            return click.style(message, fg="cyan")

    def blocks(self, multiline_keys: typing.Sequence[str]) -> typing.Iterator[str]:
        indent = " " * 4
        width, _ = click.get_terminal_size()
        width = width - 2 * len(indent)

        for key in multiline_keys:
            value = str(self.data.get(key))
            if value:
                lines = self.wrap_lines(value, width)
                lines = (click.style(l, dim=True) for l in lines)
                lines = (indent + l for l in lines)
                yield "\n".join(lines)

    @staticmethod
    def wrap_lines(lines: str, width: int) -> typing.Iterable[str]:
        for line in lines.splitlines():
            if len(line) < width:
                yield line
            else:
                yield from textwrap.wrap(line, width=width)
