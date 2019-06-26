import json
import typing

import click

from legere.record import Record


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
        record = Record(json.loads(line))
        output = record.format(
            format_string=format_string,
            multiline_keys=multiline_keys,
            level_key=level_key,
        )
        click.echo(output)
