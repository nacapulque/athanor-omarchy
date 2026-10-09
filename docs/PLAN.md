# Athanor for Omarchy: improvement plan

Scope: the two published themes, `athanor-umber` and `athanor-vellum`.
Orpiment, Cinnabar and a custom boot wordmark are out of scope (decided
2026-10-09).

## Where things stand

Both themes are on `main` (Umber `2045a1b`, Vellum `6e613cd`), `main` is
protected (PRs only, linear history), and no PRs are open. Each ships
`colors.toml`, 10 `shell.*.toml` sections, 8 dithered Doré plates plus
`omarchy.png`, previews and a README. Everything else Omarchy generates from
`colors.toml`.

### What the audit found

| # | Finding | Evidence | Severity |
|---|---|---|---|
| 1 | The generator that produces both themes exists only in a session temp folder. The theme repos hold hand-copied output. | `find ~ -name build_athanor.py` finds only the scratchpad copy | High: one lost folder away from un-reproducible themes |
| 2 | Vellum: btop's selected process row is accent on selection at **3.24:1** | generated `btop.theme`: `selected_fg=#7c5510` on `selected_bg=#c2b492` | Medium: the one text pair below 4.5:1 |
| 3 | VS Code: the editor selection blends to **1.13:1** (Umber) and **1.18:1** (Vellum) against the background, and the current-line highlight is invisible on both | Omarchy's template uses `{{ selection_background }}60` and `{{ background }}60` | Medium: selections barely show |
| 4 | `preview.png` on both themes shows the author's hostname, `/home/<user>` paths in btop's process list and the laptop model in fastfetch | the published previews | Medium: privacy, and the screenshots are hard to reproduce |
| 5 | The two READMEs are near-duplicates maintained by hand, and the per-theme facts in them (contrast numbers, hex values) are typed in, not generated | `diff` of the two READMEs | Low: they will drift |
| 6 | Athanor's square, ruled look depends on Hyprland settings an installed theme cannot ship (`hyprland.lua` is dropped), and on bitmap fonts the theme cannot set | `INSTALLED_THEME_DENIED`; `Style.cornerRadius` mirrors Hyprland rounding | Low: document an opt-in instead |
| 7 | `lock.border` (the idle rule) is shipped, but the lock view only draws `border-active` and `border-error` | `plugins/lock/LockView.qml:38-39` | Cosmetic: a dead key with a misleading value |

### What was checked and is fine

- Terminal and herdr: every ANSI color is at least 5.3:1 on the background, 4.5:1 on raised surfaces and 3.5:1 inside a selection. Herdr's active tab is 5.9:1.
- btop on Umber: the selected row is 5.15:1. All other btop and VS Code foregrounds are 5.3:1 or more.
- Shell surfaces: inverted menu rows about 13:1, tooltips 10–11:1. The menu renders as designed on both themes.
- VS Code list selections look low in a raw check, but they're translucent. Blended, the text on them is 9:1 or better.

### Premises verified

1. **Installed themes may ship `btop.theme` and `vscode-theme.json`.** Only `*.lua`, terminal configs and `vscode.json` are dropped (`INSTALLED_THEME_DENIED` in `omarchy-theme-set`). Holds.
2. **The btop and VS Code templates use only plain `{{ key }}` placeholders,** with no `mix` or gradient helpers, so the build can render them from `/usr/share/omarchy/default/themed/` and patch a few keys. Holds.
3. **Intro videos (`backgrounds/intros/*.mp4`).** Documented upstream, but the installed Omarchy is `4.0.0.alpha` and nothing in it reads `intros`. **Fails**, so this is deferred to "Later".

## Phase 0: Source monorepo (about 2–3 h): done

Put the generator under version control and make the two theme repos build
outputs.

**Outcome.** Built as scoped, with these differences:
- The comparison lives in `python -m athanor_omarchy diff`, which `publish.sh` also uses.
- Omarchy's unlock wordmark and logo wallpaper are vendored in `assets/omarchy/`, so the build doesn't need Omarchy installed. CI needs this.
- The hand-taken desktop previews are `assets/previews/<theme>.png` until Phase 3 replaces them.
- `publish.sh` copies only changed files and has a dry-run mode, which runs whenever `-m` isn't given.

