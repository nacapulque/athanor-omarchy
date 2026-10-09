"""Omarchy shell section overrides (shell.<section>.toml) in Athanor's look.

Athanor's own UI is flat and opaque: square cards, a solid amber rule, and
the selected row drawn in inverse (ink on paper) like its quit prompt and
--More-- prompt. Each section file replaces that whole section of the
generated shell.toml, so every key the template defines is restated.
"""


def bar_section(p):
    return (
        "[bar]\n"
        f'background       = "{p["bar"]}"\n'
        "background-alpha = 1.0\n"
        f'text             = "{p["barfg"]}"\n'
        f'active           = "{p["bar_warn"]}"\n'
        "scale-with-font  = true\n"
        "size-horizontal  = 26\n"
        "size-vertical    = 28\n"
    )


def shell_sections(p, c):
    bg, fg, accent, red, muted = c["background"], c["foreground"], c["accent"], c["red"], c["muted"]
    return {
        "controls": f"""normal-color        = "{fg}"
normal-fill-alpha   = 0.04
normal-border       = "{fg}"
normal-border-width = 1
normal-border-alpha = 0.4

hover-cursor-color        = "{fg}"
hover-cursor-fill-alpha   = 0.08
hover-cursor-border       = "{fg}"
hover-cursor-border-width = 1
hover-cursor-border-alpha = 0.4

# Keyboard focus gets the amber rule so it never hides behind hover.
focus-color        = "{fg}"
focus-fill-alpha   = 0.08
focus-border       = "{accent}"
focus-border-width = 1
focus-border-alpha = 1.0

# Chosen items read in inverse, ink on paper.
selected-color        = "{fg}"
selected-fill-alpha   = 0.18
selected-border       = "{accent}"
selected-border-width = 1
selected-border-alpha = 1.0

pressed-fill-alpha   = 0.22
selection-fill-alpha = 0.35
""",
        "popups": f"""background       = "{bg}"
background-alpha = 1.0
text             = "{fg}"
border           = "{accent}"
border-alpha     = 1.0
border-width     = 2
""",
        "tooltip": f"""# Tooltips speak in the status line's colors.
background       = "{p['bar']}"
background-alpha = 1.0
text             = "{p['barfg']}"
border           = "{p['border']}"
border-alpha     = 1.0
""",
        "notifications": f"""background       = "{bg}"
background-alpha = 1.0
text             = "{fg}"
border           = "{accent}"
border-alpha     = 1.0
border-width     = 2
countdown        = "{accent}"
""",
        "launcher": f"""background                = "{bg}"
background-alpha          = 1.0
text                      = "{fg}"
border                    = "{accent}"
border-alpha              = 1.0
scrim                     = "{bg}"
scrim-alpha               = 0.6
selected-background       = "{fg}"
selected-background-alpha = 1.0
selected-text             = "{bg}"
selected-border           = "{fg}"
selected-border-alpha     = 0.0
""",
        "menu": f"""background                = "{bg}"
background-alpha          = 1.0
text                      = "{fg}"
border                    = "{accent}"
border-alpha              = 1.0
border-width              = 2
scrim                     = "{bg}"
scrim-alpha               = 0.6
selected-background       = "{fg}"
selected-background-alpha = 1.0
selected-text             = "{bg}"
selected-border           = "{fg}"
selected-border-alpha     = 0.0
""",
        "polkit": f"""background       = "{bg}"
background-alpha = 1.0
text             = "{fg}"
text-error       = "{red}"
border           = "{accent}"
border-error     = "{red}"
border-alpha     = 1.0
border-width     = 2
scrim            = "{bg}"
scrim-alpha      = 0.75
accent           = "{accent}"
""",
        "lock": f"""# An opaque card over the blurred plate, ruled in amber and red when the
# word is wrong. The shell draws only border-active and border-error.
background       = "{bg}"
background-alpha = 1.0
text             = "{fg}"
placeholder      = "{muted}"
text-error       = "{red}"
border           = "{muted}"
border-active    = "{accent}"
border-error     = "{red}"
border-alpha     = 1.0
border-width     = 2
selection        = "{accent}"
selection-alpha  = 0.45
""",
        "image-picker": f"""scrim                   = "{bg}"
scrim-alpha             = 0.8
text                    = "{fg}"
selected-border         = "{accent}"
selected-border-alpha   = 1.0
unselected-border       = "{fg}"
unselected-border-alpha = 0.28
""",
    }
