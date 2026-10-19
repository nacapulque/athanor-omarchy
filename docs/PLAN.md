# Athanor for Omarchy: improvement plan

Scope: the two published themes, `athanor-umber` and `athanor-vellum`.
Orpiment, Cinnabar and a custom boot wordmark are out of scope (decided
2026-10-09). The review that produced Phases 4–7 is `docs/REVIEW.md`
(2026-10-18, against omarchy 4.0.5-1).

## Resume here (2026-10-18)

**Done:** Phases 0–4 are merged. Phase 5 is
[PR #6](https://github.com/nacapulque/athanor-omarchy/pull/6), waiting on
Raúl's review and merge; its branch `worktree-phase-5` is checked out in
`.claude/worktrees/phase-5`.

**Next, in order:**
1. Merge PR #6 with rebase and clean up (see "Phase routine" in `CLAUDE.md`).
2. Phase 6: README template and the opt-in section.
3. Phase 7: publish both themes.

**The theme repos haven't changed since this plan started** (Umber `2045a1b`,
Vellum `6e613cd`). Phase 7 publishes everything below in one PR per repo.

| File | Change | From |
|---|---|---|
| `btop.theme`, `vscode-theme.json` | added | Phase 2 |
| `shell.launcher.toml` | removed (nothing reads it) | Phase 4 |
| `shell.lock.toml` | idle border matches the accent | Phase 2 |
| `colors.toml` (Vellum) | accent `#764f06`, inactive border `rgb(c2b492)` | Phase 4 |
| `backgrounds/*.png` (Vellum) | plate ink `#a49b88` | Phase 4 |
| `preview.png` | private screenshot with the menu open | Phases 3 and 5 |
| `README.md` | new files, measured numbers, opt-in section | Phases 2–6 |

## How to run a phase (instructions for the executor)

These phases are written for a Claude Sonnet 5.5 session. Follow them
literally; where a step says "expected", compare the real output with it and
stop if they differ. Never improvise a number: every ratio and hex value is
produced by a command in the step.

**Ground rules**
- Never edit `~/.config/omarchy/themes/athanor-*`. They are build output.
- Never commit to `main`. One PR per phase; wait for Raúl's approval before
  merging and before starting the next phase.
- Stage files by explicit path. Never `git add -A` or `git add .`.
- Commit messages end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  PR bodies end with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
  Write the PR body to a file and pass `--body-file`; the worktree sandbox
  rejects long inline bodies.
- `hyprctl dispatch workspace N` fails silently here. Use
  `hyprctl dispatch 'hl.dsp.focus({ workspace = "9" })'`.
- The user's shell runs `omapager` and `lock-explorer` instead of Omarchy's
  notifications and lock, so those two surfaces can't be checked on screen.

**Start of every phase**
```sh
# 1. From the main checkout, with main up to date:
git -C ~/Projects/athanor-omarchy pull --ff-only
# 2. EnterWorktree with name phase-N (branch worktree-phase-N from origin/main), then:
git submodule update --init
uv run --no-project --with pytest pytest -q      # expected: all pass (157 before Phase 4)
python -m athanor_omarchy build                  # expected: two "athanor-…:" report lines, dist/ populated
```

**On-screen check with a temporary theme** (used by Phases 4 and 6; never
leave it installed):
```sh
prev=$(omarchy theme current)
rm -rf ~/.config/omarchy/themes/athanor-vellum-preview
cp -r dist/athanor-vellum ~/.config/omarchy/themes/athanor-vellum-preview
omarchy theme set athanor-vellum-preview
# … look / grim … then always:
omarchy theme set "$prev"
rm -rf ~/.config/omarchy/themes/athanor-vellum-preview
```
Screenshots go in the session scratchpad, never in the repo, unless they come
from `scripts/shoot-previews.sh`.

**End of every phase**
```sh
uv run --no-project --with pytest pytest -q
git status --short                               # only the files the phase names
git add <explicit paths> && git commit && git push -u origin worktree-phase-N
gh pr create --title "Phase N: …" --body-file /tmp/claude-1000/…/pr-body.md
gh pr checks --watch                             # expected: test (3.11) and test (3.13) pass
```
Then update the "Resume here" section above, re-render the plan with
`python -I scripts/render-plan.py docs/PLAN.md ~/claude-plan.html`, commit that
too, and stop. Raúl merges.

