import dataclasses

import pytest

from jsonlog_cli.key import Key
from jsonlog_cli.pattern import Pattern, TemplatePattern
from jsonlog_cli.record import Record


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
            expected="2019-06-26 Hello World",
            pattern=TemplatePattern(template="{timestamp} {message}"),
        ),
        Example(
            line='{"@timestamp": "2019-06-26", "@message": "Hello World"}',
            expected="2019-06-26 Hello World",
            pattern=TemplatePattern(template="{@timestamp} {@message}"),
        ),
        # Test message coloring.
        Example(
            line='{"message": "Hello World", "level": "CRITICAL"}',
            expected="CRITICAL Hello World",
            pattern=TemplatePattern(
                template="{level} {message}", level_key=Key("level")
            ),
        ),
        # Test nested keys can be used in both the format string and config keys.
        Example(
            line='{"nested": {"message": "Hello World", "multiline": "Lorem Ipsum", "level": "CRITICAL"}}',
            expected="Hello World\n\n    \x1b[2mLorem Ipsum\x1b[0m\n",
            pattern=TemplatePattern(
                template="{nested.message}",
                level_key=Key("nested.level"),
                multiline_keys=(Key("nested.multiline"),),
            ),
        ),
        # Test nested data renders nicely.
        Example(
            line='{"nested": {"a": 1, "b": "Z", "c": []}}',
            expected='static\n\n    \x1b[2m{\x1b[0m\n    \x1b[2m  "a": 1,\x1b[0m\n    \x1b[2m  "b": "Z",\x1b[0m\n    \x1b[2m  "c": []\x1b[0m\n    \x1b[2m}\x1b[0m\n',
            pattern=TemplatePattern(template="static", multiline_keys=(Key("nested"),)),
        ),
    ],
)
def test_examples(example: Example):
    actual = example.pattern.format_record(example.record())
    assert actual == example.expected, repr(actual)
