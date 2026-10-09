#!/bin/bash
# The third preview pane: Athanor's own git history, then the palette as the
# terminal draws it. It never shows a shell prompt, which would name the user.
# usage: pane.sh <athanor checkout>
athanor=$1
printf '\e[?25l'
git -C "$athanor" --no-pager log --graph --decorate --color=always --format='%C(yellow)%h%C(auto)%d %Creset%s' -14
echo
# Plain ls: a long listing would print the owner's username.
(cd "$athanor" && ls --color=always -F -w 70 . src/athanor)
echo
names=(black red green yellow blue magenta cyan white)
for i in 0 1 2 3 4 5 6 7; do printf '\e[3%dm%-9s' "$i" "${names[$i]}"; done
printf '\e[0m\n'
for i in 0 1 2 3 4 5 6 7; do printf '\e[9%dm%-9s' "$i" "bright"; done
printf '\e[0m\n\n'
for i in 0 1 2 3 4 5 6 7; do printf '\e[4%dm         ' "$i"; done
printf '\e[0m\n'
for i in 0 1 2 3 4 5 6 7; do printf '\e[10%dm         ' "$i"; done
printf '\e[0m\n'
exec sleep infinity
