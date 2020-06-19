import json
import logging
import pathlib
import sys
import typing

import jsonschema
import pydantic

import jsonlog
from .colours import Colour, ColourMap
from .pattern import KeyValuePattern, TemplatePattern

log = logging.getLogger(__name__)

DEFAULT_KEYVALUES = {
    "default": KeyValuePattern(multiline_keys=("traceback", "stacktrace")),
    "elasticsearch": KeyValuePattern(
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
    "jsonlog": KeyValuePattern(
        priority_keys=("timestamp", "level", "name", "message"),
        multiline_keys=("traceback",),
    ),
    "snyk": KeyValuePattern(
        priority_keys=("time", "msg", "reason.response.body.message"),
        multiline_keys=("__json__",),
        colours=ColourMap({20: Colour(fg="cyan"), 50: Colour(fg="red")}),
    ),
    "jaeger": KeyValuePattern(multiline_keys=("errorVerbose", "stacktrace")),
    "vault": KeyValuePattern(
        level_key="@level", priority_keys=("@timestamp", "@module", "@message"),
    ),
}
DEFAULT_TEMPLATES = {
    "default": TemplatePattern(format="{__line__}"),
}
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "patterns": {
            "type": "object",
            "additionalProperties": {"$ref": "#/definitions/pattern"},
        }
    },
    "definitions": {
        "pattern": {
            "$id": "#pattern",
            "type": "object",
            "properties": {
                "template": {"type": "string"},
                "level_key": {"type": "string"},
                "priority_keys": {"type": "array", "items": {"type": "string"}},
                "multiline_keys": {"type": "array", "items": {"type": "string"}},
                "multiline_json": {"type": "boolean"},
            },
        }
    },
}


class Config(pydantic.BaseModel):
    keyvalues: typing.Dict[str, KeyValuePattern]
    templates: typing.Dict[str, TemplatePattern]

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
            config.read(path)

        return config

    def read(self, path: pathlib.Path) -> None:
        log.info(
            "Reading configuration from file",
            extra={"path": str(path), "exists": path.exists()},
        )
        instance = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=instance, schema=CONFIG_SCHEMA)

        for k, v in instance.get("keyvalues", {}).items():
            self.keyvalues[k] = KeyValuePattern(**v)

        for k, v in instance.get("templates", {}).items():
            self.templates[k] = TemplatePattern(**v)


def configure_logging(path: str) -> None:
    """
    If given a path to a potential logfile, ensure the containing directory exists.
    """
    if path == "-":
        jsonlog.basicConfig(level=logging.INFO, stream=sys.stderr)
    else:
        pathlib.Path(path).parent.mkdir(exist_ok=True)
        jsonlog.basicConfig(level=logging.INFO, filename=path)