## Phases 0–3: done

**Phase 0, source monorepo.** The generator became the package
`athanor_omarchy` with `build`, `diff` and `scripts/publish.sh`. Both builds
reproduced the theme repos' `main` byte for byte (PNGs pixel for pixel).
Omarchy's unlock art is vendored in `assets/omarchy/` so CI needs no Omarchy.

**Phase 1, tests and CI.** 143 tests then, on Python 3.11 and 3.13, required
on `main`: contrast floors (text ≥ 5.0 on background, ≥ 4.5 on
`lighter_background`, ≥ 3.0 on selection; bright vs normal ≥ 1.2), ramp order,
shell completeness against the vendored `shell.toml.tpl`, canonical
`colors.toml` keys.

**Phase 2, app contrast.** `apps.py` renders Omarchy's btop and VS Code
templates (snapshotted from 4.0.4, still identical in 4.0.5) and patches three
lines: btop's selected row in foreground, VS Code's selection opaque and its
current line in `lighter_background`. The lock's dead `border` key got the
accent so it never misleads.

**Phase 3, private previews.** `scripts/shoot-previews.sh` retakes both
`preview.png` on workspace 9 with neutral content and refuses to save a shot
that OCRs to the username, hostname, a home path or the hardware model.

The audit tables these phases answered are in git history
(`git show d8d5b03:docs/PLAN.md`).

## Phase 4: Palette and shell fixes (about 2 h): in PR #5

Review items Fix 1–3, Improve 4 and 6, and the two hygiene items. Vellum
changes visibly: accent one step darker, plates one step darker, no dead
launcher file. Umber's output must not change except for the missing file.

**Outcome.** Built as written; every "expected" line in 4.2 and 4.7 matched.
Two things the steps didn't foresee:
- `build_theme()` never removed files it stopped emitting, so the first
  `diff` still showed `M shell.launcher.toml` from the previous build. It now
  deletes stale `shell.*.toml` first, and `tests/test_build.py` checks that.
- The accent-on-bar assertion (4.3) fails for Orpiment, whose inverted dark
  bar puts its accent at 2.27:1. It is scoped to the published themes; the
  unpublished pair needs its own pass ("Later").
- Changing the accent also changes the seven Vellum `shell.*.toml` that carry
  it, so Phase 7's expected list for Vellum includes them.
163 tests pass. On screen, through a temporary theme: the menu card and the
active window border show the new amber, the plate reads at the window
edges, `hyprctl configerrors` is empty.

### 4.1 Freeze the app fixtures' colors

`tests/test_apps.py::test_render_matches_omarchy` renders the templates with
today's colors and compares with files `omarchy theme set` generated in
Phase 2. Changing Vellum's accent would break it for the wrong reason. Pin
the fixtures to the colors they were generated from.

```sh
python -m athanor_omarchy build
diff dist/athanor-umber/colors.toml  ~/.config/omarchy/themes/athanor-umber/colors.toml   # expected: no output
diff dist/athanor-vellum/colors.toml ~/.config/omarchy/themes/athanor-vellum/colors.toml  # expected: no output
cp ~/.config/omarchy/themes/athanor-umber/colors.toml  tests/fixtures/omarchy-generated/umber/colors.toml
cp ~/.config/omarchy/themes/athanor-vellum/colors.toml tests/fixtures/omarchy-generated/vellum/colors.toml
```

In `tests/test_apps.py`, add `import tomllib` and change the test to render
from the pinned file:

```python
def test_render_matches_omarchy(name, template):
    """Before our patches, the renderer reproduces Omarchy's own output byte for byte,
    given the colors.toml those files were generated from."""
    colors = tomllib.loads((GENERATED / name / "colors.toml").read_text())
    tpl = (apps.TEMPLATES / f"{template}.tpl").read_text()
    assert apps.render(tpl, colors) == (GENERATED / name / template).read_text()
```

Run the tests: expected all pass, nothing else changed yet.

### 4.2 Palette: accent floor, derived borders, Vellum plate ink

In `athanor_omarchy/palette.py`:

