"""
JSON log formatting for the Python logging library.
"""

__authors__ = ["Sam Clements <sam@borntyping.co.uk>"]
__version__ = "0.1.1"

from logging import FileHandler, StreamHandler, captureWarnings, getLogger, root

from jsonlog.formatter import JSONFormatter
from jsonlog.logging import (
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
    "captureWarnings",
    "basicConfig",
    "critical",
    "debug",
    "error",
    "exception",
    "exception",
    "FileHandler",
    "getLogger",
    "info",
    "JSONFormatter",
    "log",
    "root",
    "StreamHandler",
    "warning",
)
