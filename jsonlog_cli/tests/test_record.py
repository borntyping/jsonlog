import dataclasses
import typing

import pytest

from jsonlog_cli.record import Record


@dataclasses.dataclass()
class Example:
    line: str
    expected: str
    format_string: str
    level_key: typing.Optional[str] = None
    multiline_keys: typing.Sequence[str] = ()

    def record(self):
        return Record.from_string(self.line)


@pytest.mark.parametrize(
    "example",
    [
        Example(
            line='{"timestamp": "2019-06-26", "message": "Hello World"}',
            expected="2019-06-26 Hello World",
            format_string="{timestamp} {message}",
        ),
        Example(
            line='{"@timestamp": "2019-06-26", "@message": "Hello World"}',
            expected="2019-06-26 Hello World",
            format_string="{@timestamp} {@message}",
        ),
        # Test message coloring.
        Example(
            line='{"message": "Hello World", "level": "CRITICAL"}',
            expected="\x1b[31m\x1b[1mCRITICAL Hello World\x1b[0m",
            format_string="{level} {message}",
            level_key="level",
        ),
        # Test nested keys can be used in both the format string and config keys.
        Example(
            line='{"nested": {"message": "Hello World", "multiline": "Lorem Ipsum", "level": "CRITICAL"}}',
            expected="\x1b[31m\x1b[1mHello World\x1b[0m\n\n    \x1b[2mLorem Ipsum\x1b[0m\n",
            format_string="{nested.message}",
            level_key="nested.level",
            multiline_keys=["nested.multiline"],
        ),
        # Test nested data renders nicely.
        Example(
            line='{"nested": {"a": 1, "b": "Z", "c": []}}',
            expected='static\n\n    \x1b[2m{\x1b[0m\n    \x1b[2m  "a": 1,\x1b[0m\n    \x1b[2m  "b": "Z",\x1b[0m\n    \x1b[2m  "c": []\x1b[0m\n    \x1b[2m}\x1b[0m\n',
            format_string="static",
            multiline_keys=["nested"],
        ),
    ],
)
def test_examples(example: Example):
    actual = example.record().format(
        format_string=example.format_string,
        level_key=example.level_key,
        multiline_keys=example.multiline_keys,
    )
    assert actual == example.expected, repr(actual)
