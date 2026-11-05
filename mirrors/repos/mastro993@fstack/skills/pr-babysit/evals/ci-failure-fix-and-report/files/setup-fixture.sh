#!/usr/bin/env bash
# Builds remote.git (the simulated GitHub remote) and repo/ (the user's checkout on the PR branch)
# from fixture/base, fixture/pr, and optional fixture/wip (uncommitted changes), then removes them.
# Optional fixture/base-next becomes refs/stub/base-next on the remote, committed as scenario.json's
# "base_next_title": another PR that the stub lands on the base branch later.
# scenario.json's optional "local_branch" leaves repo/ on that branch instead of the PR's.
set -eu
here=$(pwd)
read_scn() { python3 -c "import json,sys; print(json.load(open('.gh-stub/scenario.json'))[sys.argv[1]])" "$1"; }
base=$(read_scn base); head=$(read_scn head); title=$(read_scn title)
git init -q --bare -b "$base" remote.git
git init -q -b "$base" repo
cp -R fixture/base/. repo/
cd repo
git config user.name "Fede Mastrini"; git config user.email "fede@example.com"
git add -A; git commit -qm "Initial commit"
git remote add origin "$here/remote.git"; git push -q -u origin "$base"
git checkout -q -b "$head"
cp -R ../fixture/pr/. .
git add -A; git commit -qm "$title"; git push -q -u origin "$head"
sha=$(git rev-parse HEAD)
if [ -d ../fixture/base-next ]; then
  git checkout -q --detach "$base"
  cp -R ../fixture/base-next/. .
  git add -A; git commit -qm "$(cd .. && read_scn base_next_title)"; git push -q origin HEAD:refs/stub/base-next
  git checkout -q "$head"
fi
local_branch=$(cd .. && python3 -c "import json; print(json.load(open('.gh-stub/scenario.json')).get('local_branch', ''))")
if [ -n "$local_branch" ]; then git checkout -q "$local_branch"; fi
if [ -d ../fixture/wip ]; then cp -R ../fixture/wip/. .; fi
cd "$here"
python3 - "$sha" <<'PY'
import json, sys
p = ".gh-stub/scenario.json"
s = json.load(open(p)); s["initial_head"] = sys.argv[1]
json.dump(s, open(p, "w"), indent=1)
PY
rm -rf fixture setup-fixture.sh
