import textwrap
import typing

import click


def wrap_lines(lines: str, width: int) -> typing.Iterable[str]:
    """Split text into lines and wrap them to a specified width."""
    for line in lines.splitlines():
        if len(line) < width:
            yield line
        else:
            yield from textwrap.wrap(line, width=width)


def multiline(string: str, indent: int = 4, **style: typing.Any) -> str:
    """Format a block of text with styling, indentation and wrapping."""
    width, _ = click.get_terminal_size()
    width = width - (2 * indent)
    start = " " * indent
    lines = wrap_lines(string, width)
    lines = (click.style(l, **style) for l in lines)
    lines = (start + l for l in lines)
    return "\n".join(lines)
