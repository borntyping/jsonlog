jsonlog
=======

A drop-in formatter for Python's `logging` library that outputs messages as line
delimited JSON.

Usage
-----

You can use `jsonlog` as a drop-in replacement for `logging`:

```python
import jsonlog


def main():
    jsonlog.basicConfig()
    jsonlog.info("Application started.")


if __name__ == '__main__':
    main()
```

Compatibility
-------------

`jsonlog` is written for Python 3.7 and above. Compatibility patches will be
accepted for Python 3.5 and above, but patches for Python 2 will be rejected.

Authors
-------

* [Sam Clements](https://gitlab.com/borntyping)
