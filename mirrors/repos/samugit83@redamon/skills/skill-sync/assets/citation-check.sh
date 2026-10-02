#!/usr/bin/env bash
#
# citation-check.sh - advisory. Print which SKILL.md / AGENTS.md files cite a
# path that this change touches, so you know you may have just invalidated a
# rule. It NEVER blocks and ALWAYS exits 0.
#
# Two modes, same grep, opposite intent:
#     citation-check.sh                 -> staged changes (git diff --cached)
#                                          used by the pre-commit hook
#     citation-check.sh <git-range>     -> that range (e.g. master...HEAD)
#                                          used by hand at branch-review time
#
# With no argument and nothing staged it prints nothing - that is correct.
#
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../../.." && pwd))"
cd "$REPO_ROOT" || exit 0

# --- changed file list -----------------------------------------------------
if [ "$#" -ge 1 ] && [ -n "$1" ]; then
  changed="$(git diff --name-only "$1" 2>/dev/null)"
else
  changed="$(git diff --cached --name-only 2>/dev/null)"
fi
[ -n "$changed" ] || exit 0

# The rule sources we grep. Skills first (payload), then AGENTS.md (always-loaded).
# Filter AGENTS.md by basename: git's '*' spans '/', so '*AGENTS.md' would also
# match README.FOO_AGENTS.md.
RULEFILES=()
while IFS= read -r rf; do
  [ -n "$rf" ] || continue
  case "$rf" in
    *AGENTS.md) [ "$(basename "$rf")" = "AGENTS.md" ] || continue ;;
  esac
  RULEFILES+=("$rf")
done < <(git ls-files --cached --others --exclude-standard 'skills/*/SKILL.md' '*AGENTS.md' 2>/dev/null)
[ "${#RULEFILES[@]}" -gt 0 ] || exit 0

emitted=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  # skip the rule system's own files and prose documentation - editing those is
  # not what "you may have invalidated a rule" is about.
  case "$f" in
    skills/*|docs/*|_local/*|redamon.wiki/*|.github/*) continue ;;
  esac
  base="$(basename "$f")"
  # a citation matches on the full repo path OR the bare basename
  for rf in "${RULEFILES[@]}"; do
    if grep -qF -- "$f" "$rf" 2>/dev/null || grep -qF -- "$base" "$rf" 2>/dev/null; then
      if [ "$emitted" -eq 0 ]; then
        echo "[skill-citation-check] changed files cited by a skill or AGENTS.md:"
        emitted=1
      fi
      printf '  %-45s cited in %s\n' "$f" "${rf#$REPO_ROOT/}"
    fi
  done
done <<< "$changed"

if [ "$emitted" -eq 1 ]; then
  echo "[skill-citation-check] advisory only - review whether a rule needs updating (this never blocks the commit)."
fi
exit 0
