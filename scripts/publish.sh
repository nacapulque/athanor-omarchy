#!/bin/bash
# Build one theme and open a PR on its published repo with whatever changed.
#
#   scripts/publish.sh umber                  # build and report; changes nothing
#   scripts/publish.sh umber -m "Subject..."  # also branch, commit, push, open a PR
#
# The theme repo is a clone at $ATHANOR_THEMES_DIR/athanor-<theme>
# (default ~/.config/omarchy/themes). Only files the build changed are copied,
# so PNGs that differ only in their timestamp chunks never show up. Nothing is
# ever pushed to main; the repos' main branches are protected anyway.
set -euo pipefail

theme=${1:?usage: publish.sh <theme> [-m message]}
shift
message=""
while getopts "m:" opt; do
  case $opt in
    m) message=$OPTARG ;;
    *) exit 2 ;;
  esac
done

root=$(cd "$(dirname "$0")/.." && pwd)
repo=${ATHANOR_THEMES_DIR:-$HOME/.config/omarchy/themes}/athanor-$theme
built=$root/dist/athanor-$theme

[[ -d $repo/.git ]] || { echo "No theme repo at $repo" >&2; exit 1; }
[[ -z $(git -C "$repo" status --porcelain) ]] || { echo "$repo has uncommitted changes" >&2; exit 1; }
[[ $(git -C "$repo" branch --show-current) == main ]] || { echo "$repo is not on main" >&2; exit 1; }
git -C "$repo" pull -q --ff-only

(cd "$root" && python -m athanor_omarchy build --theme "$theme" --out dist)

changes=$(cd "$root" && python -m athanor_omarchy diff "$built" "$repo") && {
  echo "athanor-$theme: nothing to publish"
  exit 0
}
echo "$changes"

if [[ -z $message ]]; then
  echo "Dry run. Pass -m \"<commit message>\" to open a PR with these changes."
  exit 0
fi

branch="publish/$(date +%Y%m%d-%H%M%S)"
git -C "$repo" switch -q -c "$branch"
while read -r tag rel; do
  case $tag in
    A | M)
      mkdir -p "$(dirname "$repo/$rel")"
      cp "$built/$rel" "$repo/$rel"
      git -C "$repo" add -- "$rel"
      ;;
    D) git -C "$repo" rm -q -- "$rel" ;;
  esac
done <<<"$changes"

git -C "$repo" commit -q -F - <<<"$message"
git -C "$repo" push -q -u origin "$branch"
body=$(printf '%s\n\nFiles:\n\n```\n%s\n```\n\nBuilt by athanor-omarchy `%s`.' \
  "$(tail -n +3 <<<"$message")" "$changes" "$(git -C "$root" rev-parse --short HEAD)")
gh pr create -R "nacapulque/omarchy-athanor-$theme-theme" --head "$branch" --base main \
  --title "$(head -1 <<<"$message")" --body "$body"
git -C "$repo" switch -q main
