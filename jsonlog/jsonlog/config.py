"""Wrappers for the `logging` module."""

import functools
import logging
import typing
import warnings

import jsonlog.formatter


def basicConfig(
    *,
    level: typing.Union[int, str] = logging.WARNING,
    indent: typing.Optional[int] = jsonlog.formatter.JSONFormatter.DEFAULT_INDENT,
    keys: typing.Sequence[str] = jsonlog.formatter.JSONFormatter.DEFAULT_KEYS,
    timespec: str = jsonlog.formatter.JSONFormatter.DEFAULT_TIMESPEC,
    filename: typing.Optional[str] = None,
    filemode: str = "a",
    stream: typing.Optional[typing.Any] = None,
) -> None:
    """
    Works like logging.basicConfig but configures a JSON formatter.

    This does not recreate the exact same API as the original `basicConfig` method,
    which has a very verbose implementation. `logging.Formatter` specific arguments like
    `fmt` and `datefmt` are removed, and there is not support for providing your own
    handlers (use the `logging.config` module instead if you need to do this).
    """
    if logging.root.handlers:
        # The original basicConfig silently does nothing when handlers are configured.
        warnings.warn("Logging handlers are already configured")

    if stream and filename:
        raise ValueError("'stream' and 'filename' should not be specified together")

    handler: logging.Handler
    if filename is not None:
        handler = logging.FileHandler(filename=filename, mode=filemode)
    else:
        handler = logging.StreamHandler(stream)

    formatter = jsonlog.formatter.JSONFormatter(
        keys=keys, timespec=timespec, indent=indent
    )

    handler.setFormatter(formatter)  # type: ignore

    try:
        logging._acquireLock()  # type: ignore
        logging.root.addHandler(handler)
        logging.root.setLevel(level)
    finally:
        logging._releaseLock()  # type: ignore


def ensure_handlers(func):
    """Ensure logging handlers exist before calling a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if len(logging.root.handlers) == 0:
            basicConfig()
        return func(*args, **kwargs)

    return wrapper


debug = ensure_handlers(logging.root.debug)
info = ensure_handlers(logging.root.info)
warning = ensure_handlers(logging.root.warning)
error = ensure_handlers(logging.root.error)
critical = ensure_handlers(logging.root.critical)
fatal = ensure_handlers(logging.root.fatal)  # type: ignore
log = ensure_handlers(logging.root.log)
exception = ensure_handlers(logging.root.exception)
