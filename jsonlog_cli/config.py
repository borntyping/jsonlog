from __future__ import annotations

import dataclasses
import json
import logging
import pathlib
import typing

import jsonschema
import xdg

import jsonlog_cli.record

log = logging.getLogger(__name__)

DEFAULT_PATH = xdg.XDG_CONFIG_HOME / "jsonlog" / "config.json"
DEFAULT_CONFIG = {
    "jsonlog": jsonlog_cli.record.Pattern(
        template="{timestamp} {level} {name} {message}",
        level_key="level",
        multiline_keys=("traceback",),
    ),
}
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "patterns": {"type": "object", "additionalProperties": {"$ref": "#/definitions/pattern"}}
    },
    "definitions": {
        "pattern": {
            "$id": "#pattern",
            "type": "object",
            "properties": {
                "template": {"type": "string"},
                "level_key": {"type": "string"},
                "multiline_keys": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["template"],
        }
    },
}


@dataclasses.dataclass()
class Config:
    patterns: typing.Dict[str, jsonlog_cli.record.Pattern] = dataclasses.field(
        default_factory=dict
    )

    @classmethod
    def configure(cls, path: typing.Optional[str]) -> Config:
        config = Config(DEFAULT_CONFIG)

        if path is not None:
            log.info(f"Reading configuration from file = {path!r}")
            config.load(pathlib.Path(path))
        elif DEFAULT_PATH.exists():
            log.info(f"Reading configuration from default file = {DEFAULT_PATH}")
            config.load(DEFAULT_PATH)

        return config

    def load(self, path: pathlib.Path) -> None:
        instance = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        jsonschema.validate(instance=instance, schema=CONFIG_SCHEMA)
        for k, v in instance.get("patterns", {}).items():
            self.patterns[k] = jsonlog_cli.record.Pattern(**v)
