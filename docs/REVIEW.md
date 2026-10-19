# Athanor for Omarchy: review against Omarchy 4.0.5

Date: 2026-10-18. Scope: `athanor-umber` and `athanor-vellum`, as built from
this repo's `main` (`d8d5b03`) plus PR #4. Orpiment and Cinnabar stay out of
scope. Nothing here is applied, committed or published; it is a proposal.

Every contrast ratio below was computed from `athanor_omarchy.palette.theme_colors`
with `color.contrast` (WCAG). Shell facts come from `/usr/share/omarchy/shell`
and `/usr/bin/omarchy-theme-set*` at omarchy 4.0.5-1.

## Where things stand

- Phases 0–2 are merged. Phase 3 (private previews) is PR #4: CI green,
  mergeable, not merged; its worktree is still on disk.
- Omarchy is 4.0.5-1 on this machine. The three vendored templates
  (`shell.toml.tpl`, `btop.theme.tpl`, `vscode-theme.json.tpl`) are
  byte-identical to the installed ones. No snapshot refresh is needed.
- `vendor/athanor` is at `ad24b16`, which is upstream `main` and tag `v0.2.0`.
- Intro videos: the stock themes now ship `backgrounds/intros/*.mp4`, but
  nothing in 4.0.5 reads them. Support looks close; still "Later".

## Architecture facts that matter to the generator

| Fact | Evidence | Consequence |
|---|---|---|
| A `shell.<section>.toml` replaces its whole section; missing keys fall back to the QML defaults, not the template | `omarchy-theme-set-templates:309-358` | Keep restating every key (already enforced by `tests/test_shell.py`) |
| `[launcher]` is read by nothing; the launcher draws with `[menu]` | no `launcher.` reference in `shell/` | `shell.launcher.toml` is dead weight (Fix 1) |
| `lock.border` is parsed but never drawn; `LockView` uses `border-active` when idle and `border-error` on failure. `lock.border-width` works through the `border-active` fallback | `Color.qml:120`, `LockView.qml:38-40`, `Border.qml:112` | Current values are right; the comment in `shell.py` is wrong (Improve 6) |
| The template has 13 sections: `hyprland`, `spacing` and `font` are new and accepted from any theme | `shell.toml.tpl`, splicer accepts `[A-Za-z0-9_-]+` | Opt-in density and type scale (Opt-in 7) |
| Templating has helpers: `mix A B N%`, `*_strip`, `*_rgb`, `hypr_gradient`, `shell_gradient` | `omarchy-theme-set-templates:195-291` | `apps.py` only renders plain keys and raises on anything else: correct, needs one test |
| Repo-installed themes lose only `*.lua`, `alacritty.toml`, `foot.ini`, `ghostty.conf`, `kitty.conf`, `vscode.json` | `omarchy-theme-set:30,142` | Everything we ship survives install; square corners and fonts stay opt-in |
| Nine more app configs are generated from `colors.toml`: `claude.json`, `pi.json`, `t3code.json`, `hermes.yaml`, `obsidian.css`, `chromium.theme`, `keyboard.rgb`, `gum_env.lua`, `hyprland.lua` | `default/themed/` | Free coverage; nothing to ship. `keyboard.rgb` = accent, consumed by ASUS ROG and Framework 16 scripts |
| `cursor` is always `bright_foreground`; `mode` decides GTK, Chromium, VS Code, Claude and t3code light/dark. Neovim has no mode switch; aether reads the background | `omarchy-theme-color:225,279` | Vellum's Neovim renders correctly without a `neovim.lua` (checked in the Phase 3 preview) |
| There is no theme manifest; the display name is the directory in title case | `omarchy-theme-list:9` | Nothing to add |

## Fix

### 1. `shell.launcher.toml` does nothing

Nothing in the shell reads `launcher.*`. Phase 1 removed its `border-width`
but kept the file. Drop `shell.launcher.toml` from `shell_sections()` and the
completeness test, and add a test that fails the day the vendored shell
snapshot gains a `launcher.` reference, so the file comes back when it means
something.

Files: `athanor_omarchy/shell.py`, `tests/test_shell.py`.

### 2. Vellum's accent is below 4.5:1 on raised surfaces

| Accent | on background | on `lighter_background` | on selection | on bar |
|---|---|---|---|---|
| current `#7c5510` | 5.11 | **4.13** | 3.24 | **4.33** |
| proposed `#764f06` | 5.59 | 4.52 | 3.55 | 4.74 |

Accent is text on `lighter_background` in Helix and herdr panels, btop's
headers and VS Code's current line, and on the bar for the clock and active
modules. `#764f06` is Vellum's own tuned `yellow`, one step darker (1.09:1 from
the current accent), so the amber identity stays. Phase 2 rejected `#643f00`,
which is much darker. Apply with `push()` in `tune()` against a new floor
`(lighter_background, 4.5)` for accent, and add the test.

Files: `athanor_omarchy/palette.py`, `tests/test_palette.py`.

### 3. Vellum's inactive window border ignores the selection tuning

`colors()` writes `hyprland_inactive_border` from the raw Athanor border
(`#b9aa86`), and `tune()` later lifts `selection` to `#c2b492`. Inactive
window frames and the selection no longer agree. Umber is unaffected because
its selection isn't tuned. Derive both Hyprland border keys at the end of
`tune()` from the tuned `accent` and `selection`.

Files: `athanor_omarchy/palette.py`, `tests/test_palette.py`.

## Improve

### 4. Vellum's desk plates are too faint

