"""Attributes from `extra=` are included in the JSON object."""

import jsonlog
import logging

jsonlog.basicConfig()
logging.warning("User clicked a button", extra={"user": 123})
