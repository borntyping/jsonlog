from jsonlog_cli.colours import ColourMap, Colour


def test_colour_map():
    assert ColourMap({"Test": Colour(fg="red")}).get("tEST") == Colour(fg="red")


def test_colour_map_missing():
    assert ColourMap({"Test": Colour(fg="red")}).get("missing") == Colour()
