import dataclasses
import json

import typing


@dataclasses.dataclass()
class BufferedJSONStream:
    """Collect lines until the buffer can be parsed as a JSON document."""

    stream: typing.Iterable[str]
    buffer: str = ""

    def __iter__(self):
        self.reset_buffer()
        for line in self.stream:
            # Yield any remaining lines in the buffer if the current
            # line parses as JSON or starts with a '{' character.
            if self.is_valid_json(line):
                yield from self.reset_buffer()

                # This is a small optimisation to avoid checking if the line
                # contains JSON a second time when we add it to the empty buffer.
                yield line
                continue

            # This stops us from buffering forever if we start in the middle
            # of a JSON message, since we'd just keep adding new lines.
            if line.startswith("{"):
                yield from self.reset_buffer()

            # Add the line to the buffer, then yield lines if the buffer
            # now contains JSON. This should yield in most cases.
            self.buffer += line
            if self.is_valid_json(self.buffer):
                yield from self.reset_buffer()

        # Yield any remaining lines in the buffer.
        yield from self.reset_buffer()

    def reset_buffer(self) -> typing.Iterator[str]:
        if self.buffer:
            yield self.buffer
        self.buffer = ""

    @staticmethod
    def is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
        except json.JSONDecodeError:
            return False
        else:
            return True
