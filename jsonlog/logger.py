import logging
import collections.abc

import typing


class JSONLogger(logging.Logger):
    def _build_args(
        self, original_args: typing.Any, keyword_args: typing.Mapping
    ) -> typing.Sequence:
        """
        If additional keyword arguments are passed, they are collected into a mapping
        and used instead of the 'args' argument. You can't use both at once though.
        """
        if isinstance(original_args, collections.abc.Mapping):
            return [{**original_args, **keyword_args}]

        if original_args and keyword_args:
            raise ValueError("Can't merge keyword arguments as 'args' is not a mapping")

        if keyword_args:
            return [keyword_args]

        return original_args

    def _log(
        self,
        level: int,
        msg: str,
        args: typing.Optional[typing.Any],
        exc_info: typing.Any = None,
        extra: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        stack_info: typing.Any = False,
        **kwargs: typing.Any
    ) -> None:
        return super()._log(  # type: ignore
            level,
            msg,
            args=self._build_args(args, kwargs),
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
        )


def getLogger(name: str) -> JSONLogger:
    """
    A typed alias for logging.getLogger.

    It will ensure that JSONLogger has been set as the logger class first.
    """
    logging.setLoggerClass(JSONLogger)
    return typing.cast(JSONLogger, logging.getLogger(name))
