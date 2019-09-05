import typing

import click
import jsonlog

from jsonlog_cli.config import Config, DEFAULT_PATH
from jsonlog_cli.record import Record


@click.command(name="jsonlog_cli")
@click.argument("stream", type=click.File(encoding="utf-8"), default="-")
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=DEFAULT_PATH.as_posix(),
    help="The key that contains each record's log level.",
)
@click.option(
    "-p",
    "--pattern",
    "pattern_name",
    type=click.STRING,
    default="jsonlog",
    metavar="NAME",
    help="The named pattern to format lines with.",
)
@click.option(
    "-l",
    "--level-key",
    "level_key",
    type=click.STRING,
    default="level",
    metavar="KEY",
    help="Override the key for each record's log level.",
)
@click.option(
    "-t",
    "--template",
    "template",
    type=click.STRING,
    metavar="TEMPLATE",
    help="Override the template used to output each record.",
)
@click.option(
    "-m",
    "--multiline-key",
    "multiline_keys",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Override the multiline key for each record.",
)
def main(
    stream,
    config_path: str,
    pattern_name: str,
    level_key: typing.Optional[str],
    template: typing.Optional[str],
    multiline_keys: typing.Optional[typing.Sequence[str]],
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    jsonlog.basicConfig()

    config = Config.configure(config_path)
    pattern = config.patterns[pattern_name]
    pattern = pattern.replace(
        template=template, level_key=level_key, multiline_keys=multiline_keys
    )

    for line in stream:
        click.echo(Record.from_string(line).format(pattern))
