# athanor-omarchy

Source for the Athanor [Omarchy](https://omarchy.org) themes, built from
[script-wizards/athanor](https://github.com/script-wizards/athanor).

Published themes:

- [omarchy-athanor-umber-theme](https://github.com/nacapulque/omarchy-athanor-umber-theme)
- [omarchy-athanor-vellum-theme](https://github.com/nacapulque/omarchy-athanor-vellum-theme)

Those repos are build output. Change things here, then publish.

## Build

Needs Python 3.11+ and ImageMagick 7. No Python dependencies.

```sh
git clone --recurse-submodules https://github.com/nacapulque/athanor-omarchy
cd athanor-omarchy
python -m athanor_omarchy build              # Umber and Vellum into dist/
python -m athanor_omarchy build --theme orpiment --theme cinnabar
```

The build prints each theme's key contrast ratios.

## Test

```sh
uv run --no-project --with pytest pytest     # or: python -m pytest
```

The tests pin what the themes promise: contrast floors for every text color on
every surface, the neutral ramp's order, canonical `colors.toml` keys, and that
each `shell.<section>.toml` restates its whole section of Omarchy's template
(snapshotted in `tests/fixtures/`). The end-to-end build test needs ImageMagick
7 and skips without it. CI runs everything else on every PR.

## Publish

```sh
scripts/publish.sh umber                      # build, then list what changed
scripts/publish.sh umber -m "Subject

Body."                                        # also branch, commit, push and open a PR
```

The script expects a clone of each theme repo at
`~/.config/omarchy/themes/athanor-<theme>` (override with
`ATHANOR_THEMES_DIR`), clean and on `main`. It copies only the files whose
content changed. PNGs count as changed only when their pixels differ, since
ImageMagick stamps a creation time into every file.

To compare a build with a checkout by hand:

```sh
python -m athanor_omarchy diff dist/athanor-umber ~/.config/omarchy/themes/athanor-umber
```

## Previews

```sh
scripts/shoot-previews.sh            # umber and vellum
scripts/shoot-previews.sh vellum
```

This takes each theme's `preview.png` on the real desktop. It applies the
build as a temporary `athanor-<theme>-preview` theme and opens three panes on
an empty workspace 9: Neovim with Athanor's `planetary.c`, a fastfetch that
lists only software (`assets/preview/fastfetch.jsonc`), and Athanor's git
history with the palette (`assets/preview/pane.sh`). It OCRs the shot and
refuses to save it if your username, hostname, a home path or the hardware
model shows up. It aborts if workspace 9 isn't empty or a pane lands
elsewhere, and restores your workspace and theme when it exits. It needs a
Hyprland Lua config, foot, nvim, fastfetch, grim, tesseract and ImageMagick 7,
and takes over the screen for about 20 seconds per theme.

## Layout

| Path | What |
|---|---|
| `athanor_omarchy/palette.py` | Athanor's palette in Omarchy's `colors.toml` roles, and the contrast tuning |
| `athanor_omarchy/color.py` | Hex, WCAG contrast and OKLCH helpers |
| `athanor_omarchy/shell.py` | `shell.<section>.toml` overrides |
| `athanor_omarchy/images.py` | Dithered plates, logo wallpaper, unlock art and previews |
| `athanor_omarchy/readme.py` | The themes' README and LICENSE |
| `vendor/athanor` | Athanor, pinned as a submodule: the palette and the plates |
| `assets/omarchy/` | Omarchy's unlock wordmark and logo wallpaper, recolored per theme |
| `assets/previews/` | Desktop screenshots used as each theme's `preview.png`, from `scripts/shoot-previews.sh` |
| `assets/preview/` | What the preview panes run |

The plan for this repo and its current status are in
[docs/PLAN.md](docs/PLAN.md). Render it with
`python -I scripts/render-plan.py docs/PLAN.md ~/claude-plan.html`.

## License

MIT. Athanor's palette and dither recipe are MIT, © 2026 Script Wizards.
`assets/omarchy/` is from [Omarchy](https://github.com/basecamp/omarchy), MIT.
The Doré plates are public domain.
