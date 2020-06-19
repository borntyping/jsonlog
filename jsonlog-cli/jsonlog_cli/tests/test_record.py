import pydantic
import pytest

from jsonlog_cli.pattern import Pattern, TemplatePattern
from jsonlog_cli.record import Record
from jsonlog_cli.stream import JSONStream


class Example(pydantic.BaseModel):
    line: str
    expected: str
    pattern: Pattern

    def record(self):
        line, data = JSONStream.loads(self.line)
        return Record(line=line, data=data)


@pytest.mark.parametrize(
    "example",
    [
        Example(
            line='{"timestamp": "2019-06-26", "message": "Hello World 1"}',
            expected="2019-06-26 Hello World 1",
            pattern=TemplatePattern(format="{timestamp} {message}"),
        ),
        Example(
            line='{"@timestamp": "2019-06-26", "@message": "Hello World 2"}',
            expected="2019-06-26 Hello World 2",
            pattern=TemplatePattern(format="{@timestamp} {@message}"),
        ),
        # Test message coloring.
        Example(
            line='{"message": "Hello World 3", "level": "CRITICAL"}',
            expected="\x1b[31m\x1b[1mCRITICAL Hello World 3\x1b[0m",
            pattern=TemplatePattern(format="{level} {message}"),
        ),
        # Test nested keys can be used in both the format string and config keys.
        Example(
            line='{"nested": {"message": "Hello World 4", "multiline": "Lorem Ipsum", "level": "CRITICAL"}}',
            expected="\x1b[31m\x1b[1mHello World 4\x1b[0m\n\n    \x1b[2mLorem Ipsum\x1b[0m\n",
            pattern=TemplatePattern(
                format="{nested.message}",
                level_key="nested.level",
                multiline_keys=["nested.multiline"],
            ),
        ),
        # Test nested data renders nicely.
        Example(
            line='{"nested": {"a": 1, "b": "Z", "c": []}}',
            expected='static\n\n    \x1b[2m{\x1b[0m\n    \x1b[2m  "a": 1,\x1b[0m\n    \x1b[2m  "b": "Z",\x1b[0m\n    \x1b[2m  "c": []\x1b[0m\n    \x1b[2m}\x1b[0m\n',
            pattern=TemplatePattern(format="static", multiline_keys=["nested"]),
        ),
    ],
)
def test_examples(example: Example):
    actual = example.pattern.format_record(example.record())
    assert actual == example.expected, repr(actual)
