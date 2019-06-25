import dataclasses
import json
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
    level: str
    data: typing.Dict[str, str]

    def format(self, format_string: str, multiline_keys: typing.Sequence[str]) -> str:
        color = COLORS.get(self.level)
        record = format_string.format_map(self.data)
        record = click.style(record, **color)
        lines = self.lines(multiline_keys)
        return "\n".join((record, *lines))

    def lines(self, multiline_keys: typing.Sequence[str]) -> typing.Sequence[str]:
        indent = " " * 4
        width, _ = click.get_terminal_size()
        width = width - 2 * len(indent)

        for key in multiline_keys:
            value = self.data.get(key)
            if value:
                yield ""
                for line in self.wrap_lines(value, width):
                    yield indent + click.style(line, dim=True)
                yield ""

    @staticmethod
    def wrap_lines(lines: str, width: int) -> typing.Iterable[str]:
        for line in lines.splitlines():
            if len(line) < width:
                yield line
            else:
                yield from textwrap.wrap(line, width=width)


@click.command(name="legere")
@click.argument("stream", type=click.File(encoding="utf-8"), default="-")
@click.option(
    "--level-key",
    type=click.STRING,
    default="level",
    help="The key that contains each record's log level.",
)
@click.option(
    "-f",
    "--format",
    "format_string",
    type=click.STRING,
    default="{timestamp} {level} {name} {message}",
    help="Keys to display for each record.",
)
@click.option(
    "-m",
    "--multiline-keys",
    type=click.STRING,
    multiple=True,
    default=["traceback"],
    help="Keys to treat as multiline keys.",
)
def main(
    stream, level_key: str, format_string: str, multiline_keys: typing.Sequence[str]
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    for line in stream:
        data = json.loads(line)
        record = Record(level=data.get(level_key), data=data)
        output = record.format(format_string, multiline_keys)
        click.echo(output)
