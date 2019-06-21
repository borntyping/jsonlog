"""
JSON log formatting for the Python logging library.
"""

__authors__ = ["Sam Clements <sam@borntyping.co.uk>"]
__version__ = "0.1.1"

from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    FileHandler,
    INFO,
    NOTSET,
    StreamHandler,
    WARN,
    WARNING,
    captureWarnings,
    getLoggerClass,
    root,
    setLoggerClass,
)

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
from jsonlog.formatter import JSONFormatter
from jsonlog.logger import JSONLogger, getLogger

__all__ = (
    "basicConfig",
    "captureWarnings",
    "critical",
    "CRITICAL",
    "debug",
    "DEBUG",
    "error",
    "ERROR",
    "exception",
    "exception",
    "fatal",
    "FATAL",
    "FileHandler",
    "getLogger",
    "getLoggerClass",
    "info",
    "INFO",
    "JSONFormatter",
    "JSONLogger",
    "log",
    "NOTSET",
    "root",
    "setLoggerClass",
    "StreamHandler",
    "WARN",
    "warning",
    "WARNING",
)
