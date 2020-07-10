import logging
import typing

import click
import xdg

import jsonlog_cli.config
import jsonlog_cli.pattern
import jsonlog_cli.stream

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = xdg.XDG_CONFIG_HOME / "jsonlog" / "config.json"
DEFAULT_LOG_PATH = xdg.XDG_CACHE_HOME / "jsonlog" / "internal.log"

streams_argument = click.argument(
    "streams", type=click.File(encoding="utf-8"), metavar="STREAM", nargs=-1
)


class AliasedGroup(click.Group):
    def list_commands(self, ctx: typing.Any) -> typing.Sequence[str]:
        """Only list the canonical names for each command."""
        return sorted(set(c.name for c in self.commands.values()))


@click.group(
    name="jsonlog",
    context_settings={"max_content_width": 120, "help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    cls=AliasedGroup,
)
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(file_okay=True, dir_okay=False),
    default=DEFAULT_CONFIG_PATH.as_posix(),
    show_default=True,
    help="Path to a configuration file.",
)
@click.option(
    "--log-path",
    "log_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default=DEFAULT_LOG_PATH.as_posix(),
    show_default=True,
    help="Path to write internal logs to.",
)
@click.option(
    "--log-level",
    "log_level",
    type=click.STRING,
    default="warning",
    show_default=True,
    help="Log level for internal logs.",
)
@click.pass_context
def main(ctx: click.Context, log_path: str, log_level: str, config_path: str) -> None:
    """
    Format JSON messages.
    """
    jsonlog_cli.config.configure_logging(log_path, log_level)

    ctx.obj = jsonlog_cli.config.Config.load(config_path)

    if ctx.invoked_subcommand is None:
        ctx.invoke(format_key_value)


@click.command("config")
@click.pass_obj
def display_config(config: jsonlog_cli.config.Config) -> None:
    """
    Show configuration (aliases: c).
    """
    print(config.json(indent=2))


@click.command("key-value")
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
    "kv_multiline_keys",
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
def format_key_value(
    config: jsonlog_cli.config.Config,
    streams: typing.Sequence[jsonlog_cli.stream.TextStream],
    kv_name: str,
    kv_level_key: typing.Optional[str],
    kv_multiline_keys: typing.Sequence[str],
    kv_priority_keys: typing.Sequence[str],
    kv_remove_keys: typing.Sequence[str],
) -> None:
    """
    Format messages as coloured key=value lines (aliases: k, kv).

    """
    pattern: jsonlog_cli.pattern.KeyValuePattern = config.keyvalues[kv_name]
    pattern = pattern.add_multiline_keys(kv_multiline_keys)
    pattern = pattern.remove_keys(kv_remove_keys)
    pattern = pattern.replace(priority_keys=kv_priority_keys)
    pattern = pattern.replace(level_key=kv_level_key)

    log.debug("Selected pattern", extra={"pattern": pattern.dict()})

    with jsonlog_cli.stream.StreamHandler(pattern=pattern) as handler:
        handler.consume(streams)


@click.command("raw")
@streams_argument
def format_raw(streams: typing.Sequence[jsonlog_cli.stream.TextStream]) -> None:
    """
    Format messages as JSON lines (aliases: r).

    Buffers JSON so messages split over multiple lines will be output as a single line.
    """
    pattern = jsonlog_cli.pattern.RawPattern(multiline_json=True)
    with jsonlog_cli.stream.StreamHandler(pattern=pattern) as handler:
        handler.consume(streams)


@click.command("template")
@click.option(
    "-m",
    "--multiline-key",
    "template_multiline_keys",
    type=click.STRING,
    multiple=True,
    help="Add multiline keys to the pattern.",
)
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
def format_template(
    config: jsonlog_cli.config.Config,
    streams: typing.Sequence[jsonlog_cli.stream.TextStream],
    template_multiline_keys: typing.Sequence[str],
    template_name: str,
    template_format: str,
) -> None:
    """Format messages as templated lines (aliases: t)."""
    template: jsonlog_cli.pattern.TemplatePattern = config.templates[template_name]
    template = template.replace(format=template_format)
    template = template.add_multiline_keys(template_multiline_keys)

    with jsonlog_cli.stream.StreamHandler(pattern=template) as handler:
        handler.consume(streams)


main.add_command(display_config)
main.add_command(display_config, name="c")
main.add_command(format_key_value)
main.add_command(format_key_value, name="k")
main.add_command(format_key_value, name="kv")
main.add_command(format_raw)
main.add_command(format_raw, name="r")
main.add_command(format_template)
main.add_command(format_template, name="t")
