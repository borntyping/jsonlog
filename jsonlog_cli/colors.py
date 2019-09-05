import click
import typing


def info(message: str) -> str:
    return click.style(message, fg="cyan")


def warning(message: str) -> str:
    return click.style(message, fg="yellow")


def error(message: str) -> str:
    return click.style(message, fg="red")


def critical(message: str) -> str:
    return click.style(message, fg="red", bold=True)


COLORS: typing.Mapping[str, typing.Callable[[str], str]] = {
    "INFO".casefold(): info,
    "WARNING".casefold(): warning,
    "ERROR".casefold(): error,
    "CRITICAL".casefold(): critical,
}


def color(key: str, message: str) -> str:
    return COLORS.get(key.casefold(), lambda x: x)(message)
