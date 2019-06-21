"""Tracebacks will be included in the output JSON."""

import jsonlog

jsonlog.warning("Started script")

try:
    raise ValueError("Example exception")
except ValueError:
    jsonlog.exception("Encountered an error")
