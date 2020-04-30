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
from jsonlog_cli.pattern import KeyValuePattern, TemplatePattern, Pattern
from jsonlog_cli.key import Key


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
    "_priority_keys",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Set keys to output first.",
)
@click.option(
    "-r",
    "--remove-key",
    "_remove_keys",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Remove keys from the pattern.",
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
    "--add-multiline-key",
    "_multiline_keys_add",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Add multiline keys to the pattern.",
)
@click.option(
    "-M",
    "--replace-multiline-key",
    "_multiline_keys_replace",
    type=click.STRING,
    multiple=True,
    metavar="KEY",
    help="Replace the patterns existing multiline keys.",
)
def main(
    streams: typing.Iterable[typing.TextIO],
    config_path: str,
    log_path: str,
    pattern_name: str,
    level_key: typing.Optional[str],
    template: typing.Optional[str],
    _multiline_keys_add: typing.Sequence[str],
    _multiline_keys_replace: typing.Sequence[str],
    _priority_keys: typing.Sequence[str],
    _remove_keys: typing.Sequence[str],
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    jsonlog.basicConfig(filename=ensure_log_path(log_path))

    remove_keys = Key.from_strings(_remove_keys)
    multiline_keys_add = Key.from_strings(_multiline_keys_add)
    multiline_keys_replace = Key.from_strings(_multiline_keys_replace)
    priority_keys = Key.from_strings(_priority_keys)

    streams = streams or (sys.stdin,)
    config: Config = Config.configure(config_path)
    pattern: Pattern = config.patterns[pattern_name]

    if level_key:
        pattern = pattern.replace(level_key=Key.from_string(level_key))

    if multiline_keys_replace:
        pattern = pattern.replace(multiline_keys=multiline_keys_replace)

    if multiline_keys_add:
        multiline_keys = (*pattern.multiline_keys, *multiline_keys_add)
        pattern = pattern.replace(multiline_keys=multiline_keys)

    if priority_keys:
        assert isinstance(pattern, KeyValuePattern)
        pattern = pattern.replace(priority_keys=priority_keys)

    if remove_keys:
        assert isinstance(pattern, KeyValuePattern)
        pattern = pattern.remove_keys(remove_keys)

    if template:
        assert isinstance(pattern, TemplatePattern)
        pattern = pattern.replace(template=template)

    for stream in streams:
        pattern.stream(stream)
