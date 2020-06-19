import typing

import click
import pydantic


class Colour(pydantic.BaseModel):
    fg: typing.Optional[str] = None
    bold: typing.Optional[bool] = None

    def __bool__(self) -> bool:
        return bool(self.fg)

    def style(self, text: str) -> str:
        return click.style(text, fg=self.fg, bold=self.bold) if self else text
