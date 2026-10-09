"""The theme READMEs: every plate credited, every number taken from the built palette."""

from athanor_omarchy.images import PLATES, plate_names
from athanor_omarchy.palette import theme_colors
from athanor_omarchy.readme import PLATE_BOOKS, readme


def test_every_plate_has_a_book_credit():
    for plate in [*PLATES["level"], PLATES["lock"]]:
        assert plate["file"] in PLATE_BOOKS, plate["file"]


def test_readme_shows_the_tuned_palette():
    for name in ("umber", "vellum"):
        c = theme_colors(name)
        text = readme(name, c)
        for key in ("background", "foreground", "accent", "selection", "muted", "red", "cyan"):
            assert f"`{c[key]}`" in text, (name, key)
        assert text.count("commons.wikimedia.org") == len(plate_names())
