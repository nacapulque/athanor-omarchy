"""Map Athanor's palette.toml onto Omarchy's colors.toml roles, then tune contrast."""

import tomllib

from .color import contrast, mix, push
from .paths import ATHANOR

PALETTE = tomllib.loads((ATHANOR / "src/athanor/palette.toml").read_text())

# Per-theme facts Athanor's palette doesn't carry.
THEMES = {
    "umber": {"mode": "dark", "stage": "nigredo", "gloss": "the blackening", "icons": "Yaru-wartybrown",
              "tagline": "Lamplight amber on soot-brown ground.", "companion": "vellum"},
    "vellum": {"mode": "light", "stage": "albedo", "gloss": "the whitening", "icons": "Yaru-wartybrown",
               "tagline": "Iron-gall ink on parchment.", "companion": "umber"},
    "orpiment": {"mode": "light", "stage": "citrinitas", "gloss": "the yellowing", "icons": "Yaru-yellow",
                 "tagline": "", "companion": None},
    "cinnabar": {"mode": "dark", "stage": "rubedo", "gloss": "the reddening", "icons": "Yaru-red",
                 "tagline": "", "companion": None},
}  # fmt: skip

# colors.toml layout: Omarchy's canonical semantic-first groups.
GROUPS = [
    ["mode"],
    ["accent", "selection", "muted"],
    ["background", "dark_background", "darker_background", "lighter_background"],
    ["foreground", "dark_foreground", "light_foreground", "bright_foreground"],
    ["red", "yellow", "orange", "green", "cyan", "blue", "magenta", "brown"],
    ["bright_red", "bright_yellow", "bright_green", "bright_cyan", "bright_blue", "bright_magenta"],
    ["hyprland_active_border", "hyprland_inactive_border"],
]

HUES = ["red", "green", "yellow", "blue", "magenta", "cyan"]
TEXT = [*HUES, "muted"]


def colors(name):
    """Athanor's palette in Omarchy's roles, before contrast tuning."""
    p, light = PALETTE[name], THEMES[name]["mode"] == "light"
    a, bg = p["ansi"], p["bg"]
    if light:
        dark_bg, darker_bg, lighter_bg = mix(bg, p["border"], 0.25), mix(bg, p["border"], 0.5), mix(bg, p["border"], 0.4)
        brown, bright_fg = mix(a[3], p["fg"], 0.4), p["fg"]
    else:
        dark_bg, darker_bg, lighter_bg = mix(bg, "#000000", 0.3), mix(bg, "#000000", 0.5), mix(bg, p["border"], 0.5)
        brown, bright_fg = mix(a[3], bg, 0.55), a[15]
    return {
        "mode": THEMES[name]["mode"],
        "accent": p["active"],
        "selection": p["border"],
        "muted": p["dim"],
        "background": bg,
        "dark_background": dark_bg,
        "darker_background": darker_bg,
        "lighter_background": lighter_bg,
        "foreground": p["fg"],
        "dark_foreground": mix(p["dim"], bg, 0.3),
        "light_foreground": mix(p["fg"], p["dim"], 0.4),
        "bright_foreground": bright_fg,
        "red": a[1],
        "yellow": a[3],
        "orange": mix(a[1], a[3], 0.5),
        "green": a[2],
        "cyan": a[6],
        "blue": a[4],
        "magenta": a[5],
        "brown": brown,
        "bright_red": a[9],
        "bright_yellow": a[11],
        "bright_green": a[10],
        "bright_cyan": a[14],
        "bright_blue": a[12],
        "bright_magenta": a[13],
        "hyprland_active_border": f"rgb({p['active'][1:]})",
        "hyprland_inactive_border": f"rgb({p['border'][1:]})",
    }


# Athanor guarantees 4.5:1 against bg only. Terminal text also lands on
# lighter_background (editor cursorlines, herdr and Helix panels) and inside
# the selection, so each text color's lightness is nudged until it clears
# those surfaces too.
def tune(c):
    c = dict(c)
    light = c["mode"] == "light"
    away = "dark" if light else "light"
    if light:
        # Lift the selection toward the page until all text reads on it, keeping it visible.
        sel, t = c["selection"], 0.0
        while t < 0.6 and min(contrast(c[k], sel) for k in TEXT) < 3.0:
            t += 0.02
            sel = mix(c["selection"], c["background"], t)
        c["selection"] = sel
    floors = [(c["background"], 5.0), (c["lighter_background"], 4.5), (c["selection"], 3.0)]
    for k in TEXT:
        c[k] = push(c[k], floors, away)
    for k in HUES:
        c["bright_" + k] = push(c["bright_" + k], [*floors, (c[k], 1.2)], away)
    c["dark_foreground"] = push(c["dark_foreground"], [(c["background"], 3.0)], away)
    return c


def theme_colors(name):
    return tune(colors(name))


def colors_toml(name, c):
    label = PALETTE[name]["label"]
    body = f"# Athanor {label} ({THEMES[name]['stage']}), from script-wizards/athanor palette.toml\n"
    for group in GROUPS:
        body += "\n" + "".join(f'{k} = "{c[k]}"\n' for k in group)
    return body