1. After `PALETTE = tomllib.loads(...)`, add the override and apply it:
```python
# Per-theme values that differ from Athanor's palette.toml on purpose.
# Vellum's desk plates were 1.49:1 ink on paper, half of Umber's 2.26:1;
# this ink is paper mixed 35% toward the foreground, 2.12:1 (docs/REVIEW.md, Improve 4).
OVERRIDES = {"vellum": {"wall_desk": ["#a49b88", "#ece1c6"]}}
for _name, _values in OVERRIDES.items():
    PALETTE[_name].update(_values)
```
2. In `tune()`, after the `for k in HUES:` loop and before `dark_foreground`,
   add the accent floor:
```python
    # Accent is text on raised panels (Helix, herdr, btop headers) and on the bar.
    c["accent"] = push(c["accent"], [(c["background"], 4.5), (c["lighter_background"], 4.5)], away)
```
3. At the end of `tune()`, before `return c`, derive the Hyprland borders from
   the tuned colors instead of the raw palette:
```python
    c["hyprland_active_border"] = f"rgb({c['accent'][1:]})"
    c["hyprland_inactive_border"] = f"rgb({c['selection'][1:]})"
```
   Leave the two lines in `colors()` as they are; `tune()` overwrites them.

Check the effect before writing tests:
```sh
python - <<'PY'
from athanor_omarchy.palette import theme_colors, PALETTE
for n in ("umber", "vellum"):
    c = theme_colors(n)
    print(n, c["accent"], c["hyprland_active_border"], c["hyprland_inactive_border"], PALETTE[n]["wall_desk"])
PY
```
Expected, exactly:
```
umber #d49a3a rgb(d49a3a) rgb(3a3126) ['#16120e', '#5c4c39']
vellum #764f06 rgb(764f06) rgb(c2b492) ['#a49b88', '#ece1c6']
```
If Vellum's accent is anything other than `#764f06`, stop and report.

### 4.3 Palette tests

In `tests/test_palette.py`:

- Extend `test_accent_and_dim_text`:
```python
    assert contrast(c["accent"], c["lighter_background"]) >= 4.5
```
- Add:
```python
def test_hyprland_borders_follow_the_tuned_colors(theme):
    _, c = theme
    assert c["hyprland_active_border"] == f"rgb({c['accent'][1:]})"
    assert c["hyprland_inactive_border"] == f"rgb({c['selection'][1:]})"


def test_vellum_plate_ink_is_quieter_than_umber_but_visible():
    """Review Improve 4: both desk plates sit between 2.0 and 2.4:1 ink on paper."""
    for name in ("umber", "vellum"):
        ink, paper = PALETTE[name]["wall_desk"]
        assert 2.0 <= contrast(ink, paper) <= 2.4, name
```
- Also assert the bar: in `test_bar_and_tooltip`, add
  `assert contrast(theme_colors(name)["accent"], p["bar"]) >= 4.5`.

### 4.4 Shell: drop `[launcher]`, fix the lock comment

In `athanor_omarchy/shell.py`:
- Delete the whole `"launcher": f"""…"""` entry from `shell_sections()`.
- Replace the `[lock]` comment with:
```
# An opaque card over the blurred plate. The shell draws border-active while
# idle and typing, border-error after a wrong word; `border` is parsed but
# never drawn, and border-width reaches the card through border-active.
```

In `tests/test_shell.py`:
- Rewrite the `READS_BORDER_WIDTH` comment's last sentence to:
  `# [launcher] is not emitted at all: nothing in the shell reads it (omarchy 4.0.5).`
- Add a guard that runs where Omarchy is installed and is skipped in CI:
```python
SHELL_QML = Path("/usr/share/omarchy/shell")


@pytest.mark.skipif(not SHELL_QML.exists(), reason="needs an installed Omarchy")
def test_launcher_section_is_still_unread():
    """We stopped shipping shell.launcher.toml because no QML reads launcher.*.
    If this fails after an Omarchy update, bring the section back in shell.py."""
    hits = [p for p in SHELL_QML.rglob("*.qml") if re.search(r"\blauncher\.[a-z-]+", p.read_text())]
    assert hits == [], hits
```
  Before adding it, run the search by hand and read any hit:
  `rg -n '\blauncher\.[a-z-]+' /usr/share/omarchy/shell --glob '*.qml'`.
  Expected: no output. If something unrelated matches (a plugin id, a route),
  narrow the regex to that section's token style and say so in the comment.

### 4.5 Snapshot check script

