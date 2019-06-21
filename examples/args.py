"""Attributes from a mapping passed as a lone positional argument are included."""

import jsonlog
import logging

jsonlog.basicConfig()
logging.warning("User clicked a button", {"user": 123})