| Plate ink on paper `#ece1c6` | ratio |
|---|---|
| Umber, for reference (`#5c4c39` on `#16120e`) | 2.26 |
| Vellum current `#c8b994` | **1.49** |
| candidate `#aea591` | 1.88 |
| candidate `#a49b88` (recommended) | 2.12 |
| candidate `#9a917f` | 2.40 |

On screen the Vellum engraving reads as parchment texture; next to Umber the
pair is unbalanced. The HTML review shows the four renders side by side.
`#a49b88` is `mix(paper, foreground, 0.35)`, so it stays in the palette's
family.

This also softens a second effect: Omarchy's default terminal opacity lets
the plate ghost through windows. On Umber the ink equals the background, so it
is invisible; on Vellum it shows (visible in the Phase 3 preview, and in the
stock flexoki-light preview, so it's platform behaviour). A quieter ink doesn't
remove the ghost; the opt-in note in 10 does.

Files: `vendor/athanor` palette is the source for `wall_desk`; override it in
`athanor_omarchy/palette.py` (`THEMES["vellum"]["wall_desk"]`) rather than
patching the submodule.

### 5. Previews should show the shell

The Phase 3 shots are private and reproducible, but the Neovim pane is mostly
empty and no shell surface is visible. The shell styling is what sets these
themes apart from a plain `colors.toml` theme. Proposal for
`scripts/shoot-previews.sh`: three denser panes plus the Omarchy menu card (or
a notification) open, same workspace-9 and OCR guards. Needs a dry run per
theme on this machine before Phase 3 is published.

Files: `scripts/shoot-previews.sh`, `assets/preview/`.

### 6. Lock section comment

`shell.py` documents `lock.border` as the idle rule. It isn't: idle uses
`border-active`. Keep the values (they already give `border-active` the
accent), fix the comment, and state that `border-width` reaches the lock card
through the `border-active` fallback.

Files: `athanor_omarchy/shell.py`.

## Opt-in (README section "Make it feel like Athanor", Phase 4)

These stay out of the theme. The README gives a snippet, where it goes, and
how to undo it.

7. **Density and type scale.** `~/.config/omarchy/shell.toml` overrides
   individual keys on top of any theme. Athanor's bar is 24px with a 16px
   bitmap face; a starting point is `[spacing] scale = 0.9` and
   `[font] base-size = 13`. Measure on screen before quoting numbers.
8. **Quieter motion.** Omarchy's default `looknfeel.lua` already has
   `rounding = 0`, `border_size = 2`, shadow and blur off, so the frame is
   Athanor's out of the box (checked 2026-10-18). What's left from Athanor's
   `hyprland.lua` is `animations.enabled = false`, one line in
   `~/.config/hypr/looknfeel.lua`.
9. **Bitmap fonts.** `omarchy font set` with Terminus or Cozette. The Px437 and
   PxPlus faces Athanor uses need its fontconfig snippet (antialias off,
   `rgba none`) to draw as bitmaps.
10. **Opaque terminals.** Omarchy tags every window `default-opacity` and
    draws it at 0.985/0.96 (`default/hypr/windows.lua:25`). User rules load
    later, so `o.window({ tag = "terminal" }, { opacity = "1 1" })` in
    `looknfeel.lua` keeps the plate from ghosting through on Vellum.

## Keep as is

- All contrast floors hold on 4.0.5: every text color ≥ 5.33:1 (Umber) and
  ≥ 5.11:1 (Vellum) on the background, ≥ 4.5:1 on `lighter_background`,
  ≥ 3.24:1 in a selection. Body text 12.93:1 and 13.38:1.
- Shell cards: 2px accent rule, radius 0, opaque, inverse selection. This
  matches Athanor's own fuzzel, mako and hyprlock templates line for line
  (border 2, radius 0, selection = fg on bg, prompt and match in `active`).
- `[controls]` gives keyboard focus the accent rule and selected items a 1px
  accent border. Omarchy's default makes hover and focus identical; ours is
  better for keyboard users.
- Bars: Umber's is 1.05:1 darker than windows, Vellum's 1.18:1, with 11.05:1
  and 9.99:1 text. Both echo Athanor's waybar.
- `hyprland_active_border` is solid. Omarchy's `hypr_gradient` helper accepts
  a solid, and a gradient would contradict the flat look.
- Umber `yellow == accent` (Athanor's design), `dark_foreground` at exactly
  3.0:1 on both (stock themes run 3.4–3.5), `brown` 2.45:1 on Umber (aether
  marks brown deprecated). Notes, not changes.
- `apps.py` raises on any placeholder it doesn't know, so a template that
  starts using `mix` fails the build instead of shipping `{{ mix ... }}`. Add
  one test that asserts this.
- Snapshot hygiene: add `scripts/check-omarchy.sh` that diffs
  `assets/omarchy/themed/*.tpl` and `tests/fixtures/shell.toml.tpl` against
  `/usr/share/omarchy/default/themed/`, to run after `omarchy update`.

## Proposed Phase 6 (to append to `docs/PLAN.md` after approval)

**Phase 6: Review follow-ups (about 2 h).** Fixes 1–3 and Improve 4 and 6,
with tests, in one PR; Improve 5 folds into Phase 3's script before Phase 5
publishes; Opt-in 7–10 join Phase 4's README section. Acceptance: tests pass
on 3.11 and 3.13; Vellum applied through a temporary preview theme shows the
new accent on the bar and a Helix panel, and the new plate ink on workspace 1;
`publish.sh vellum` lists `colors.toml`, `backgrounds/*.png`, `shell.lock.toml`
and the removed `shell.launcher.toml`.