Create `scripts/check-omarchy.sh`, executable:
```sh
#!/bin/bash
# Compare the vendored Omarchy templates with the installed ones.
# Run after `omarchy update`. Exit 1 if anything moved.
set -u
root=$(cd "$(dirname "$0")/.." && pwd)
installed=/usr/share/omarchy/default/themed
[[ -d $installed ]] || { echo "Omarchy isn't installed here" >&2; exit 2; }
rc=0
for pair in "assets/omarchy/themed/btop.theme.tpl:btop.theme.tpl" \
            "assets/omarchy/themed/vscode-theme.json.tpl:vscode-theme.json.tpl" \
            "tests/fixtures/shell.toml.tpl:shell.toml.tpl"; do
  ours=${pair%%:*}; theirs=${pair##*:}
  if diff -q "$root/$ours" "$installed/$theirs" >/dev/null; then
    echo "same     $ours"
  else
    echo "CHANGED  $ours  (see: diff $root/$ours $installed/$theirs)"; rc=1
  fi
done
echo "omarchy $(pacman -Q omarchy 2>/dev/null | cut -d' ' -f2)"
exit $rc
```
Run it: expected three `same` lines and `omarchy 4.0.5-1`.

### 4.6 Docs in this repo

- `CLAUDE.md`: test count in the Commands block (read it from the pytest
  summary); the `shell.<section>.toml` gotcha now says `[launcher]` isn't
  emitted; the snapshots gotcha says "from omarchy 4.0.4, unchanged in 4.0.5;
  run `scripts/check-omarchy.sh` after an update".
- `README.md` (source repo): add `scripts/check-omarchy.sh` to the Test
  section and the Layout table.
- `athanor_omarchy/readme.py`: no change yet (Phase 6 rewrites the numbers).

### 4.7 Build and verify

```sh
uv run --no-project --with pytest pytest -q                    # expected: all pass
python -m athanor_omarchy build
ls dist/athanor-vellum/shell.*.toml | wc -l                     # expected: 9
grep -c . dist/athanor-vellum/shell.launcher.toml 2>&1 | head -1 # expected: No such file
grep -E '^(accent|hyprland_inactive_border)' dist/athanor-vellum/colors.toml
# expected: accent = "#764f06"  and  hyprland_inactive_border = "rgb(c2b492)"
magick dist/athanor-vellum/backgrounds/1-merlin-and-the-king.png -format %c histogram:info:- | sed 's/.*#/#/' | cut -c1-7 | sort -u
# expected: exactly #A49B88 and #ECE1C6
python -m athanor_omarchy diff dist/athanor-umber ~/.config/omarchy/themes/athanor-umber
# expected: A btop.theme, A vscode-theme.json, D shell.launcher.toml, M shell.lock.toml, M README.md, M preview.png — nothing else
```

On screen, with the temporary Vellum theme (see "How to run a phase"): the
bar's clock and the active-module color, the first plate on workspace 1, and
`omarchy menu summon` for the menu card. `grim` one shot of each to the
scratchpad and look at them. Then restore the theme. Run
`hyprctl configerrors`: expected empty.

### 4.8 Deliver

Files: `athanor_omarchy/palette.py`, `athanor_omarchy/shell.py`,
`tests/test_palette.py`, `tests/test_shell.py`, `tests/test_apps.py`,
`tests/fixtures/omarchy-generated/*/colors.toml`, `scripts/check-omarchy.sh`,
`CLAUDE.md`, `README.md`, `docs/PLAN.md`.

PR title: `Phase 4: palette and shell fixes from the review`. Body: the three
fixes with their before/after ratios from 4.2 and 4.3, the plate ink change,
and the `diff` output from 4.7.

**Acceptance**
- Tests pass on 3.11 and 3.13.
- The `python -` check in 4.2 prints the expected two lines.
- `dist/athanor-umber/colors.toml` is byte-identical to the published one.
- Screenshots show the new accent on the bar and the darker plate on Vellum.

## Phase 5: Previews that show the shell (about 1 h): in PR #6

Review Improve 5. The current previews never show a shell surface, and the
Neovim pane is mostly empty. Needs the desktop; it can't run in CI.

**Outcome.** Built as written. The menu appeared within the 1.5 s wait on
both runs, both shots passed the OCR guard, and the layout JSON is the same
one Phase 3 recorded. The previews now carry Phase 4's colors too (Vellum's
accent on the menu rule, the darker plate ink). Took about 20 s per theme.

