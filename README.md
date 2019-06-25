revelio
=======

A human readable formatter for JSON logs.
 
It's built for use with [jsonlog] but will work well with any log format that
uses line delimited JSON.

![Example output](https://raw.githubusercontent.com/borntyping/revelio/master/docs/example.png)

Usage
-----

Pass a file as the only argument to `revelio`, or read from STDIN by default.

```bash
revelio docs/example.log
```

```bash
python docs/example.py | revelio
```

Configuration
-------------

See `revelio --help` for all options.

Only show timestamps and messages (defaults to `{timestamp} {level} {name} {message}`).

```bash
revelio --format "{timestamp} {message}" docs/example.log
```

Configure the keys of multiline values you want to display (can be specified
multiple times, and defaults to the `traceback` key.)

```bash
revelio --format "{timestamp} {message}" docs/example.log
```

Configure the key to extract and use as the records level, controlling the
colour each line is printed in (defaults to the `level` key).

```bash
revelio --format "{timestamp} {message}" docs/example.log
```

Authors
-------

* [Sam Clements]

[jsonlog]: https://gitlab.com/borntyping/jsonlog
[Sam Clements]: https://gitlab.com/borntyping
