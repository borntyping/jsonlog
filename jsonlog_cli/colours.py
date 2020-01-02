from __future__ import annotations

import dataclasses
import typing

import click

from jsonlog_cli.record import RecordJSONValue


@dataclasses.dataclass()
class Colour:
    fg: typing.Optional[str] = None

    def __bool__(self) -> bool:
        return bool(self.fg)

    def style(self, text: str) -> str:
        return click.style(text, fg=self.fg) if self else text


@dataclasses.dataclass()
class ColourMap:
    mapping: typing.Mapping[RecordJSONValue, Colour]

    def __init__(
        self, mapping: typing.Optional[typing.Mapping[RecordJSONValue, Colour]] = None
    ):
        mapping = mapping if mapping is not None else {}
        self.mapping = {self.normalise(k): v for k, v in mapping.items()}

    def get(self, item: RecordJSONValue) -> Colour:
        return self.mapping.get(self.normalise(item), Colour())

    @staticmethod
    def normalise(value: RecordJSONValue) -> RecordJSONValue:
        return value.casefold() if isinstance(value, str) else value
