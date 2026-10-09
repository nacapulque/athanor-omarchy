"""Contrast floors and palette shape that the published themes promise in their READMEs."""

import tomllib

import pytest

from athanor_omarchy.color import contrast
from athanor_omarchy.palette import GROUPS, HUES, PALETTE, TEXT, colors_toml, theme_colors

THEMES = list(PALETTE)

# Omarchy's canonical colors.toml keys (docs/theming.md), plus the two Hyprland border roles.
CANONICAL = {
    "mode", "accent", "selection", "muted",
    "background", "dark_background", "darker_background", "lighter_background",
    "foreground", "dark_foreground", "light_foreground", "bright_foreground",
    "red", "yellow", "orange", "green", "cyan", "blue", "magenta", "brown",
    "bright_red", "bright_yellow", "bright_green", "bright_cyan", "bright_blue", "bright_magenta",
    "hyprland_active_border", "hyprland_inactive_border",
}  # fmt: skip


@pytest.fixture(params=THEMES)
def theme(request):
    return request.param, theme_colors(request.param)


def test_body_text(theme):
    _, c = theme
    assert contrast(c["foreground"], c["background"]) >= 12


@pytest.mark.parametrize("key", TEXT)
@pytest.mark.parametrize(("surface", "floor"), [("background", 5.0), ("lighter_background", 4.5), ("selection", 3.0)])
def test_text_on_surfaces(theme, key, surface, floor):
    _, c = theme
    assert contrast(c[key], c[surface]) >= floor, f"{key} on {surface}"


@pytest.mark.parametrize("hue", HUES)
def test_bright_variants(theme, hue):
    _, c = theme
    bright = c["bright_" + hue]
    for surface, floor in [("background", 5.0), ("lighter_background", 4.5), ("selection", 3.0)]:
        assert contrast(bright, c[surface]) >= floor, f"bright_{hue} on {surface}"
    assert contrast(bright, c[hue]) >= 1.2, f"bright_{hue} too close to {hue}"


def test_accent_and_dim_text(theme):
    _, c = theme
    assert contrast(c["accent"], c["background"]) >= 4.5
    assert contrast(c["dark_foreground"], c["background"]) >= 3.0


def test_inverse_selection(theme):
    """Menu and launcher draw the selected row as background on foreground."""
    _, c = theme
    assert contrast(c["background"], c["foreground"]) >= 7


def test_bar_and_tooltip(theme):
    name, _ = theme
    p = PALETTE[name]
    assert contrast(p["barfg"], p["bar"]) >= 4.5
    assert contrast(p["bar_warn"], p["bar"]) >= 4.5


def test_neutral_ramp(theme):
    """Seen from the background, each neutral stands out more than the one before.

    This reads the same way for dark and light themes, so it checks the ramp's
    order without caring which way it runs.
    """
    _, c = theme
    ramp = ["lighter_background", "selection", "dark_foreground", "muted", "light_foreground", "foreground"]
    seen = [contrast(c[k], c["background"]) for k in ramp]
    assert seen == sorted(seen), dict(zip(ramp, seen))
    assert contrast(c["bright_foreground"], c["background"]) >= contrast(c["foreground"], c["background"])
    # Recessed panels must stay quieter than the selection, or they read as highlighted.
    for k in ("dark_background", "darker_background"):
        assert contrast(c[k], c["background"]) < contrast(c["selection"], c["background"]), k


def test_colors_toml_is_canonical(theme):
    name, c = theme
    parsed = tomllib.loads(colors_toml(name, c))
    assert set(parsed) == CANONICAL
    assert [k for group in GROUPS for k in group] == [k for k in parsed]
    assert parsed["mode"] in ("dark", "light")
