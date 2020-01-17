from __future__ import annotations

import dataclasses
import typing

import click

from jsonlog_cli.record import RecordJSONValue


@dataclasses.dataclass()
class Alias:
    name: str


@dataclasses.dataclass()
class Colour:
    fg: typing.Optional[str] = None
    bold: typing.Optional[bool] = None

    def __bool__(self) -> bool:
        return bool(self.fg)

    def style(self, text: str) -> str:
        return click.style(text, fg=self.fg, bold=self.bold) if self else text


ColorMapKey = RecordJSONValue
ColorMapValue = typing.Union[Alias, Colour]


@dataclasses.dataclass(frozen=True)
class ColourMap:
    mapping: typing.Mapping[ColorMapKey, ColorMapValue]

    @classmethod
    def empty(cls):
        return cls({})

    @classmethod
    def from_map(cls, mapping: typing.Mapping[ColorMapKey, Colour]):
        return cls({cls.normalise(k): v for k, v in mapping.items()})

    def _get_item(self, item: ColorMapKey) -> ColorMapValue:
        return self.mapping.get(self.normalise(item), Colour())

    def _get_alias(self, alias: ColorMapKey, item: ColorMapKey) -> ColorMapValue:
        key = self.normalise(item)
        value = self.mapping.get(key, Colour())

        if isinstance(value, Alias):
            raise Exception(
                f"Key {alias!r} points to alias {item!r} with value {value!r}"
            )

        return value

    def get(self, item: ColorMapKey) -> Colour:
        value = self._get_item(item)

        if isinstance(value, Alias):
            return self._get_alias(item, value.name)

        return value

    @staticmethod
    def normalise(value: ColorMapKey) -> ColorMapKey:
        return value.casefold() if isinstance(value, str) else value
