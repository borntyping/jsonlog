jsonlog-cli
===========

A human readable formatter for JSON logs.
 
It's built for use with [jsonlog] but will work well with any log format that
uses line delimited JSON.

![Example output](https://raw.githubusercontent.com/borntyping/jsonlog-cli/master/docs/example.png)

Usage
-----

See `jsonlog --help` for all options.

### Key-value mode

Pass a file as the only argument to `jsonlog`, or read from STDIN by default.

```bash
jsonlog kv docs/example.log
```

```bash
python docs/example.py | jsonlog kv
```

```bash
cat docs/example.log | jsonlog
```

Only show the `timestamp` and `message` fields:

```bash
jsonlog kv --key timestamp --key message docs/example.log
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

### Template mode

Only show the `timestamp` and `message` fields:

```bash
jsonlog template --format "{timestamp} {message}" docs/example.log
```

Also show a multiline key when it's present:

```bash
jsonlog template --format "{timestamp} {message}" --multiline-key traceback docs/example.log
```

Configuration
-------------

Named "patterns" are supported as a way of collecting a set of options for
jsonlog's key-value and template modes. If `~/.config/jsonlog/config.json`
exists, it will be loaded at startup. All fields should be optional.

The example configuration file below creates patterns named `example` and
`defaults` for the key-value and template modes. The patterns named `example`
will show the `timestamp` and `message` fields of incoming logs. The patterns
named `defaults` set all fields to their default values.

```json
{
  "keyvalues": {
    "example": {
      "priority_keys": ["timestamp", "message"]
    },
    "defaults": {
      "level_key": "level",
      "multiline_json": false,
      "multiline_keys": [],
      "priority_keys": [],
      "removed_keys": []
    }
  },
  "templates": {
    "example": {
      "format": "{timestamp} {message}"
    },
    "defaults": {
      "level_key": "level",
      "multiline_json": false,
      "multiline_keys": [],
      "format": "{timestamp} {message}" 
    }
  }
}
```

Authors
-------

* [Sam Clements]

[jsonlog]: https://github.com/borntyping/jsonlog
[Sam Clements]: https://gitlab.com/borntyping
