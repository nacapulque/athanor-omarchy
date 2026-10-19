"""Section files must restate their whole template section, since each one replaces it."""

import re
from pathlib import Path

import pytest

from athanor_omarchy.palette import PALETTE, theme_colors
from athanor_omarchy.shell import bar_section, shell_sections

# Omarchy's default/themed/shell.toml.tpl, snapshotted from omarchy 4.0.4.
TEMPLATE = Path(__file__).parent / "fixtures/shell.toml.tpl"
KEY = re.compile(r"^(#\s*)?([a-z][a-z0-9-]*)\s*=")

# Sections whose border goes through Border.surfaceSpec, which reads `border-width`
# for any section even where the template doesn't mention it (omarchy 4.0.4:
# Menu.qml, PolkitAgent.qml, LockView.qml, NotificationCard.qml, popups, tooltips).
# [launcher] is not emitted at all: nothing in the shell reads it (omarchy 4.0.5).
READS_BORDER_WIDTH = {"menu", "popups", "tooltip", "notifications", "polkit", "lock"}


def template_keys():
    """{section: (required keys, optional keys)}; optional ones are commented out in the template."""
    sections, current = {}, None
    for line in TEMPLATE.read_text().splitlines():
        if m := re.match(r"^\[([a-z-]+)\]", line):
            current = sections.setdefault(m.group(1), (set(), set()))
        elif current is not None and (m := KEY.match(line.strip())):
            (current[1] if m.group(1) else current[0]).add(m.group(2))
    return sections


def section_keys(text):
    return {m.group(2) for line in text.splitlines() if (m := KEY.match(line)) and not m.group(1)}


def emitted(name):
    p, c = PALETTE[name], theme_colors(name)
    files = {section: f"[{section}]\n" + body for section, body in shell_sections(p, c).items()}
    files["bar"] = bar_section(p)
    return files


@pytest.mark.parametrize("name", list(PALETTE))
def test_sections_restate_every_key(name):
    tpl = template_keys()
    for section, text in emitted(name).items():
        assert section in tpl, f"[{section}] isn't a section of the shell template"
        required, optional = tpl[section]
        keys = section_keys(text)
        assert required <= keys, f"[{section}] drops {sorted(required - keys)}"
        known = required | optional | ({"border-width"} if section in READS_BORDER_WIDTH else set())
        assert keys <= known, f"[{section}] adds keys the shell doesn't read: {sorted(keys - known)}"


@pytest.mark.parametrize("name", list(PALETTE))
def test_section_files_have_their_header(name):
    for section, text in emitted(name).items():
        assert text.startswith(f"[{section}]\n")


SHELL_QML = Path("/usr/share/omarchy/shell")


@pytest.mark.skipif(not SHELL_QML.exists(), reason="needs an installed Omarchy")
def test_launcher_section_is_still_unread():
    """We stopped shipping shell.launcher.toml because no QML reads a launcher.* token.
    Tokens are read as quoted "section.key" strings (e.g. "menu.background"); the quote
    keeps the filename launcher.hides in AppLibrary.qml from matching. If this fails after
    an Omarchy update, bring the section back in shell.py."""
    hits = [p for p in SHELL_QML.rglob("*.qml") if re.search(r'"launcher\.[a-z-]+', p.read_text())]
    assert hits == [], hits
