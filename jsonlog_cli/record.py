from __future__ import annotations

import dataclasses
import json
import textwrap
import typing

import click
import jsonlog

import jsonlog_cli.text
import jsonlog_cli.pattern

log = jsonlog.getLogger(__name__)

RecordJSONValue = typing.Union[
    None, str, int, float, bool, typing.Sequence, typing.Mapping
]


class RecordDict(dict, typing.Mapping[str, RecordJSONValue]):
    """A mapping that allows access to values as if they were attributes."""

    def __getattr__(self, item) -> typing.Any:
        return self[item]


@dataclasses.dataclass()
class Record:
    message: str
    json: RecordDict

    def __post_init__(self) -> None:
        self.json["__message__"] = self.message
        self.json["__json__"] = self.json

    @classmethod
    def from_string(cls, message: str):
        message = message.strip()
        try:
            data = json.loads(message, object_hook=RecordDict)
        except json.JSONDecodeError as error:
            excerpt = textwrap.shorten(message, 100)
            log.exception(f"Could not parse JSON from line {excerpt!r}")
            raise error
        return cls(message=message, json=data)

    def extract(self, key: typing.Optional[str]) -> RecordJSONValue:
        if key is None:
            return None

        result = self.json
        for k in key.split("."):
            try:
                result = result[k]
            except KeyError:
                return None
        return result

    # def color(self, message: str, level_key: typing.Optional[str]) -> str:
    #     """Extract a level and use it to color the record if possible."""
    #     level_value = self.extract(level_key)
    #
    #     if not isinstance(level_value, str):
    #         return message
    #
    #     return jsonlog_cli.colors.color(level_value, message)

    def blocks(self, multiline_keys: typing.Sequence[str]) -> typing.Iterator[str]:
        for key in multiline_keys:
            value = self.extract(key)
            if value:
                string = self.value_to_string(value)
                yield jsonlog_cli.text.format_multiline(string, dim=True)

    @staticmethod
    def value_to_string(value: RecordJSONValue) -> str:
        """
        Transform a JSON value into something we can display in a multiline block.

        Strings are left alone (as we don't want to add quotes) and any other values are
        dumped as indented JSON.
        """
        if isinstance(value, str):
            return value

        return json.dumps(value, indent=2)


@dataclasses.dataclass()
class RecordState:
    """
    Track the state of lines surrounding text we want to separate.

    Used when we print lines that didn't parse as JSON.
    """

    error: bool = False
    record_class: typing.Type[Record] = Record

    def __enter__(self) -> RecordState:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.toggle_normal_state()

    def toggle_normal_state(self) -> None:
        if self.error:
            self.error = False
            click.echo()

    def toggle_error_state(self) -> None:
        if not self.error:
            self.error = True
            click.echo()

    def echo(self, line: str, formatter: jsonlog_cli.pattern.Pattern, color=None):
        try:
            record = Record.from_string(line)
        except json.JSONDecodeError:
            self.toggle_error_state()
            output = jsonlog_cli.text.format_multiline(line, fg="red", dim=True)
        else:
            self.toggle_normal_state()
            output = formatter.format_message(record)
        click.echo(output, color=color)