Verified: both builds match `main` of their theme repos (text byte-identical, PNGs pixel-identical), `publish.sh` reports "nothing to publish" for both, and a deliberately drifted clone is reported correctly.

**Scope**
- Create `~/Projects/athanor-omarchy` (public repo `nacapulque/athanor-omarchy`), protected `main` like the theme repos.
- Refactor the scratchpad `build_athanor.py` into a small package. Same behavior, no visual changes:
  - `athanor_omarchy/color.py`: hex/OKLCH, `mix`, `contrast`, `push`
  - `palette.py`: `colors()` and `tune()`
  - `shell.py`: `shell_sections()`
  - `wallpapers.py`: plates, lock plate, `omarchy.png`
  - `previews.py`: `preview-unlock`
  - `readme.py`
  - `build.py`: the CLI, `python -m athanor_omarchy build --theme umber --out dist/`
- Pin Athanor as a git submodule at the commit used so far (`vendor/athanor`), the only input for `palette.toml` and the plates.
- `scripts/publish.sh <theme>`: rsync `dist/athanor-<theme>/` into the theme repo clone on a new branch, show `git diff --stat`, push and open a PR. It never pushes to `main`.
- Move this plan into the repo as `docs/PLAN.md`.

**Files**: new repo only. The theme repos are untouched in this phase.

**Acceptance**
- `build` reproduces both themes' current `main`: text files byte-identical, PNGs pixel-identical (`magick compare -metric AE` = 0).
- `publish.sh umber` with no changes reports "nothing to publish".

## Phase 1: Tests and CI (about 1–1.5 h): done

Lock in what this session tuned by hand.

**Outcome.** 143 tests, run in CI on Python 3.11 and 3.13 and required on `main`. Writing them found two issues:
- `[launcher]` set `border-width`, which nothing reads: the menu plugin draws the launcher with `[menu]` tokens. Removed. The theme repos pick this up in Phase 5.
- The first version of the ramp test used an arbitrary 1.3:1 limit for recessed backgrounds. It now requires them to stay quieter than the selection.

Weakening the background floor changed nothing, because it never binds: text that clears 4.5:1 on `lighter_background` already has about 5.3:1 on the background. Weakening the `lighter_background` floor fails 10 tests.

**Scope**
- `pytest` suite:
  - Contrast floors: ANSI on background ≥ 5.0, on `lighter_background` ≥ 4.5, on selection ≥ 3.0; bright vs normal ≥ 1.2; inverted menu ≥ 7; tooltip ≥ 4.5.
  - Ramp order: the neutrals read darkest to lightest (dark theme) or the reverse (light theme).
  - Shell completeness: each `shell.<section>.toml` restates every key in that section of a vendored snapshot of `shell.toml.tpl`, since a section file replaces the whole section.
  - `colors.toml` holds only the canonical keys, in canonical groups.
- GitHub Actions: run the tests on every PR, and add them as a required check on `main`.

**Acceptance**: CI is green, and changing one color to break a floor makes CI fail.

## Phase 2: App contrast fixes (about 1.5 h): done

Fix findings 2, 3 and 7 without touching the palette's identity.

**Outcome.**
- `athanor_omarchy/apps.py` renders the two templates, snapshotted from omarchy 4.0.4 in `assets/omarchy/themed/` so CI doesn't need Omarchy, then applies three exact-match patches.
- A test checks that the unpatched render equals what `omarchy theme set` generated, byte for byte, on both themes.
- On screen, through temporary preview themes:
  - Vellum's btop selected row reads in ink.
  - VS Code selections render opaque: `#393126` on Umber, about 1.46:1.
  - The current line is exactly `lighter_background` on both themes.
- The VS Code visibility floor is 1.25:1, grounded in the 22 stock themes (selection 1.21–2.45:1, median 1.43). Unpublished Cinnabar sits at 1.40.

**Scope**
- Render `btop.theme.tpl` and `vscode-theme.json.tpl` from the Omarchy templates at build time (plain `{{ key }}` substitution, including the derived `selection_background`, `selection_foreground` and `theme_type`), then apply targeted patches:
  - **btop** (Vellum, and Umber for consistency): `selected_fg = foreground` instead of `accent`. Text on the selected row rises to 8.48:1 (Vellum) and 8.85:1 (Umber), and the selection keeps its own color.
  - **VS Code**: an opaque `editor.selectionBackground = selection`, and `editor.lineHighlightBackground = lighter_background`. Blended selection visibility rises from about 1.15 to about 1.5:1 against the background, and the current line shows.
