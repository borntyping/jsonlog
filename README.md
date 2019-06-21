jsonlog
=======

A drop-in formatter for Python's `logging` module that outputs messages as line
delimited JSON.

While `jsonlog` provides it's own `basicConfig` method so you can get started
quickly, all of it's features and classes can be used with the `logging` module.

Usage
-----

You can use `jsonlog` as a drop-in replacement for `logging`:

```python
import jsonlog

jsonlog.warning("Hello world.")
```

It's implemented as a log formatter, so you can use `logging` just like you
normally would.

```python
import jsonlog
import logging

jsonlog.basicConfig(level=jsonlog.INFO)
jsonlog.warning("Works with functions in the jsonlog module.")
logging.warning("And works with functions in the logging module.")
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

Record attributes provided with `extra=` will be included in the JSON object.

```python
import jsonlog
import logging

jsonlog.basicConfig()
logging.warning("User clicked a button", extra={"user": 123})
```

```
{"time": "2019-06-21T16:25:05.823190", "level": "WARNING", "message": "User clicked a button", "user": 123}
```

If a mapping is passed as the only positional argument, attributes from the
mapping will also be included.

```python
import jsonlog
import logging

jsonlog.basicConfig()
logging.warning("User clicked a button", {"user": 123})
```


Compatibility
-------------

`jsonlog` is written for Python 3.7 and above. Compatibility patches will be
accepted for Python 3.5 and above, but patches for Python 2 will be rejected.

Authors
-------

* [Sam Clements](https://gitlab.com/borntyping)
