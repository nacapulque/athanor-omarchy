"""Wallpapers, logo art and previews, rendered with ImageMagick 7."""

import math
import subprocess
import tomllib
from pathlib import Path

from .color import mix
from .paths import OMARCHY_UNLOCK, OMARCHY_WALLPAPER, PLATES_DIR

PLATES = tomllib.loads((PLATES_DIR / "plates.toml").read_text())
# The Omarchy wallpaper and unlock art are drawn on Miasma's #222222 ground.
OMARCHY_GROUND = "srgb(34,34,34)"


def magick(*args):
    subprocess.run(["magick", *map(str, args)], check=True)


def size(path):
    out = subprocess.run(["magick", "identify", "-format", "%w %h", str(path)], capture_output=True, text=True, check=True)
    return tuple(map(int, out.stdout.split()))


def inset_box(dims, inset):
    pw, ph = dims
    left, top, right, bottom = inset or (0, 0, 0, 0)
    return round(pw * (1 - left - right)), round(ph * (1 - top - bottom)), round(pw * left), round(ph * top)


def dither(contrast, ink, paper):
    return ["-sigmoidal-contrast", contrast, "-dither", "FloydSteinberg", "-monochrome", "+level-colors", f"{ink},{paper}"]


def plate_names():
    """Filenames of the backgrounds, in order: each level plate, then the lock plate."""
    levels = [f"{n}-{Path(lv['file']).stem}.png" for n, lv in enumerate(PLATES["level"], start=1)]
    return [*levels, f"{len(levels) + 1}-{Path(PLATES['lock']['file']).stem}.png"]


# Mirrors athanor/wall.py: render on a 1/pixel grid, dither, then point-scale up so pixels stay crisp.
def backgrounds(p, out, width, height, pixel):
    lw, lh = math.ceil(width / pixel), math.ceil(height / pixel)
    out.mkdir(parents=True, exist_ok=True)
    names = plate_names()
    for name, level in zip(names, PLATES["level"]):
        plate = PLATES_DIR / level["file"]
        bw, bh, bx, by = inset_box(size(plate), level.get("inset"))
        k = max(lw / bw, lh / bh)
        sw, sh = math.ceil(bw * k), math.ceil(bh * k)
        fx, fy = level["focus"]
        ax, ay = level["anchor"]
        ox = round(min(max(fx * sw - ax * lw, 0), sw - lw))
        oy = round(min(max(fy * sh - ay * lh, 0), sh - lh))
        magick(
            plate, "-colorspace", "gray", "-crop", f"{bw}x{bh}+{bx}+{by}", "+repage",
            "-gamma", level.get("gamma", 1.0), "-resize", f"{sw}x{sh}!",
            "-crop", f"{lw}x{lh}+{ox}+{oy}", "+repage", *dither(level["contrast"], *p["wall_desk"]),
            "-filter", "point", "-resize", f"{lw * pixel}x{lh * pixel}!", "-crop", f"{width}x{height}+0+0", "+repage",
            out / name,
        )  # fmt: skip

    # The lock plate: the engraving on the left, plain ground on the right.
    lock = PLATES["lock"]
    plate = PLATES_DIR / lock["file"]
    bw, bh, bx, by = inset_box(size(plate), lock.get("inset"))
    plate_w = min(round(bw * lh / bh), round(lw * 0.6))
    magick(
        "-size", f"{lw}x{lh}", f"xc:{p['bg']}",
        "(", plate, "-colorspace", "gray", "-crop", f"{bw}x{bh}+{bx}+{by}", "+repage",
        "-resize", f"{plate_w}x{lh}^", "-gravity", "center", "-extent", f"{plate_w}x{lh}",
        *dither(lock["contrast"], *p["wall_lock"]), ")",
        "-gravity", "west", "-composite", "-filter", "point", "-resize", f"{lw * pixel}x{lh * pixel}!",
        out / names[-1],
    )  # fmt: skip


def logo_wallpaper(p, out):
    magick(OMARCHY_WALLPAPER, "-fill", p["active"], "+opaque", OMARCHY_GROUND, "-fill", p["bg"], "-opaque", OMARCHY_GROUND, out)


def unlock(p, out):
    magick(OMARCHY_UNLOCK, "-fill", p["active"], "-colorize", "100", out)


def preview_unlock(c, unlock_png, out):
    """A mock of the Plymouth unlock screen: the wordmark, a padlock and a password field."""
    bg, fg = c["background"], c["foreground"]
    field = mix(bg, fg, 0.04)
    magick(
        "-size", "1920x1080", f"xc:{bg}",
        unlock_png, "-geometry", "+560+446", "-composite",
        "-fill", field, "-stroke", fg, "-strokewidth", "2", "-draw", "rectangle 818,675 1101,720",
        "-stroke", "none", "-fill", fg,
        "-draw", "circle 841,697 841,700", "-draw", "circle 853,697 853,700",
        "-draw", "circle 865,697 865,700", "-draw", "circle 877,697 877,700",
        "-draw", "roundrectangle 769,694 801,717 3,3",
        "-fill", "none", "-stroke", fg, "-strokewidth", "5", "-draw", "arc 773,679 797,705 180,360",
        "-draw", "line 773,692 773,695", "-draw", "line 797,692 797,695",
        "-stroke", "none", "-fill", bg, "-draw", "roundrectangle 783,700 787,710 2,2",
        out,
    )  # fmt: skip
