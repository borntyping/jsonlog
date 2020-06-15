jsonlog
=======

A set of Python modules for working with structured JSON logs.

* [jsonlog](./jsonlog/README.md) provides a JSON formatter for Python's `logging` module.
* [jsonlog-cli](./jsonlog-cli/README.md) provides a command line tool for converting JSON
logs into human readable output.

The `jsonlog` module
--------------------

You can use `jsonlog` as a drop-in replacement for `logging`:

```python
import jsonlog

jsonlog.warning("Hello world.")
```

```json
{"timestamp": "2019-06-21T19:06:25.285730", "level": "WARNING", "name": "root", "message": "Hello world."}
```

See the [jsonlog] README for documentation and examples.

The `jsonlog` cli
-----------------

Pipe line-delimited JSON into the `jsonlog` CLI:

```bash
python jsonlog-cli/docs/example.py | jsonlog
```

```text
timestamp='2020-06-15T13:27:41.909782' name='example' message='debug level log message'
timestamp='2020-06-15T13:27:41.909882' name='example' message='info level log message'
timestamp='2020-06-15T13:27:41.909940' name='example' message='warning level log message'
timestamp='2020-06-15T13:27:41.909990' name='example' message='error level log message'
timestamp='2020-06-15T13:27:41.910040' name='example' message='error level log message with traceback'

    Traceback (most recent call last):
      File "jsonlog-cli/docs/example.py", line 15, in <module>
        1 / 0
    ZeroDivisionError: division by zero

timestamp='2020-06-15T13:27:41.910239' name='example' message='critical level log message'
```

See the [jsonlog-cli] README for documentation and examples.

Authors
-------

* [Sam Clements]

[jsonlog-cli]: ./jsonlog-cli/README.md
[jsonlog]: ./jsonlog/README.md
[Sam Clements]: https://gitlab.com/borntyping
