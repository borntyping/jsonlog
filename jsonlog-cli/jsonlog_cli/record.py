import typing

import jsonlog
import jsonlog_cli.types

log = jsonlog.getLogger(__name__)


class RecordDict(dict, typing.Mapping[str, jsonlog_cli.types.Value]):
    """A mapping that allows access to values as if they were attributes."""

    def __getattr__(self, item) -> typing.Any:
        return self[item]


class Record(typing.Mapping[str, typing.Any]):
    line: str
    data: RecordDict

    def __init__(self, line: str, data: RecordDict) -> None:
        self.line = line
        self.data = data

    def ordered_keys(self) -> typing.Iterable[str]:
        return self.data.keys()

    def extract(self, key: typing.Optional[str]) -> jsonlog_cli.types.Value:
        if key is None:
            return None

        if key in self.data:
            return self.data[key]
        return self._extract(key)

    def _extract(self, key: str) -> jsonlog_cli.types.Value:
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
