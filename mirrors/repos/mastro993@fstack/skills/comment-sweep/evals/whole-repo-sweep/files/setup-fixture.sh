#!/usr/bin/env bash
# Builds repo/ from fixture/<NN-step>/ in order: each step's files are copied in and committed.
# A step may hold .message (commit message), .branch (check out this new branch first), and
# .delete (paths to remove). fixture/ is removed afterwards.
set -eu
here=$(pwd)
git init -q -b main repo
cd repo
git config user.name "Fede Mastrini"; git config user.email "fede@example.com"
for step in "$here"/fixture/*/; do
  if [ -f "$step.branch" ]; then git checkout -q -b "$(cat "$step.branch")"; fi
  if [ -f "$step.delete" ]; then xargs git rm -q < "$step.delete"; fi
  (cd "$step" && find . -type f ! -name '.message' ! -name '.branch' ! -name '.delete' -print0 | xargs -0 -I{} sh -c 'mkdir -p "$1/$(dirname "$2")" && cp "$2" "$1/$2"' _ "$here/repo" {})
  git add -A
  git commit -qm "$(cat "$step.message")"
done
cd "$here"
rm -rf fixture setup-fixture.sh
