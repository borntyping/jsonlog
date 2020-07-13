import logging
import pathlib
import sys
import typing

import pydantic

import jsonlog
import jsonlog_cli.colours
import jsonlog_cli.pattern

log = logging.getLogger(__name__)

DEFAULT_KEYVALUES = {
    "default": jsonlog_cli.pattern.KeyValuePattern(
        multiline_keys=("traceback", "stacktrace")
    ),
    "elasticsearch": jsonlog_cli.pattern.KeyValuePattern(
        priority_keys=(
            "timestamp",
            "level",
            "type",
            "component",
            "cluster.name",
            "node.name",
            "message",
        ),
        multiline_keys=("stacktrace",),
        multiline_json=True,
    ),
    "jsonlog": jsonlog_cli.pattern.KeyValuePattern(
        priority_keys=("timestamp", "level", "name", "message"),
        multiline_keys=("traceback",),
    ),
    "snyk": jsonlog_cli.pattern.KeyValuePattern(
        priority_keys=("time", "msg", "reason.response.body.message"),
        multiline_keys=("__json__",),
        colours={
            20: jsonlog_cli.colours.Colour(fg="cyan"),
            50: jsonlog_cli.colours.Colour(fg="red"),
        },
    ),
    "jaeger": jsonlog_cli.pattern.KeyValuePattern(
        multiline_keys=("errorVerbose", "stacktrace")
    ),
    "vault": jsonlog_cli.pattern.KeyValuePattern(
        level_key="@level", priority_keys=("@timestamp", "@module", "@message"),
    ),
}
DEFAULT_TEMPLATES = {
    "default": jsonlog_cli.pattern.TemplatePattern(format="{__line__}"),
}


class Config(pydantic.BaseModel):
    keyvalues: typing.Dict[str, jsonlog_cli.pattern.KeyValuePattern] = pydantic.Field(
        default_factory=dict
    )
    templates: typing.Dict[str, jsonlog_cli.pattern.TemplatePattern] = pydantic.Field(
        default_factory=dict
    )

    @classmethod
    def load(cls, filename: str) -> "Config":
        path: pathlib.Path = pathlib.Path(filename)
        log.info(
            "Loading configuration from file",
            extra={"path": str(path), "exists": path.exists()},
        )
        config = cls(
            keyvalues=DEFAULT_KEYVALUES.copy(), templates=DEFAULT_TEMPLATES.copy(),
        )

        if path.exists():
            log.info(
                "Reading configuration from file",
                extra={"path": str(path), "exists": path.exists()},
            )
            loaded = Config.parse_file(path)
            config.templates.update(loaded.templates)
            config.keyvalues.update(loaded.keyvalues)

        return config


def configure_logging(path: str, level: str) -> None:
    """
    If given a path to a potential logfile, ensure the containing directory exists.
    """
    logging_level = logging._nameToLevel[level.upper()]
    if path == "-":
        jsonlog.basicConfig(level=logging_level, stream=sys.stderr)
    else:
        pathlib.Path(path).parent.mkdir(exist_ok=True)
        jsonlog.basicConfig(level=logging_level, filename=path)
