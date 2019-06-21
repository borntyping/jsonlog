"""The jsonlog formatter is configured when you call module-level functions."""

import jsonlog

jsonlog.warning("User %(user)s clicked a button", {"user": 123})
