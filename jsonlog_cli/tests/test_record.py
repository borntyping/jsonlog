import dataclasses

import pytest

from jsonlog_cli.record import Record
from jsonlog_cli.pattern import Pattern, TemplatePattern


@dataclasses.dataclass()
class Example:
    line: str
    expected: str
    pattern: Pattern

    def record(self):
        return Record.from_string(self.line)


@pytest.mark.parametrize(
    "example",
    [
        Example(
            line='{"timestamp": "2019-06-26", "message": "Hello World"}',
            expected="2019-06-26 Hello World\x1b[0m",
            pattern=TemplatePattern(template="{timestamp} {message}"),
        ),
        Example(
            line='{"@timestamp": "2019-06-26", "@message": "Hello World"}',
            expected="2019-06-26 Hello World\x1b[0m",
            pattern=TemplatePattern(template="{@timestamp} {@message}"),
        ),
        # Test message coloring.
        Example(
            line='{"message": "Hello World", "level": "CRITICAL"}',
            expected="\x1b[31mCRITICAL Hello World\x1b[0m",
            pattern=TemplatePattern(template="{level} {message}", level_key="level"),
        ),
        # Test nested keys can be used in both the format string and config keys.
        Example(
            line='{"nested": {"message": "Hello World", "multiline": "Lorem Ipsum", "level": "CRITICAL"}}',
            expected="\x1b[31mHello World\x1b[0m\n\n    \x1b[2mLorem Ipsum\x1b[0m\n",
            pattern=TemplatePattern(
                template="{nested.message}",
                level_key="nested.level",
                multiline_keys=["nested.multiline"],
            ),
        ),
        # Test nested data renders nicely.
        Example(
            line='{"nested": {"a": 1, "b": "Z", "c": []}}',
            expected='static\x1b[0m\n\n    \x1b[2m{\x1b[0m\n    \x1b[2m  "a": 1,\x1b[0m\n    \x1b[2m  "b": "Z",\x1b[0m\n    \x1b[2m  "c": []\x1b[0m\n    \x1b[2m}\x1b[0m\n',
            pattern=TemplatePattern(template="static", multiline_keys=["nested"]),
        ),
    ],
)
def test_examples(example: Example):
    actual = example.pattern.format_record(example.record())
    assert actual == example.expected, repr(actual)