### 5.1 Script changes

In `scripts/shoot-previews.sh`:
1. Stage a second file: after the `cp … planetary.c` line add
   `cp "$root/vendor/athanor/README.md" "$stage/"`.
2. Open Neovim with both files side by side:
   `foot --app-id "$app" -D "$stage" nvim -O planetary.c README.md 2>/dev/null &`
3. After the three-pane guard passes and before `grim`, open the menu:
```sh
    omarchy menu summon >/dev/null 2>&1
    sleep 1.5
```
   and after `grim`, close it: `omarchy menu close >/dev/null 2>&1`.
   Also call `omarchy menu close` in `cleanup()` so an abort never leaves it
   open.
4. The menu is a layer surface, not a client, so the helper count stays 3; do
   not change that guard.

### 5.2 Run and check

```sh
scripts/shoot-previews.sh vellum      # takes over the screen for ~20 s
scripts/shoot-previews.sh umber
```
Expected: two `saved assets/previews/<theme>.png` lines, the layout JSON the
same for both, no `ABORT`. Open both PNGs and check: the menu card is visible
in the middle, Neovim shows two columns, and nothing personal is readable (the
script's OCR already refused anything in its list; read the image anyway).

If the menu doesn't appear within 1.5 s, raise the sleep to 3 and re-run; if
it still doesn't, stop and report with the raw shot kept in `dist/previews/`.

### 5.3 Docs

- `athanor_omarchy/readme.py`: alt text becomes
  `Athanor {label} desktop with the Omarchy menu, Neovim, fastfetch and the terminal palette`.
- `README.md` (source): the Previews paragraph mentions the menu card.

### 5.4 Deliver

Files: `scripts/shoot-previews.sh`, `assets/previews/umber.png`,
`assets/previews/vellum.png`, `athanor_omarchy/readme.py`, `README.md`,
`docs/PLAN.md`. PR title: `Phase 5: previews that show the shell`.

**Acceptance**: both PNGs are 1800×1012 (`magick identify`), both show the
menu, two consecutive runs give the same layout JSON, tests pass.

## Phase 6: README template and opt-in extras (about 1.5 h)

Review items Opt-in 7–10 and the old Phase 4 scope. The README is rendered by
`athanor_omarchy/readme.py`; every number in it is computed.

### 6.1 Measured numbers

In `readme.py`, replace the hard-coded floors paragraph ("at least 5:1 …",
"Body text is above 12:1") with values computed from `c`:

```python
from .color import contrast
from .palette import TEXT
...
    floor = lambda surface: min(contrast(c[k], c[surface]) for k in TEXT)
    body = contrast(c["foreground"], c["background"])
```
and render:
```
- at least {floor("background"):.1f}:1 on the background
- at least {floor("lighter_background"):.1f}:1 on raised surfaces, such as editor cursorlines and herdr or Helix panels
- at least {floor("selection"):.1f}:1 inside a selection

Body text is {body:.1f}:1.
```
Expected after Phase 4: Umber 5.3 / 4.5 / 3.6 and 12.9; Vellum 5.1 / 4.5 /
3.2 and 13.4 (run `python -m athanor_omarchy build` and read `dist/*/README.md`).

### 6.2 The opt-in section

Add a `## Make it feel like Athanor` section after "Wallpapers", with this
content (keep the wording; fill nothing in by hand):

- Intro: Omarchy already draws square corners with 2px borders, which is most
  of Athanor's frame. The rest is yours to opt into; the theme ships no code.
- **Quieter motion.** In `~/.config/hypr/looknfeel.lua`:
  ```lua
  hl.config({ animations = { enabled = false } })
  ```
- **Opaque terminals.** Omarchy draws every window at 0.985 opacity, and on a
  light theme the plate shows through. In `looknfeel.lua`:
  ```lua
  o.window({ tag = "terminal" }, { opacity = "1 1" })
  ```
- **Denser shell.** `~/.config/omarchy/shell.toml` overrides single keys on
  top of any theme:
  ```toml
  [spacing]
  scale = 0.9
  [font]
  base-size = 13
  ```
- **Bitmap fonts.** `omarchy font set` with Terminus or Cozette
  (`omarchy pkg add terminus-font` or `ttf-cozette`). Athanor's own Px437
  faces also need its fontconfig snippet, which turns antialiasing off; link
  `vendor/athanor/config/fontconfig/60-athanor.conf`.
- Note that replacement notification or lock plugins (`omapager`,
  `lock-explorer`) draw themselves and ignore the theme's shell sections.

Before writing the numbers for the shell snippet, try them: put the four
lines in `~/.config/omarchy/shell.toml` (back it up first; it currently holds
`[font] base-size = 12`), look at the bar and a menu, and keep whichever of
`0.9`/`13` or `0.85`/`12` reads closest to a 24px bar. Restore the backup.

Apply each other snippet once in `looknfeel.lua`, run `hyprctl configerrors`
(expected empty), look, and revert.

### 6.3 Tests and docs

- `tests/test_readme.py`: add an assertion that the README contains
  `## Make it feel like Athanor` and the string `o.window({ tag = "terminal" }`.
- The "What's in it" table in `readme.py` loses nothing; `shell.*.toml` is
  now nine files, which the table doesn't count.
- Source `README.md`: nothing new.

### 6.4 Deliver

Files: `athanor_omarchy/readme.py`, `tests/test_readme.py`, `docs/PLAN.md`.
PR title: `Phase 6: README from measured numbers, with the opt-in section`.

**Acceptance**: tests pass; `scripts/publish.sh vellum` (dry run) lists
`README.md` among the changes; each snippet was applied and reverted with a
clean `hyprctl configerrors`.

## Phase 7: Publish (about 45 min)

### 7.1 Dry runs

```sh
scripts/publish.sh umber
scripts/publish.sh vellum
```
Expected Umber: `A btop.theme`, `A vscode-theme.json`, `D shell.launcher.toml`,
`M README.md`, `M preview.png`, `M shell.lock.toml`. Expected Vellum: the same
plus `M colors.toml`, `M backgrounds/1-…png` through `7-…png` (the lock
plate `8-satans-despair.png` keeps its own ink and must not appear), and
`M shell.controls.toml`, `shell.image-picker.toml`, `shell.menu.toml`,
`shell.notifications.toml`, `shell.polkit.toml`, `shell.popups.toml`, which
carry the accent. Anything else: stop and report.

### 7.2 Open the PRs

```sh
scripts/publish.sh umber -m "Athanor Umber: app fixes, private preview, README

btop and VS Code themes with readable selections, a preview without personal
details, the dead shell.launcher.toml removed, and a README with measured
contrast and the opt-in section."
scripts/publish.sh vellum -m "Athanor Vellum: accent and plate contrast, app fixes, README

Accent #764f06 (4.5:1 on raised panels and the bar), desk plates at 2.1:1 ink
on paper, btop and VS Code themes with readable selections, a preview without
personal details, the dead shell.launcher.toml removed, and a README with
measured contrast and the opt-in section."
```
Each prints a PR URL. Wait for Raúl to merge both (rebase).

### 7.3 After the merges

```sh
omarchy theme update                       # pulls both clones
omarchy theme set athanor-vellum; sleep 3; hyprctl configerrors    # expected empty
omarchy theme set athanor-umber;  sleep 3; hyprctl configerrors    # expected empty
tmp=$(mktemp -d); git clone -q https://github.com/nacapulque/omarchy-athanor-umber-theme "$tmp/umber"
python -m athanor_omarchy diff dist/athanor-umber "$tmp/umber"; echo "exit $?"   # expected: exit 0
```
Repeat the clone check for Vellum. Then record the new theme-repo commits in
"Resume here", re-render the plan, and open a last PR with only `docs/PLAN.md`.

**Acceptance**: both theme PRs merged; both `diff` checks exit 0; both themes
apply with a clean `hyprctl configerrors`.

## Later (not in this plan)

- **Intro videos**: stock themes already ship `backgrounds/intros/*.mp4`, but
  omarchy 4.0.5 doesn't read them. Once it does: a 5–7 s clip per plate where
  the dither develops from noise into the engraving.
- **Orpiment and Cinnabar**: `build` plus `publish`, after a contrast pass.
- **Omarchy theme gallery**: submit once Phase 7 is merged.

## Assumptions

- The theme repos stay lean: no build tooling in what users clone.
- Rendering the btop and VS Code templates at build time is acceptable;
  `scripts/check-omarchy.sh` and the tests catch template drift.
- GitHub Actions minutes for a small public repo are fine.
