import sys
import typing

import click
import jsonlog

from jsonlog_cli.config import (
    Config,
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_PATH,
    ensure_log_path,
)
from jsonlog_cli.multiline import BufferedJSONStream
from jsonlog_cli.errorhandler import ErrorHandler
from jsonlog_cli.pattern import KeyValuePattern, TemplatePattern


@click.command(name="jsonlog_cli")
@click.argument(
    "streams", type=click.File(encoding="utf-8"), metavar="STREAM", nargs=-1
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=DEFAULT_CONFIG_PATH.as_posix(),
    show_default=True,
    help="A configuration file to load.",
)
@click.option(
    "-l",
    "--log",
    "log_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default=DEFAULT_LOG_PATH.as_posix(),
    show_default=True,
    help="Path to write internal logs to.",
)
@click.option(
    "-p",
    "--pattern",
    "pattern_name",
    type=click.STRING,
    default="default",
    metavar="NAME",
    help="The named pattern to format lines with.",
)
@click.option(
    "-l",
    "--level-key",
    "level_key",
    type=click.STRING,
    metavar="KEY",
    help="Override the key for each record's log level.",
)
@click.option(
    "-k",
    "--key",
    "priority_keys",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Set keys to output first.",
)
@click.option(
    "-t",
    "--template",
    "template",
    type=click.STRING,
    metavar="TEMPLATE",
    help="Set a template to format records with. Overrides --key.",
)
@click.option(
    "-m",
    "--multiline-key",
    "multiline_keys",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Add multiline keys to the pattern.",
)
@click.option(
    "-M",
    "--reset-multiline-keys",
    "reset_multiline_keys",
    is_flag=True,
    help="Remove existing multiline keys from the pattern.",
)
def main(
    streams: typing.Iterable[typing.TextIO],
    config_path: str,
    log_path: str,
    pattern_name: str,
    priority_keys: typing.Sequence[str],
    level_key: typing.Optional[str],
    template: typing.Optional[str],
    multiline_keys: typing.Optional[typing.Sequence[str]],
    reset_multiline_keys: bool,
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    jsonlog.basicConfig(filename=ensure_log_path(log_path))

    streams = streams or (sys.stdin,)
    config = Config.configure(config_path)
    pattern = config.patterns[pattern_name]
    pattern = pattern.replace(level_key=level_key)
    pattern = pattern.add_multiline_keys(multiline_keys, reset_multiline_keys)

    if priority_keys:
        assert isinstance(pattern, KeyValuePattern)
        pattern = pattern.replace(priority_keys=priority_keys)

    if template:
        assert isinstance(pattern, TemplatePattern)
        pattern = pattern.replace(template=template)

    for stream in streams:
        pattern.stream(stream)
