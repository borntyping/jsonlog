import jsonlog

jsonlog.basicConfig()

log = jsonlog.getLogger(__name__)
log.warning("User clicked a button", user=123)
