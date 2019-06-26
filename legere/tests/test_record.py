import dataclasses
import typing

import pytest

from legere.record import Record


@dataclasses.dataclass()
class Example:
    record: Record
    expected: str
    format_string: str
    level_key: typing.Optional[str] = None
    multiline_keys: typing.Sequence[str] = ()


@pytest.mark.parametrize(
    "example",
    [
        Example(
            Record({"timestamp": "2019-06-26", "message": "Hello World"}),
            expected="2019-06-26 Hello World\x1b[0m",
            format_string="{timestamp} {message}",
        ),
        Example(
            Record({"@timestamp": "2019-06-26", "@message": "Hello World"}),
            expected="2019-06-26 Hello World\x1b[0m",
            format_string="{@timestamp} {@message}",
        ),
        Example(
            Record({"level": "CRITICAL", "message": "Hello World"}),
            expected="\x1b[31m\x1b[1mCRITICAL Hello World\x1b[0m",
            format_string="{level} {message}",
            level_key="level",
        ),
    ],
)
def test_examples(example: Example):
    assert example.expected == example.record.format(
        format_string=example.format_string,
        level_key=example.level_key,
        multiline_keys=example.multiline_keys,
    )
