import collections
import typing

import click
import pydantic

from jsonlog_cli.types import Value

K = typing.TypeVar("K")
V = typing.TypeVar("V")


class Alias(pydantic.BaseModel, typing.Generic[K]):
    name: K


class AliasedDict(collections.UserDict, typing.Mapping[K, V]):
    def __getitem__(self, item: K) -> V:
        value = super().__getitem__(item)

        if isinstance(value, Alias):
            return self._get_alias(item, value)

        return value

    def _get_alias(self, original: K, alias: Alias[K]) -> V:
        value = self.__getitem__(alias.name)

        if isinstance(value, Alias):
            raise Exception(f"Aliased key {original!r} points to alias {value!r}")

        return value


class Colour(pydantic.BaseModel):
    fg: typing.Optional[str] = None
    bold: typing.Optional[bool] = None

    def __bool__(self) -> bool:
        return bool(self.fg)

    def style(self, text: str) -> str:
        return click.style(text, fg=self.fg, bold=self.bold) if self else text


ColorMapDefinition = typing.Mapping[Value, typing.Union[Alias, Colour]]


class ColourMap(pydantic.BaseModel):
    mapping: typing.Mapping[Value, Colour]

    def __init__(self, mapping: ColorMapDefinition) -> None:
        super().__init__(
            mapping=AliasedDict({self.normalise(k): v for k, v in mapping.items()})
        )

    @classmethod
    def empty(cls) -> "ColourMap":
        return cls({})

    @classmethod
    def default(cls) -> "ColourMap":
        return cls(
            {
                "info": Colour(fg="cyan"),
                "warning": Colour(fg="yellow"),
                "warn": Alias(name="warning"),
                "error": Colour(fg="red"),
                "critical": Colour(fg="red", bold=True),
                "fatal": Alias(name="critical"),
            }
        )

    def get(self, item: Value) -> Colour:
        return self.mapping.get(self.normalise(item), Colour())

    @staticmethod
    def normalise(value: Value) -> Value:
        return value.casefold() if isinstance(value, str) else value
