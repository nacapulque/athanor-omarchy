#!/bin/bash
# Take each theme's preview.png on a real desktop, without personal details.
#
#   scripts/shoot-previews.sh                 # umber and vellum
#   scripts/shoot-previews.sh vellum
#
# Each build is applied as a temporary user theme (athanor-<theme>-preview), and
# three panes open on an empty workspace 9: Neovim with Athanor's planetary.c,
# fastfetch limited to software, and Athanor's git history with the palette.
# The screenshot is OCR'd, and it's only saved to assets/previews/<theme>.png
# when no username, hostname, home path or hardware model shows up in it.
# Your workspace and theme are restored on exit, whatever happens.
#
# Needs Hyprland with Lua config, foot, nvim, fastfetch, grim, tesseract and
# ImageMagick 7. Takes over the screen for about 20 seconds per theme.
set -u

root=$(cd "$(dirname "$0")/.." && pwd)
themes_dir=$HOME/.config/omarchy/themes
stage=/tmp/athanor-preview
out=$root/dist/previews
app=athanor-preview
orig_ws=$(hyprctl activeworkspace -j | jq -r .id)
orig_theme=$(omarchy theme current)

focus() { hyprctl dispatch "hl.dsp.focus({ workspace = \"$1\" })" >/dev/null; }
helpers() { hyprctl clients -j | jq -c --arg a "$app" '[.[] | select(.class == $a)]'; }
close_helpers() {
  for pid in $(helpers | jq -r '.[].pid'); do
    [[ $(tr '\0' ' ' </proc/"$pid"/cmdline 2>/dev/null) == "foot --app-id $app"* ]] && kill "$pid"
  done
  for _ in $(seq 20); do [[ $(helpers | jq length) == 0 ]] && break; sleep 0.25; done
}
cleanup() {
  close_helpers
  omarchy theme set "$orig_theme" >/dev/null 2>&1
  rm -rf "$themes_dir"/athanor-*-preview "$stage"
  focus "$orig_ws"
}
trap cleanup EXIT
fail() { echo "ABORT: $*" >&2; exit 1; }

# What must never appear in a published screenshot.
private=("$USER" "$(hostname)" "/home/")
for f in /sys/class/dmi/id/product_name /sys/class/dmi/id/product_version; do
  [[ -r $f && -n $(<"$f") ]] && private+=("$(<"$f")")
done

mkdir -p "$stage" "$out"
cp "$root/vendor/athanor/docs/screenshots/planetary.c" "$stage/"

for theme in "${@:-umber vellum}"; do
  for t in $theme; do
    echo "== athanor-$t"
    (cd "$root" && python -m athanor_omarchy build --theme "$t" --out dist >/dev/null) || fail "build failed"
    rm -rf "$themes_dir/athanor-$t-preview"
    cp -r "$root/dist/athanor-$t" "$themes_dir/athanor-$t-preview"
    omarchy theme set "athanor-$t-preview" >/dev/null 2>&1
    sleep 3

    focus 9; sleep 0.5
    [[ $(hyprctl activeworkspace -j | jq -r .id) == 9 ]] || fail "workspace 9 isn't focused"
    [[ $(hyprctl activeworkspace -j | jq -r .windows) == 0 ]] || fail "workspace 9 isn't empty"

    foot --app-id "$app" -D "$stage" nvim planetary.c 2>/dev/null &
    sleep 1.5
    # fastfetch reads the terminal from its parent process, so foot runs it directly.
    foot --app-id "$app" -D "$stage" --hold fastfetch --config "$root/assets/preview/fastfetch.jsonc" 2>/dev/null &
    sleep 1.5
    foot --app-id "$app" -D "$stage" bash "$root/assets/preview/pane.sh" "$root/vendor/athanor" 2>/dev/null &
    sleep 5

    [[ $(helpers | jq 'length == 3 and all(.[]; .workspace.id == 9)') == true ]] || fail "helper windows aren't all on workspace 9"
    [[ $(hyprctl activeworkspace -j | jq -r .id) == 9 ]] || fail "focus moved off workspace 9"
    grim "$out/$t-raw.png" || fail "grim failed"
    helpers | jq -c 'sort_by(.at[0], .at[1]) | map({at, size})' >"$out/$t-layout.json"
    close_helpers

    tesseract "$out/$t-raw.png" "$out/$t-ocr" >/dev/null 2>&1 || fail "tesseract failed"
    leaks=()
    for word in "${private[@]}"; do
      grep -qiF -- "$word" "$out/$t-ocr.txt" && leaks+=("$word")
    done
    ((${#leaks[@]} == 0)) || fail "$t screenshot shows: ${leaks[*]} (kept at $out/$t-raw.png)"

    magick "$out/$t-raw.png" -filter Lanczos -resize 1800x1012! -colors 256 "PNG8:$root/assets/previews/$t.png"
    echo "saved assets/previews/$t.png (layout: $(<"$out/$t-layout.json"))"
  done
done
