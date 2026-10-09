"""App configs Omarchy would generate from colors.toml, rendered here with targeted fixes.

A theme that ships btop.theme or vscode-theme.json replaces Omarchy's generated
file outright, so these are rendered from Omarchy's own templates (snapshotted
from omarchy 4.0.4 in assets/omarchy/themed/) and then patched in a few places:

- btop draws the selected process row as accent text on the selection. On
  Vellum that's 3.24:1; foreground text clears 8:1 on both themes.
- VS Code paints the editor selection at 38% alpha and the current line in the
  background color itself, so selections barely show (about 1.15:1) and the
  current line doesn't show at all.
"""

import json
import re

from .paths import ASSETS

TEMPLATES = ASSETS / "omarchy/themed"
PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")


def values(c):
    """colors.toml plus the keys Omarchy derives (omarchy-theme-color --all)."""
    return {**c, "selection_background": c["selection"], "selection_foreground": c["bright_foreground"], "theme_type": c["mode"]}


def render(template, c):
    v = values(c)

    def sub(m):
        if m.group(1) not in v:
            raise KeyError(f"template placeholder {{{{ {m.group(1)} }}}} has no value")
        return v[m.group(1)]

    return PLACEHOLDER.sub(sub, template)


def patch(text, old, new):
    """Replace one exact line fragment; fail if the template no longer has it exactly once."""
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {old!r} in the rendered template")
    return text.replace(old, new)


def btop_theme(c):
    text = render((TEMPLATES / "btop.theme.tpl").read_text(), c)
    return patch(text, f'theme[selected_fg]="{c["accent"]}"', f'theme[selected_fg]="{c["foreground"]}"')


def vscode_theme(c):
    text = render((TEMPLATES / "vscode-theme.json.tpl").read_text(), c)
    text = patch(text, f'"editor.selectionBackground": "{c["selection"]}60"', f'"editor.selectionBackground": "{c["selection"]}"')
    text = patch(
        text,
        f'"editor.lineHighlightBackground": "{c["background"]}60"',
        f'"editor.lineHighlightBackground": "{c["lighter_background"]}"',
    )
    json.loads(text)
    return text
