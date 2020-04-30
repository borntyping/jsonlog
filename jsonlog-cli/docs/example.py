import logging
import sys

import jsonlog

jsonlog.basicConfig(level=jsonlog.DEBUG, stream=sys.stdout)

log = logging.getLogger("example")
log.debug("debug level log message")
log.info("info level log message")
log.warning("warning level log message")
log.error("error level log message")

try:
    1 / 0
except ZeroDivisionError:
    log.exception("error level log message with traceback")


log.critical("critical level log message")
