from __future__ import annotations

import dataclasses
import json
import logging
import pathlib
import sys
import typing

import jsonlog
import jsonschema

from .colours import Colour, ColourMap
from .key import Key
from .pattern import KeyValuePattern, TemplatePattern

log = logging.getLogger(__name__)

DEFAULT_KEYVALUES = {
    "default": KeyValuePattern(multiline_keys=(Key("traceback"), Key("stacktrace"))),
    "elasticsearch": KeyValuePattern(
        priority_keys=(
            Key("timestamp"),
            Key("level"),
            Key("type"),
            Key("component"),
            Key("cluster.name"),
            Key("node.name"),
            Key("message"),
        ),
        multiline_keys=(Key("stacktrace"),),
        multiline_json=True,
    ),
    "jsonlog": KeyValuePattern(
        priority_keys=(Key("timestamp"), Key("level"), Key("name"), Key("message")),
        multiline_keys=(Key("traceback"),),
    ),
    "snyk": KeyValuePattern(
        priority_keys=(Key("time"), Key("msg"), Key("reason.response.body.message")),
        multiline_keys=(Key("__json__"),),
        colours=ColourMap({20: Colour(fg="cyan"), 50: Colour(fg="red")}),
    ),
    "jaeger": KeyValuePattern(multiline_keys=(Key("errorVerbose"), Key("stacktrace"))),
    "vault": KeyValuePattern(
        level_key=Key("@level"),
        priority_keys=(Key("@timestamp"), Key("@module"), Key("@message")),
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


@dataclasses.dataclass()
class Config:
    keyvalues: typing.Dict[str, KeyValuePattern]
    templates: typing.Dict[str, TemplatePattern]

    @classmethod
    def defaults(cls):
        return Config(
            keyvalues=dict(DEFAULT_KEYVALUES), templates=dict(DEFAULT_TEMPLATES),
        )

    def load(self, path: typing.Union[None, str, pathlib.Path]) -> None:
        log.info(f"Loading configuration from file", extra={"path": repr(path)})
        if path is None:
            log.info("Path is none, not loading anything")
            return

        path: pathlib.Path = pathlib.Path(path) if isinstance(path, str) else path

        log.info(f"Reading configuration from file", extra={"path": repr(path)})
        instance = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
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
        jsonlog.basicConfig(stream=sys.stderr)
    else:
        pathlib.Path(path).parent.mkdir(exist_ok=True)
        jsonlog.basicConfig(filename=path)
