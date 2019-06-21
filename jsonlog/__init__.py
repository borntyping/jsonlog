"""
JSON log formatting for the Python logging library.
"""

__authors__ = ["Sam Clements <sam@borntyping.co.uk>"]
__version__ = "0.1.1"

from logging import FileHandler, StreamHandler, captureWarnings, getLogger, root

from jsonlog.formatter import JSONFormatter
from jsonlog.config import (
    basicConfig,
    critical,
    debug,
    error,
    exception,
    fatal,
    info,
    log,
    warning,
)

__all__ = (
    "basicConfig",
    "captureWarnings",
    "critical",
    "debug",
    "error",
    "exception",
    "exception",
    "fatal",
    "FileHandler",
    "getLogger",
    "info",
    "JSONFormatter",
    "log",
    "root",
    "StreamHandler",
    "warning",
)
