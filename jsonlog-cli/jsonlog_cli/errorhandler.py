from __future__ import annotations

import dataclasses
import json
import typing

import click

import jsonlog_cli.pattern
import jsonlog_cli.text
from jsonlog_cli.record import Record


@dataclasses.dataclass()
class ErrorHandler:
    """
    Track the state of lines surrounding text we want to separate.

    Used when we print lines that didn't parse as JSON.
    """

    error: bool = False
    record_class: typing.Type[Record] = Record

    def __enter__(self) -> ErrorHandler:
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

    def echo(self, line: str, pattern: jsonlog_cli.pattern.Pattern, color=None):
        try:
            record = Record.from_string(line)
        except json.JSONDecodeError:
            self.toggle_error_state()
            output = jsonlog_cli.text.wrap_and_style_lines(line, fg="red", dim=True)
        else:
            self.toggle_normal_state()
            output = pattern.format_record(record)
        click.echo(output, color=color)
