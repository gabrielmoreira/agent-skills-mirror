# Helpers for each case's build.sh, which builds remote.git (the simulated GitHub remote) and
# repo/ (the user's checkout) commit by commit. Sourced from the sandbox root.
set -eu
ROOT=$(pwd)

# start_repo BRANCH: an empty repo on BRANCH with origin at remote.git; cd into it.
start_repo() {
  git init -q --bare -b "$1" "$ROOT/remote.git"
  git init -q -b "$1" "$ROOT/repo"
  cd "$ROOT/repo"
  git config user.name "Fede Mastrini"; git config user.email "fede@example.com"
  git remote add origin "$ROOT/remote.git"
}

# put PATH: writes stdin to PATH in the repo, creating directories.
put() { mkdir -p "$(dirname "$1")"; cat > "$1"; }

# commit MSG [PR]: commits everything, as part of pull request PR when given (its commits list
# in .gh-stub/github.json gets the SHA, so `gh api .../commits/<sha>/pulls` finds it).
commit() {
  git add -A
  git commit -qm "$1"
  if [ $# -gt 1 ]; then
    python3 - "$ROOT/.gh-stub/github.json" "$2" "$(git rev-parse HEAD)" <<'PY'
import json, sys
path, n, sha = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = json.load(open(path))
next(p for p in d["pulls"] if p["number"] == n).setdefault("commits", []).append(sha)
json.dump(d, open(path, "w"), indent=1)
PY
  fi
}
