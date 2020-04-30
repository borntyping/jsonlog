"""
JSON log formatting for the Python logging module.
"""

__authors__ = ["Sam Clements <sam@borntyping.co.uk>"]

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
    getLogger,
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
    "fatal",
    "FATAL",
    "FileHandler",
    "getLogger",
    "getLoggerClass",
    "info",
    "INFO",
    "JSONFormatter",
    "log",
    "NOTSET",
    "root",
    "setLoggerClass",
    "StreamHandler",
    "WARN",
    "warning",
    "WARNING",
)
