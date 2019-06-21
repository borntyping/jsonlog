jsonlog
=======

A drop-in formatter for Python's `logging` library that outputs messages as line
delimited JSON.

Usage
-----

You can use `jsonlog` as a drop-in replacement for `logging`:

```python
import jsonlog
import logging

jsonlog.basicConfig(level=jsonlog.INFO)
jsonlog.info("Works with functions in the jsonlog module.")
logging.info("And works with functions in the logging module.")
```

### Configuration using `jsonlog.basicConfig`

The `jsonlog.basicConfig` function accepts slightly different parameters to
`logging.basicConfig`. It's shown here with the defaults for each parameter.

The `filename`, `filemode` and `stream` parameters work the same way as their
equivalents in `logging.basicConfig`, and as such `filename` and `stream` are
exclusive. 

```python
import jsonlog

jsonlog.basicConfig(
    level=jsonlog.INFO,
    indent=None,
    keys=("time", "level", "message"),
    timespec="auto",
    # filename=None,
    # filemode="a",
    # stream=None,
)
```

### Configuration using `logging.config.dictConfig`

Any of the configuration methods in `logging.config` can be used to configure a
handler that uses `jsonlog.formmatters.JSONFormatter` to format records as JSON. 

```python
import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {"json": {"()": "jsonlog.JSONFormatter"}},
        "handlers": {"stream": {"class": "logging.StreamHandler", "formatter": "json"}},
        "loggers": {"": {"handlers": ["stream"]}},
    }
)
```

### Adding extra attributes to JSON output

If `LogRecord.args` is a mapping, the values in the mapping will be included in
the JSON object the formatter creates.

```python
import jsonlog

jsonlog.warning("User clicked a button", {"user": 123})
```

```
{"time": "2019-06-21T16:25:05.823190", "level": "WARNING", "message": "User clicked a button", "user": 123}
```

### Passing extra attributes as keyword arguments.

The `jsonlog.logger.JSONLogger` class modifies the signature of `.log()` and
it's related methods to accept arbitrary keyword arguments. These are stored in
a record's `args` attributes as a map.

You can't use this feature on the root logger (and any module level methods that
use the root logger). Loggers created before `jsonlog.basicConfig` is called may
still be `logging.Logger` instances - if you want to ensure they are
`jsonlog.JSONLogger` instances use `jsonlog.getLogger` to create them.

```python
import jsonlog

jsonlog.warning("User clicked a button", user=123)
```

The `jsonlog.logger.JSONLogger` class will be automatically installed as the
default logger class when `jsonlog.basicConfig()` is called. You can also
manually configure it as the default logger class:

```python
import logging
import jsonlog

logging.setLoggerClass(jsonlog.JSONLogger)
```

Compatibility
-------------

`jsonlog` is written for Python 3.7 and above. Compatibility patches will be
accepted for Python 3.5 and above, but patches for Python 2 will be rejected.

Authors
-------

* [Sam Clements](https://gitlab.com/borntyping)
