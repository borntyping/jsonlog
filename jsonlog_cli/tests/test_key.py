from jsonlog_cli.key import Key


def test_contains():
    assert Key("a") in {Key("a"), Key("b"), Key("c")}


def test_format():
    assert Key("a", "{:1}") in {Key("a"), Key("b"), Key("c")}
    assert Key("traceback") in {Key("traceback")}
