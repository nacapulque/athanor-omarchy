"""README.md and LICENSE for a published theme repo."""

from .images import PLATES, plate_names
from .palette import PALETTE, THEMES

REPO = "https://github.com/nacapulque/omarchy-athanor-{}-theme"
ATHANOR_URL = "https://github.com/script-wizards/athanor"

# The book and edition each Doré plate comes from, keyed by plates.toml filename.
PLATE_BOOKS = {
    "merlin-and-the-king.jpg": "Idylls of the King, 1868",
    "merlin-and-the-book.jpg": "Idylls of the King, 1868",
    "merlin-and-vivien.jpg": "Idylls of the King, 1868",
    "the-grotto.jpg": "Idylls of the King, 1868",
    "hooded-figures.jpg": "Orlando Furioso, 1879",
    "the-lamp-lit-hall.jpg": "Orlando Furioso, 1879",
    "the-graveyard.jpg": "The Raven, 1884",
    "satans-despair.jpg": "Paradise Lost, 1866",
}
# plates.toml names the lock plate with its book; the credits table lists the book separately.
PLATE_TITLES = {"satans-despair.jpg": "Satan's despair"}


def plate_rows():
    plates = [*PLATES["level"], PLATES["lock"]]
    missing = [pl["file"] for pl in plates if pl["file"] not in PLATE_BOOKS]
    if missing:
        raise KeyError(f"no book credit for plates: {missing}")
    return "\n".join(
        f"| {n} | [*{PLATE_TITLES.get(pl['file'], pl['name'])}*]({pl['source']}) | {PLATE_BOOKS[pl['file']]} |"
        for n, pl in enumerate(plates, start=1)
    )


def readme(name, c):
    t, label = THEMES[name], PALETTE[name]["label"]
    other = t["companion"]
    o_label, o_stage = PALETTE[other]["label"], THEMES[other]["stage"]
    palette = "\n".join(
        f"| {role} | `{c[k]}` |"
        for role, k in [("Background", "background"), ("Foreground", "foreground"), ("Accent", "accent"),
                        ("Selection", "selection"), ("Muted", "muted")]
    )  # fmt: skip
    ansi = " ".join(f"`{c[k]}`" for k in ["red", "green", "yellow", "blue", "magenta", "cyan"])
    plates = len(plate_names())
    return f"""# Athanor {label}

{t['tagline']} A {t['mode']} [Omarchy](https://omarchy.org) theme based on
[Athanor]({ATHANOR_URL}) by Script Wizards, an
alchemical layer for Arch and Hyprland.

Athanor's four color schemes are the stages of the Magnum Opus. {label} is
*{t['stage']}*, {t['gloss']}. Its companion is
[Athanor {o_label}]({REPO.format(other)})
(*{o_stage}*).

![Athanor {label} desktop with Neovim, fastfetch and the terminal palette](preview.png)

## Install

```sh
omarchy theme install {REPO.format(name)}
omarchy theme set athanor-{name}
```

`omarchy theme bg next` cycles the wallpapers, and `omarchy theme update`
pulls new versions of the theme.

## What's in it

| File | What it does |
|---|---|
| `colors.toml` | The palette. Omarchy generates the terminal, Hyprland, Neovim, Helix and shell colors from it. |
| `btop.theme`, `vscode-theme.json` | Omarchy's own btop and VS Code themes, with fixes: the selected btop row in foreground text, and VS Code selections and the current line made visible. |
| `shell.bar.toml` | The status bar in Athanor's own bar colors. |
| `shell.*.toml` | The rest of the Omarchy shell in Athanor's style. See [Shell](#shell). |
| `backgrounds/` | {NUMBERS[plates]} Doré plates plus the Omarchy logo wallpaper. |
| `icons.theme` | `{t['icons']}` icons. |
| `preview.png`, `preview-unlock.png`, `unlock.png` | Theme switcher previews and the boot-unlock logo. |

### Palette

| Role | Color |
|---|---|
{palette}

ANSI red, green, yellow, blue, magenta and cyan: {ansi}.

The palette is Athanor's {label}. The ANSI colors keep Athanor's hues,
with only their lightness nudged so terminal text holds up on every surface it
sits on:

- at least 5:1 on the background
- at least 4.5:1 on raised surfaces, such as editor cursorlines and herdr or
  Helix panels
- at least 3:1 inside a selection

Body text is above 12:1.

### Shell

The Omarchy shell follows Athanor's own UI: flat, opaque cards with a 2px
accent rule, and the selected row drawn in inverse, like Athanor's quit prompt
and its `--More--` line.

- **Menu and launcher:** opaque card, accent border, inverse selection.
- **Notifications and popups:** opaque, accent border and countdown.
- **Lock screen and password prompts:** an opaque card ruled in the accent,
  red on a wrong password.
- **Tooltips:** in the status bar's colors.
- **Controls:** keyboard focus gets the accent outline.

These style Omarchy's built-in shell plugins. A replacement notification or
lock plugin draws itself and may ignore them.

### Wallpapers

The wallpapers are Gustave Doré's wood engravings, dithered to two tones with
Floyd-Steinberg in the palette's ground and ink colors, as Athanor makes them.
They're 3840×2160, drawn on a 960×540 grid and pixel quadrupled, so the
dither stays crisp on 4K and scales down evenly to 1080p.

## What's not in it

This theme only carries Athanor's look. The roguelike status line, planetary
hours, tarot draws, lockscreen sigils, a plate per workspace, the bitmap fonts
and the notch plugin belong to
[Athanor itself]({ATHANOR_URL}). Install it for the
whole furnace.

## Credits

The palette, the dither recipe and the idea come from
[Athanor]({ATHANOR_URL}), MIT, © 2026 Script Wizards.
This theme isn't affiliated with or endorsed by them.

The plates are public domain, from Wikimedia Commons:

| # | Plate | From |
|---|---|---|
{plate_rows()}

## License

MIT. See [LICENSE](LICENSE).
"""


NUMBERS = {7: "Seven", 8: "Eight", 9: "Nine"}

LICENSE = """MIT License

Copyright (c) 2026 Script Wizards (Athanor palette and dither recipe)
Copyright (c) 2026 Raúl Salinas (Omarchy theme adaptation)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The Gustave Doré engravings in backgrounds/ are in the public domain.
"""
