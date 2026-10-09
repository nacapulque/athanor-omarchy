"""Build Omarchy theme directories from Athanor's palette and plates."""

import argparse
import shutil
from pathlib import Path

from . import apps, images
from .color import contrast
from .compare import compare
from .palette import PALETTE, THEMES, colors_toml, theme_colors
from .paths import ASSETS
from .readme import LICENSE, readme
from .shell import bar_section, shell_sections

PUBLISHED = ["umber", "vellum"]


def build_theme(name, out, width=3840, height=2160, pixel=4):
    """Write athanor-<name>/ under out, replacing its backgrounds. Returns the tuned colors."""
    p, c = PALETTE[name], theme_colors(name)
    d = out / f"athanor-{name}"
    d.mkdir(parents=True, exist_ok=True)

    (d / "colors.toml").write_text(colors_toml(name, c))
    (d / "btop.theme").write_text(apps.btop_theme(c))
    (d / "vscode-theme.json").write_text(apps.vscode_theme(c))
    (d / "icons.theme").write_text(THEMES[name]["icons"] + "\n")
    (d / "shell.bar.toml").write_text(bar_section(p))
    for section, body in shell_sections(p, c).items():
        (d / f"shell.{section}.toml").write_text(f"[{section}]\n" + body)
    if THEMES[name]["companion"]:
        (d / "README.md").write_text(readme(name, c))
    (d / "LICENSE").write_text(LICENSE)

    bgs = d / "backgrounds"
    if bgs.exists():
        shutil.rmtree(bgs)
    images.backgrounds(p, bgs, width, height, pixel)
    images.logo_wallpaper(p, bgs / "omarchy.png")
    images.unlock(p, d / "unlock.png")
    images.preview_unlock(c, d / "unlock.png", d / "preview-unlock.png")

    # Desktop previews are screenshots, kept as assets; fall back to the first plate.
    shot = ASSETS / "previews" / f"{name}.png"
    if shot.exists():
        shutil.copyfile(shot, d / "preview.png")
    else:
        images.magick(bgs / images.plate_names()[0], "-filter", "point", "-resize", "1800x1012!", d / "preview.png")
    return c


def report(name, c):
    p = PALETTE[name]
    checks = {
        "fg/bg": contrast(c["foreground"], c["background"]),
        "accent/bg": contrast(c["accent"], c["background"]),
        "muted/bg": contrast(c["muted"], c["background"]),
        "bar": contrast(p["barfg"], p["bar"]),
        "bar warn": contrast(p["bar_warn"], p["bar"]),
        "menu inverse": contrast(c["background"], c["foreground"]),
        "text on selection": contrast(c["bright_foreground"], c["selection"]),
    }
    return f"athanor-{name}: " + "  ".join(f"{k} {v:.2f}" for k, v in checks.items())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="athanor_omarchy", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build theme directories")
    b.add_argument("--theme", action="append", choices=list(PALETTE), help=f"repeatable; default: {', '.join(PUBLISHED)}")
    b.add_argument("--out", type=Path, default=Path("dist"))
    b.add_argument("--width", type=int, default=3840)
    b.add_argument("--height", type=int, default=2160)
    b.add_argument("--pixel", type=int, default=4, help="screen pixels per dither pixel")
    d = sub.add_parser("diff", help="compare a built theme with a published checkout")
    d.add_argument("built", type=Path)
    d.add_argument("published", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "diff":
        added, removed, changed = compare(args.built, args.published)
        for tag, paths in (("A", added), ("D", removed), ("M", changed)):
            for rel in paths:
                print(f"{tag} {rel}")
        raise SystemExit(1 if added or removed or changed else 0)

    for name in args.theme or PUBLISHED:
        c = build_theme(name, args.out, args.width, args.height, args.pixel)
        print(report(name, c))
