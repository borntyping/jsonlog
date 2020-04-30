import typing

import click
import xdg

import jsonlog_cli.config
import jsonlog_cli.key
import jsonlog_cli.pattern
import jsonlog_cli.stream
import jsonlog_cli.stream

DEFAULT_CONFIG_PATH = xdg.XDG_CONFIG_HOME / "jsonlog" / "config.json"
DEFAULT_LOG_PATH = xdg.XDG_CACHE_HOME / "jsonlog" / "internal.log"

streams_argument = click.argument(
    "streams", type=click.File(encoding="utf-8"), metavar="STREAM", nargs=-1
)


@click.group(name="jsonlog", context_settings=dict(max_content_width=120))
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=DEFAULT_CONFIG_PATH.as_posix(),
    show_default=True,
    help="Path to a configuration file.",
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
@click.pass_context
def main(ctx: click.Context, log_path: str, config_path: str) -> None:
    jsonlog_cli.config.configure_logging(log_path)

    ctx.obj = jsonlog_cli.config.Config.defaults()
    ctx.obj.load(config_path)


@main.command("template")
@click.option(
    "-t",
    "--template",
    "template_name",
    type=click.STRING,
    default="default",
    metavar="NAME",
    help="Use a named template from configured templates",
)
@click.option(
    "-f",
    "--format",
    "template_format",
    type=click.STRING,
    metavar="TEMPLATE",
    help="Override the template's format.",
)
@streams_argument
@click.pass_obj
def template_formatter(
    config: jsonlog_cli.config.Config,
    streams: typing.Sequence[jsonlog_cli.stream.TextStream],
    template_name: str,
    template_format: str,
) -> None:
    template: jsonlog_cli.pattern.TemplatePattern = config.templates[template_name]
    template = template.replace(format=template_format)

    with jsonlog_cli.stream.StreamHandler(template) as handler:
        handler.consume(streams)


@main.command("raw")
@streams_argument
def raw_formatter(streams: typing.Sequence[jsonlog_cli.stream.TextStream]) -> None:
    pattern = jsonlog_cli.pattern.RawPattern()
    stream_cls = jsonlog_cli.stream.BufferedJSONStream

    with jsonlog_cli.stream.StreamHandler(pattern, stream_cls) as handler:
        handler.consume(streams)


@main.command("kv")
@streams_argument
@click.option(
    "-p",
    "--pattern",
    "kv_name",
    type=click.STRING,
    default="default",
    help="Use a named key-value pattern from configured templates",
)
@click.option(
    "-l",
    "--level-key",
    "kv_level_key",
    type=click.STRING,
    help="Override the key for each record's log level.",
)
@click.option(
    "-m",
    "--multiline-key",
    "kv_multiline_keys_add",
    type=click.STRING,
    multiple=True,
    help="Add multiline keys to the pattern.",
)
@click.option(
    "-k",
    "--priority-key",
    "--key",
    "kv_priority_keys",
    type=click.STRING,
    multiple=True,
    help="Set keys to output first.",
)
@click.option(
    "-r",
    "--remove-key",
    "kv_remove_keys",
    type=click.STRING,
    multiple=True,
    help="Remove keys from the pattern.",
)
@click.pass_obj
def keyvalues(
    config: jsonlog_cli.config.Config,
    streams: typing.Sequence[jsonlog_cli.stream.TextStream],
    kv_name: str,
    kv_level_key: typing.Optional[str],
    kv_multiline_keys_add: typing.Sequence[str],
    kv_priority_keys: typing.Sequence[str],
    kv_remove_keys: typing.Sequence[str],
) -> None:
    """Format line-delimited JSON log records in a human-readable way."""
    pattern: jsonlog_cli.pattern.KeyValuePattern = config.keyvalues[kv_name]
    pattern = pattern.add_multiline_keys(kv_multiline_keys_add)
    pattern = pattern.remove_keys(kv_remove_keys)
    pattern = pattern.replace_keys(priority_keys=kv_priority_keys)
    pattern = pattern.replace_level_key(kv_level_key)

    with jsonlog_cli.stream.StreamHandler(pattern) as handler:
        handler.consume(streams)