- Add contrast tests for both pairs, and drop the dead `lock.border` value. The template key stays, but it gets the same value as `border-active`, so nothing reads misleadingly.

**Rejected alternatives (measured)**
- Darkening Vellum's accent to `#643f00` fixes btop (4.54:1) but darkens every amber border and the bar's identity.
- Lifting Umber's selection globally only gets VS Code to 1.27:1, and drops terminal text on selection below 3:1.

**Files**: per theme, new `btop.theme`, `vscode-theme.json` and `shell.lock.toml`, plus tests.

**Acceptance**
- The tests pass.
- Applied with `omarchy theme set`: the btop selected row is readable on Vellum, and a VS Code selection and current line are visible on both, checked with screenshots.
- `hyprctl configerrors` is clean.

## Phase 3: Reproducible, private previews (about 1 h): done

Fix finding 4.

**Outcome.** `scripts/shoot-previews.sh` replaced both previews.
- The OCR check covers `$USER`, the hostname, `/home/` and the DMI product name and version.
- Two runs gave identical window geometry.
- Changes from the scope:
  - The third pane also lists Athanor's source tree with plain `ls`. Its history is only 3 commits, and `ls -l` would print the owner's username.
  - fastfetch's logo and keys use ANSI yellow, so they follow each theme instead of fastfetch's built-in lime.
  - fastfetch's shell and terminal lines were dropped: it reads both from its parent processes, which the script controls.

**Scope**
- `scripts/shoot-previews.sh`, the guarded version from this session:
  - focuses an empty workspace 9 and aborts if any helper window lands elsewhere
  - closes its helpers by PID and returns to your previous workspace
  - uses Lua `hl.dsp.focus`, since `hyprctl dispatch workspace` doesn't work with your config
- Neutral content:
  - Neovim with Athanor's `planetary.c`
  - fastfetch with a bundled config that hides host, user, model and disk
  - a pane with colored `git log` and a palette strip instead of btop's process list
- Output `preview.png` at 1800×1012, as before.

**Acceptance**: no hostname, username, home path or hardware model appears in either preview (checked by eye and with OCR via `tesseract`, if installed). Running the script twice gives the same layout.

## Phase 4: Docs and opt-in extras (about 1 h)

Fix findings 5 and 6.

**Scope**
- READMEs rendered from one template in `readme.py`, with every number and hex value read from the built palette and the test results, never typed in.
- A new "Make it feel like Athanor" README section with opt-in snippets the user pastes into their own config. The theme still ships no code:
  - `~/.config/hypr/looknfeel.lua`: square corners (`rounding = 0`) and `border_size = 2`. The shell copies Hyprland's rounding, so menus go square too.
  - a pixel font, e.g. Terminus or Cozette via `omarchy font set`, with the install line
  - note that replacement notification or lock plugins (e.g. `omapager`, `lock-explorer`) draw themselves
- The source repo's README explains how to build, test and publish.

**Acceptance**: the READMEs build from the template, and `publish.sh` shows README-only diffs. Each snippet is applied once by hand on this machine and works: `hyprctl configerrors` is clean, then the change is reverted.

## Phase 5: Publish (about 30 min)

**Scope**
- `publish.sh umber` and `publish.sh vellum` open one PR per theme repo with Phases 2–4.
- Rebase-merge after review, then `omarchy theme update` locally and re-apply.

**Acceptance**: both PRs pass, merge, and a fresh `omarchy theme install` of each repo applies cleanly.

## Later (not in this plan)

- **Intro videos**: once Omarchy ships intro support, a 5–7 s clip per plate where the dither "develops" from noise into the engraving (ImageMagick frames into ffmpeg).
- **Orpiment and Cinnabar**: with Phases 0–1 in place, publishing them is `build` plus `publish`.
- **Omarchy theme gallery**: submit once the previews are clean.

## Assumptions

- You want the theme repos to stay lean, with no build tooling in what users clone.
- Rendering the btop and VS Code templates at build time is acceptable, even though it ties our files to the Omarchy version present when we build. The tests catch missing keys if the templates change.
- GitHub Actions minutes for a small public repo are fine.
