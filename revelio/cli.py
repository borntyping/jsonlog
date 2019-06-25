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
    important_values: typing.Dict[str, str]
    multiline_values: typing.Dict[str, str]

    def __str__(self):
        color = COLORS.get(self.level)
        string = " ".join(
            [click.style(v, **color) for _, v in self.important_values.items()]
        )

        indent = " " * 4
        width, _ = click.get_terminal_size()
        width = width - 2 * len(indent)

        for key, value in self.multiline_values.items():
            string += "\n"
            for original_line in value.splitlines():
                for line in textwrap.wrap(original_line, width):
                    string += "\n" + indent + click.style(line)
            string += "\n"

        return string


@click.command(name="revelio")
@click.argument("stream", type=click.File(encoding="utf-8"), default="-")
@click.option(
    "--level-key",
    type=click.STRING,
    default="level",
    help="The key that contains each record's log level.",
)
@click.option(
    "-k",
    "--keys",
    type=click.STRING,
    multiple=True,
    default=["time", "level", "name", "message"],
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
    stream,
    level_key: str,
    keys: typing.Sequence[str],
    multiline_keys: typing.Sequence[str],
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    for line in stream:
        data = json.loads(line)

        record = Record(
            level=data.get(level_key),
            important_values={k: v for k, v in data.items() if k in keys},
            multiline_values={k: v for k, v in data.items() if k in multiline_keys},
        )

        click.echo(record)
