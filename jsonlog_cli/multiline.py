import dataclasses

import typing


@dataclasses.dataclass()
class MultilineStream:
    stream: typing.TextIO

    def __iter__(self):
        for line in self.stream:
            yield line
