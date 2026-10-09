# CLAUDE.md

Source and build tooling for the Athanor Omarchy themes. The published repos
`nacapulque/omarchy-athanor-umber-theme` and `omarchy-athanor-vellum-theme`
(cloned at `~/.config/omarchy/themes/athanor-*`) are **build output**. Never
edit them by hand: change this repo, then publish.

Plan and current status: `docs/PLAN.md`. Start at "Resume here".

## Commands

```sh
git submodule update --init                        # vendor/athanor; needed in every new worktree
python -m athanor_omarchy build [--theme umber]    # into dist/; prints key contrast ratios
uv run --no-project --with pytest pytest           # 157 tests; the build test needs ImageMagick 7
python -m athanor_omarchy diff dist/athanor-umber ~/.config/omarchy/themes/athanor-umber
scripts/publish.sh umber                           # dry run: build and list what would change
scripts/publish.sh umber -m "Subject"              # branch, commit, push and open a PR on the theme repo
scripts/shoot-previews.sh [umber|vellum]           # retake assets/previews/*.png; takes over the screen
python -I scripts/render-plan.py docs/PLAN.md ~/claude-plan.html   # after every plan change
```

## Phase routine

1. `EnterWorktree` with name `phase-N`, which branches `worktree-phase-N` from `origin/main`. Then `git submodule update --init`.
2. Build, test, and verify on screen for anything visual. Commit with explicit paths, push, and open a PR with `--body-file`.
3. CI (`test (3.11)`, `test (3.13)`) must pass: it's required on `main`, alongside PRs only, linear history and admin enforcement.
4. After approval: `gh pr merge N --rebase`, without `--delete-branch`, because the branch is checked out in the worktree.
5. Clean up: `ExitWorktree` keep, then `git pull` and confirm `git diff --stat worktree-phase-N main` is empty. Then `git worktree remove --force` (submodules block a plain remove; check `status --ignored` first), `git branch -D` and `git push origin --delete`.
6. Mark the phase done in `docs/PLAN.md` and re-render the HTML.

## Gotchas

- **The worktree sandbox** refuses complex shell commands (loops with git, `git -C <computed path>`, long inline PR bodies). Use plain commands, files and `--body-file`.
- **`hyprctl dispatch workspace N` silently fails** on this Lua-config Hyprland. Use `hyprctl dispatch 'hl.dsp.focus({ workspace = "N" })'`.
- **Screen-taking scripts** must guard workspace 9 (empty before, every helper on it), close helpers by exact app ID or command line, and restore the workspace and theme on exit. VS Code's window class is `com.microsoft.VSCode`, and its launcher reorders arguments.
- **Screenshots of this desktop** can capture personal windows. Keep them out of commits unless they come from `shoot-previews.sh`, which checks them with OCR.
- **`shell.<section>.toml` replaces its whole section.** Restate every key; `tests/test_shell.py` enforces it against `tests/fixtures/shell.toml.tpl`. `[launcher]` is unread in omarchy 4.0.4, because the menu plugin uses `[menu]`.
- **The user's machine** runs `omapager` and `lock-explorer` instead of Omarchy's notifications and lock, so those sections barely show here.
- **Omarchy snapshots** (`assets/omarchy/`, `tests/fixtures/`) are from omarchy 4.0.4. After an Omarchy update, refresh them, and the tests will show what moved.
- **PNG bytes differ between identical builds** (ImageMagick timestamps). `diff` and `publish.sh` compare PNGs by pixels.

## Conventions

- Contrast floors live in `palette.tune()` and `tests/test_palette.py`. Change both together, and ground any new threshold in data (see the VS Code floor in `tests/test_apps.py`).
- `apps.py` patches must match exactly once, or the build fails. Don't loosen that.
- Commits end with the Co-Authored-By trailer. PR bodies end with the Claude Code line.
