legere
======

A human readable formatter for JSON logs.
 
It's built for use with [jsonlog] but will work well with any log format that
uses line delimited JSON.

![Example output](https://raw.githubusercontent.com/borntyping/legere/master/docs/example.png)

Usage
-----

Pass a file as the only argument to `legere`, or read from STDIN by default.

```bash
legere docs/example.log
```

```bash
python docs/example.py | legere
```

Configuration
-------------

See `legere --help` for all options.

Only show timestamps and messages (defaults to `{timestamp} {level} {name} {message}`).

```bash
legere --format "{timestamp} {message}" docs/example.log
```

Configure the keys of multiline values you want to display (can be specified
multiple times, and defaults to the `traceback` key.)

```bash
legere --format "{timestamp} {message}" docs/example.log
```

Configure the key to extract and use as the records level, controlling the
colour each line is printed in (defaults to the `level` key).

```bash
legere --format "{timestamp} {message}" docs/example.log
```

Authors
-------

* [Sam Clements]

[jsonlog]: https://github.com/borntyping/jsonlog
[Sam Clements]: https://gitlab.com/borntyping
