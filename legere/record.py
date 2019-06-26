import dataclasses
import textwrap
import typing

import click

COLORS = {
    None: {},
    "DEBUG": {},
    "INFO": {"fg": "cyan"},
    "WARNING": {"fg": "yellow"},
    "ERROR": {"fg": "red"},
    "CRITICAL": {"fg": "red", "bold": True},
}


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
        color = COLORS.get(self.data.get(level_key))
        record = format_string.format_map(self.data)
        record = click.style(record, **color)
        blocks = tuple(self.blocks(multiline_keys))

        if blocks:
            lines = "\n\n".join(blocks)
            return f"{record}\n\n{lines}\n"

        return record

    def blocks(self, multiline_keys: typing.Sequence[str]) -> typing.Sequence[str]:
        indent = " " * 4
        width, _ = click.get_terminal_size()
        width = width - 2 * len(indent)

        for key in multiline_keys:
            value = self.data.get(key)
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
