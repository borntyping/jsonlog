import logging

import typing


class JSONLogger(logging.Logger):
    def _log(
        self,
        level: int,
        msg: str,
        args: typing.Any,
        exc_info: typing.Any = None,
        extra: typing.Optional[typing.Mapping] = None,
        stack_info: typing.Any = False,
        **kwargs: typing.Any
    ) -> None:
        """Additional keyword arguments are added to the `extra` mapping."""
        extra = extra if extra is not None else {}
        extra = {**extra, **kwargs}
        return super()._log(  # type: ignore
            level, msg, args=args, exc_info=exc_info, extra=extra, stack_info=stack_info
        )


def getLogger(name: str) -> JSONLogger:
    """
    A typed alias for logging.getLogger.

    It will ensure that JSONLogger has been set as the logger class first.
    """
    logging.setLoggerClass(JSONLogger)
    return typing.cast(JSONLogger, logging.getLogger(name))
