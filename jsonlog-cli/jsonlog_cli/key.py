from __future__ import annotations

import dataclasses
import typing

from jsonlog_cli.colours import Colour
from jsonlog_cli.record import RecordValue


@dataclasses.dataclass(frozen=True)
class Key:
    name: str
    template: typing.Optional[str] = dataclasses.field(compare=False, default=None)

    @classmethod
    def from_strings(cls, strings: typing.Sequence[str]) -> typing.Sequence[Key]:
        return [cls.from_string(k) for k in strings]

    @classmethod
    def from_string(cls, string: str) -> Key:
        return Key(*string.split("=", 1))

    def format_key(self) -> str:
        return f"{self.name}="

    def format_value(self, value: RecordValue) -> str:
        if self.template is not None:
            return self.template.format(value)

        return repr(value)

    def format_pair(self, value: RecordValue, colour: Colour) -> str:
        k = self.format_key()
        v = self.format_value(value)

        if colour:
            k = Colour(fg="white").style(k)
            v = colour.style(v)

        return f"{k}{v}"
