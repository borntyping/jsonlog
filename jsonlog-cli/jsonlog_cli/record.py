from __future__ import annotations

import dataclasses
import json
import textwrap
import typing

import jsonlog

log = jsonlog.getLogger(__name__)

RecordKey = str
RecordValue = typing.Union[None, str, int, float, bool, typing.Sequence, typing.Mapping]


class RecordDict(dict, typing.Mapping[str, RecordValue]):
    """A mapping that allows access to values as if they were attributes."""

    def __getattr__(self, item) -> typing.Any:
        return self[item]


@dataclasses.dataclass()
class Record:
    message: str
    json: RecordDict

    def __post_init__(self) -> None:
        self.json["__json__"] = dict(self.json)
        self.json["__message__"] = self.message

    @classmethod
    def from_string(cls, message: str):
        message = message.strip()
        try:
            data = json.loads(message, object_hook=RecordDict)
        except json.JSONDecodeError as error:
            excerpt = textwrap.shorten(message, 100)
            log.exception(f"Could not parse JSON from line {excerpt!r}")
            raise error
        return cls(message=message, json=data)

    def keys(self) -> typing.Iterable[str]:
        return [k for k in self.json.keys() if k not in {"__json__", "__message__"}]

    def extract(self, key: typing.Optional[str]) -> RecordValue:
        if key is None:
            return None

        if key in self.json:
            return self.json[key]

        return self._extract(key)

    def _extract(self, key: str) -> RecordValue:
        result = self.json

        for k in key.split("."):
            try:
                result = result[k]
            except KeyError:
                return None
        return result
