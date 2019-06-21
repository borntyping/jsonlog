import dataclasses

import _pytest.capture
import typing


@dataclasses.dataclass()
class Capture:
    capsys: _pytest.capture.CaptureResult
    output: typing.Optional[str] = dataclasses.field(init=False, default=None)

    def __repr__(self) -> str:
        return f"Capture[{self.stderr.strip()!r}]"  # pragma: no cover

    @property
    def stderr(self) -> str:
        if self.output is None:
            self.output = self.capsys.readouterr().err
        return self.output

    def __contains__(self, item: str) -> bool:
        return item in self.stderr
