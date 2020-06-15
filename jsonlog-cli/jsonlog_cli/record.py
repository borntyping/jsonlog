from __future__ import annotations

import dataclasses
import typing

import jsonlog
from .key import Key

log = jsonlog.getLogger(__name__)

RecordKey = str
RecordValue = typing.Union[None, str, int, float, bool, typing.Sequence, typing.Mapping]


class RecordDict(dict, typing.Mapping[str, RecordValue]):
    """A mapping that allows access to values as if they were attributes."""

    def __getattr__(self, item) -> typing.Any:
        return self[item]


@dataclasses.dataclass()
class Record(typing.Mapping[str, typing.Any]):
    line: str
    data: RecordDict

    def ordered_keys(self) -> typing.Iterable[Key]:
        return [Key(k) for k in self.data.keys()]

    def extract(self, key: typing.Optional[str]) -> RecordValue:
        if key is None:
            return None

        if key in self.data:
            return self.data[key]
        return self._extract(key)

    def _extract(self, key: str) -> RecordValue:
        result = self.data

        for k in key.split("."):
            try:
                result = result[k]
            except KeyError:
                return None
        return result

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.data)

    def __getitem__(self, item) -> typing.Any:
        if item == "__json__":
            return self.data

        if item == "__line__":
            return self.line

        return self.data[item]


class RecordFormatter(typing.Protocol):
    def format_record(self, record: Record) -> str:
        ...
