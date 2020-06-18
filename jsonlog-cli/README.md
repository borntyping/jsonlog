jsonlog-cli
===========

A human readable formatter for JSON logs.

It's built for use with [jsonlog] but will work well with any log format that
uses line delimited JSON.

![Example output](https://raw.githubusercontent.com/borntyping/jsonlog-cli/master/docs/example.png)

Usage
-----

Pass a file as the only argument to `jsonlog`, or read from STDIN by default.

```bash
jsonlog kv docs/example.log
```

```bash
python docs/example.py | jsonlog kv
```

Configuration
-------------

See `jsonlog --help` for all options.

Only show the `timestamp` and `message` fields:

```bash
jsonlog kv --key timestamp --key message docs/example.log
```

```bash
jsonlog template --format "{timestamp} {message}" docs/example.log
```

Configure the keys of multiline values you want to display (can be specified
multiple times, and defaults to the `traceback` key.)

```bash
jsonlog kv --key timestamp --key message --multiline-key traceback docs/example.log
```

Configure the key to extract and use as the records level, controlling the
colour each line is printed in (defaults to the `level` key).

```bash
jsonlog kv --level-key level --key timestamp --key message --multiline-key traceback docs/example.log
```

Compatibility
-------------

`jsonlog-cli` is written for Python 3.6 and above. Compatibility patches will be
accepted for Python 3.5 and above, but patches for Python 2 will be rejected.


Authors
-------

* [Sam Clements]

[jsonlog]: https://github.com/borntyping/jsonlog
[Sam Clements]: https://gitlab.com/borntyping
