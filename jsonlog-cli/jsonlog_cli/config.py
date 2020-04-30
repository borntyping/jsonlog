from __future__ import annotations

import dataclasses
import json
import logging
import pathlib
import typing

import jsonschema
import xdg

from .colours import Colour, ColourMap
from .pattern import KeyValuePattern, Pattern, TemplatePattern
from .key import Key

log = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = xdg.XDG_CONFIG_HOME / "jsonlog" / "config.json"
DEFAULT_LOG_PATH = xdg.XDG_CACHE_HOME / "jsonlog" / "internal.log"
DEFAULT_CONFIG = {
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
    "highlight": TemplatePattern(template="{__message__}"),
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
    patterns: typing.Dict[str, Pattern]
    pattern_classes: typing.Dict[str, typing.Type[Pattern]]

    @classmethod
    def configure(cls, path: typing.Optional[str]) -> Config:
        config = Config(
            patterns=DEFAULT_CONFIG,
            pattern_classes={
                "TemplatePattern": TemplatePattern,
                "KeyValuePattern": KeyValuePattern,
            },
        )

        if path is not None:
            log.info(f"Reading configuration from file = {path!r}")
            config.load(pathlib.Path(path))
        elif DEFAULT_CONFIG_PATH.exists():
            log.info(f"Reading configuration from default file = {DEFAULT_CONFIG_PATH}")
            config.load(DEFAULT_CONFIG_PATH)

        return config

    def load(self, path: pathlib.Path) -> None:
        instance = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        jsonschema.validate(instance=instance, schema=CONFIG_SCHEMA)
        for k, v in instance.get("patterns", {}).items():
            cls_name = v.pop("class", "key_value")
            cls = self.pattern_classes[cls_name]
            self.patterns[k] = cls(**v)


def ensure_log_path(path: str) -> typing.Optional[str]:
    """
    If given a path to a potential logfile, ensure the containing directory exists.
    """
    if path == "-":
        return None

    pathlib.Path(path).parent.mkdir(exist_ok=True)
    return path
