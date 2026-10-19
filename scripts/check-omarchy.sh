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
