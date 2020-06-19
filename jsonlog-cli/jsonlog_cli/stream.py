import json
import logging
import sys
import textwrap
import typing

import click

import jsonlog_cli.pattern
import jsonlog_cli.record
import jsonlog_cli.text

try:
    from typing import Protocol  # Only available since python 3.8.
except ImportError:
    from typing_extensions import Protocol  # type: ignore

log = logging.getLogger(__name__)

RecordData = typing.Optional[jsonlog_cli.record.RecordDict]
RecordPair = typing.Tuple[str, RecordData]


class TextStream(Protocol):
    def __iter__(self) -> typing.Iterator[str]:
        ...


class JSONStream:
    stream: TextStream

    def __init__(self, stream: TextStream):
        self.stream = stream

    def consume(self) -> typing.Iterator[RecordPair]:
        for line in self.stream:
            yield self.loads(line)

    @staticmethod
    def loads(string: str) -> RecordPair:
        try:
            data = json.loads(string, object_hook=jsonlog_cli.record.RecordDict)
        except json.JSONDecodeError:
            log.exception(
                "Could not parse JSON",
                extra={"excerpt": textwrap.shorten(string, 100)},
            )
            return string, None
        else:
            return string, data


class BufferedJSONStream(JSONStream):
    """Collect lines until the buffer can be parsed as a JSON document."""

    buffer: str = ""

    def __init__(self, stream: TextStream) -> None:
        super().__init__(stream=stream)
        self.buffer = ""

    def consume(self) -> typing.Iterator[RecordPair]:
        self.reset_buffer()
        for line in self.stream:
            # Yield any remaining lines in the buffer if the current
            # line parses as JSON or starts with a '{' character.
            if self.is_valid_json(line):
                yield from self.reset_buffer()

                # This is a small optimisation to avoid checking if the line
                # contains JSON a second time when we add it to the empty buffer.
                yield self.loads(line)
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

    def reset_buffer(self) -> typing.Iterator[RecordPair]:
        if self.buffer:
            yield self.loads(self.buffer)
        self.buffer = ""

    @staticmethod
    def is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
        except json.JSONDecodeError:
            return False
        else:
            return True


class StreamHandler:
    """
    Track the state of lines surrounding text we want to separate.

    Used when we print lines that didn't parse as JSON.
    """

    pattern: jsonlog_cli.pattern.Pattern
    color: bool
    error: bool

    def __init__(
        self, pattern: jsonlog_cli.pattern.Pattern, color: bool = True
    ) -> None:
        self.pattern = pattern
        self.color = color
        self.error = False

    def __enter__(self) -> "StreamHandler":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.toggle_normal_state()

    @property
    def json_stream_class(self) -> typing.Type[JSONStream]:
        return BufferedJSONStream if self.pattern.is_multiline_json() else JSONStream

    def consume(self, streams: typing.Sequence[TextStream] = ()) -> None:
        text_streams = streams or (sys.stdin,)
        json_streams = [self.json_stream_class(stream=s) for s in text_streams]

        for stream in json_streams:
            self.consume_stream(stream)

    def consume_stream(self, stream: JSONStream) -> None:
        for line, data in stream.consume():
            self.echo(line, data)

    def toggle_normal_state(self) -> None:
        if self.error:
            self.error = False
            click.echo()

    def toggle_error_state(self) -> None:
        if not self.error:
            self.error = True
            click.echo()

    def echo(
        self, line: str, data: typing.Optional[jsonlog_cli.record.RecordDict]
    ) -> None:
        if data is None:
            self.toggle_error_state()
            self.echo_err(line)
        else:
            self.toggle_normal_state()
            self.echo_out(line, data)

    def echo_err(self, line: str) -> None:
        output = jsonlog_cli.text.wrap_and_style_lines(line, fg="red", dim=True)
        click.echo(output, color=self.color, err=True)

    def echo_out(self, line: str, data: jsonlog_cli.record.RecordDict) -> None:
        record = jsonlog_cli.record.Record(line=line.strip(), data=data)
        output = self.pattern.format_record(record)
        click.echo(output, color=self.color, err=False)
