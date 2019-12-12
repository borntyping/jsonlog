import dataclasses
import json

import typing


@dataclasses.dataclass()
class BufferedJSONStream:
    """Collect lines until the buffer can be parsed as a JSON document."""

    stream: typing.TextIO
    buffer: str = ""

    def __iter__(self):
        self.reset_buffer()
        for line in self.stream:
            self.buffer += line
            if self.buffer_is_complete():
                yield self.buffer
                self.reset_buffer()

        if self.buffer:
            yield self.buffer

    def reset_buffer(self) -> None:
        self.buffer = ""

    def buffer_is_complete(self) -> bool:
        try:
            json.loads(self.buffer)
        except json.JSONDecodeError:
            return False
        else:
            return True
