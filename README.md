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

```json
{"timestamp": "2019-06-21T19:06:25.285730", "level": "WARNING", "name": "root", "message": "Hello world."}
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
    keys=("timestamp", "level", "message"),
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

```json
{"timestamp": "2019-06-21T19:06:54.293929", "level": "WARNING", "name": "root", "message": "User clicked a button", "user": 123}
```

If a mapping is passed as the only positional argument, attributes from the
mapping will also be included.

```python
import jsonlog
import logging

jsonlog.basicConfig()
logging.warning("User clicked a button", {"user": 123})
```

### Pipelining

Try piping logs through [jq] if you want to read them on the command line!

```bash
python examples/hello.py 2> >(jq .)
```

```json
{
  "timestamp": "2019-06-21T19:07:43.211782",
  "level": "WARNING",
  "name": "root",
  "message": "Hello world."
}

```

### Tracebacks

Tracebacks are included as a single string - it's not very nice to read, but
means it'll play nicely with any systems that read the JSON logs you output.

```json
{"timestamp": "2019-06-21T19:08:37.326897", "level": "ERROR", "name": "root", "message": "Encountered an error", "traceback": "Traceback (most recent call last):\n  File \"examples/error.py\", line 6, in <module>\n    raise ValueError(\"Example exception\")\nValueError: Example exception"}
```

Tools like [jq] make it easy to extract and read the traceback:

```bash
python examples/error.py 2> >(jq -r ".traceback")
```

```
Traceback (most recent call last):
  File "examples/error.py", line 6, in <module>
    raise ValueError("Example exception")
ValueError: Example exception
``` 

Compatibility
-------------

`jsonlog` is written for Python 3.7 and above. Compatibility patches will be
accepted for Python 3.5 and above, but patches for Python 2 will be rejected.

References
----------

* Build for use with the [logging] module.
* Partially based on [colorlog].
* Works great with [jq]!

Authors
-------

* [Sam Clements]

[colorlog]: https://gitlab.com/borntyping/colorlog
[jq]: https://stedolan.github.io/jq/
[logging]: https://docs.python.org/3/library/logging.html
[Sam Clements]: https://gitlab.com/borntyping
