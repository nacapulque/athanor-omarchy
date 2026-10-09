"""btop.theme and vscode-theme.json: faithful to Omarchy's templates, plus the contrast fixes."""

import json
import re
from pathlib import Path

import pytest

from athanor_omarchy import apps
from athanor_omarchy.color import contrast, mix
from athanor_omarchy.palette import PALETTE, theme_colors

# What `omarchy theme set` generated for each theme under omarchy 4.0.4.
GENERATED = Path(__file__).parent / "fixtures/omarchy-generated"


@pytest.mark.parametrize("name", ["umber", "vellum"])
@pytest.mark.parametrize("template", ["btop.theme", "vscode-theme.json"])
def test_render_matches_omarchy(name, template):
    """Before our patches, the renderer reproduces Omarchy's own output byte for byte."""
    tpl = (apps.TEMPLATES / f"{template}.tpl").read_text()
    assert apps.render(tpl, theme_colors(name)) == (GENERATED / name / template).read_text()


@pytest.mark.parametrize("name", list(PALETTE))
def test_btop_selected_row(name):
    c = theme_colors(name)
    theme = dict(re.findall(r'theme\[(\w+)\]="(#[0-9a-fA-F]{6})"', apps.btop_theme(c)))
    assert contrast(theme["selected_fg"], theme["selected_bg"]) >= 4.5


def blend(color, over):
    """Composite an #rrggbbaa color over an opaque #rrggbb one."""
    alpha = int(color[7:9], 16) / 255 if len(color) == 9 else 1.0
    return mix(over, color[:7], alpha)


@pytest.mark.parametrize("name", list(PALETTE))
def test_vscode_selection_and_current_line_show(name):
    c = theme_colors(name)
    v = json.loads(apps.vscode_theme(c))["colors"]
    bg, fg = v["editor.background"], v["editor.foreground"]
    selection = blend(v["editor.selectionBackground"], bg)
    line = blend(v["editor.lineHighlightBackground"], bg)
    # Omarchy's 22 stock themes put their selection at 1.21–2.45:1 against the
    # background (median 1.43). The template's 38% blend lands near 1.15, below all of them.
    assert contrast(selection, bg) >= 1.25, "selection barely shows"
    assert contrast(line, bg) > 1.05, "current line doesn't show"
    assert contrast(fg, selection) >= 7
    assert contrast(selection, bg) > contrast(line, bg), "the current line outshines the selection"


def test_patches_fail_loudly_when_the_template_moves():
    with pytest.raises(ValueError):
        apps.patch("nothing to see", "theme[selected_fg]", "x")


def test_unknown_placeholders_fail():
    with pytest.raises(KeyError):
        apps.render("{{ not_a_color }}", theme_colors("umber"))
