#!/usr/bin/env bash
#
# drift-audit.sh - detection, no model. For every path cited by every SKILL.md
# AND every AGENTS.md, check the path still resolves. Prints the dead ones.
#
# AGENTS.md citations matter MORE than skill citations: an AGENTS.md is always
# in context, so a stale path there misleads every agent on every task. They
# are reported first and flagged [AGENTS].
#
# Flag:
#     --skill <name>   audit only skills/<name>/SKILL.md
#
# Exit: 0 when every citation resolves, 1 when any is dead (so cron/CI can tell).
#
# ---------------------------------------------------------------------------
# CONFIGURE HERE: component roots, relative to the repository root. Skills cite
# paths relative to a COMPONENT root, not the repo root, so a citation counts
# as live if it resolves under the citing file's own dir, the repo root, OR any
# root below. Leave this wrong and the audit floods with false positives.
# ---------------------------------------------------------------------------
ROOTS=(
  "."                    # repository root
  "webapp"               # scope: webapp
  "agentic"              # scope: agentic
  "recon"                # scope: recon
  "recon_orchestrator"   # scope: recon_orchestrator
  "scanners/capture_proxy"        # scope: capture_proxy
  "scanners/supply_chain_scan"    # scope: supply_chain (dir)
  "scanners/supply_chain_common"  # supply_chain shared lib
  "scanners/supply_chain_analyzer" # supply_chain analyzer
)
# ---------------------------------------------------------------------------

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../../.." && pwd))"

ONLY_SKILL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --skill) shift; ONLY_SKILL="${1:-}" ;;
    -h|--help) sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "drift-audit.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

# --- files to audit --------------------------------------------------------
FILES=()
if [ -n "$ONLY_SKILL" ]; then
  f="$REPO_ROOT/skills/$ONLY_SKILL/SKILL.md"
  [ -f "$f" ] || { echo "no such skill: skills/$ONLY_SKILL/SKILL.md" >&2; exit 2; }
  FILES=("$f")
else
  shopt -s nullglob
  for f in "$REPO_ROOT"/skills/*/SKILL.md; do FILES+=("$f"); done
  # every AGENTS.md tracked in the repo (basename must be exactly AGENTS.md:
  # git's '*' spans '/', so '*AGENTS.md' would also match README.FOO_AGENTS.md)
  while IFS= read -r a; do
    [ -n "$a" ] && [ "$(basename "$a")" = "AGENTS.md" ] && FILES+=("$REPO_ROOT/$a")
  done < <(git -C "$REPO_ROOT" ls-files --cached --others --exclude-standard '*AGENTS.md' 2>/dev/null)
fi

# --- extract citations from one file --------------------------------------
# Emits "<origin><TAB><token>": origin L = markdown link ](target) (an explicit
# citation, always audited); origin B = backticked token (audited only if it is
# path-shaped, i.e. contains a "/", so bare identifiers in prose like `.py` or
# `sync.sh` are not mistaken for dead paths).
extract_citations() {
  awk '
    {
      line=$0
      s=line
      while (match(s, /\]\([^)]+\)/)) {
        print "L\t" substr(s, RSTART+2, RLENGTH-3)
        s=substr(s, RSTART+RLENGTH)
      }
      s=line
      while (match(s, /`[^`]+`/)) {
        print "B\t" substr(s, RSTART+1, RLENGTH-2)
        s=substr(s, RSTART+RLENGTH)
      }
    }
  ' "$1"
}

# does a candidate look like a repo path we can check? $1 token, $2 origin (L/B)
is_path_like() {
  case "$1" in
    http://*|https://*|mailto:*|\#*) return 1 ;;         # urls / anchors
    /*) return 1 ;;                                       # absolute -> HTTP endpoint (/defaults) or abs path, not a repo citation
    *" "*) return 1 ;;                                    # has a space -> prose/command
    *[{}\<\>\*\$,]*) return 1 ;;                          # placeholder/brace/glob -> illustrative, not a real path
    *:*) return 1 ;;                                      # colon -> volume spec (host:container), host:port, not a repo path
  esac
  # backticked tokens must be path-shaped (contain a slash); links are explicit.
  if [ "$2" = "B" ]; then
    case "$1" in */*) : ;; *) return 1 ;; esac
  fi
  return 0
}

# resolve a candidate against the citing file's dir, then every ROOT, then repo root
resolves() {
  local cand="$1" fdir="$2" p="${1%%#*}"        # strip a trailing #anchor
  p="${p%\)}"                                     # stray close paren
  [ -n "$p" ] || return 0
  [ -e "$fdir/$p" ] && return 0
  local r base
  for r in "${ROOTS[@]}"; do
    if [ "$r" = "." ]; then base="$REPO_ROOT"; else base="$REPO_ROOT/$r"; fi
    [ -e "$base/$p" ] && return 0
    # also try the basename under the root (skills cite files by short path)
    [ -e "$base/$(basename "$p")" ] && return 0
  done
  [ -e "$REPO_ROOT/$p" ] && return 0
  return 1
}

# --- audit -----------------------------------------------------------------
agents_dead=()
skill_dead=()
checked=0
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  fdir="$(dirname "$f")"
  rel="${f#$REPO_ROOT/}"
  case "$rel" in *AGENTS.md) is_agents=1 ;; *) is_agents=0 ;; esac
  while IFS=$'\t' read -r origin cand; do
    [ -n "$cand" ] || continue
    is_path_like "$cand" "$origin" || continue
    checked=$((checked+1))
    if ! resolves "$cand" "$fdir"; then
      if [ "$is_agents" -eq 1 ]; then
        agents_dead+=("$rel -> $cand")
      else
        skill_dead+=("$rel -> $cand")
      fi
    fi
  done < <(extract_citations "$f" | sort -u)
done

# --- report ----------------------------------------------------------------
dead=$(( ${#agents_dead[@]} + ${#skill_dead[@]} ))
echo "drift-audit: ${#FILES[@]} file(s), $checked citation(s) checked."
if [ "$dead" -eq 0 ]; then
  echo "OK - every cited path resolves."
  exit 0
fi
if [ "${#agents_dead[@]}" -gt 0 ]; then
  echo
  echo "[AGENTS] dead citations (always in context - fix first):"
  printf '  %s\n' "${agents_dead[@]}"
fi
if [ "${#skill_dead[@]}" -gt 0 ]; then
  echo
  echo "[skills] dead citations:"
  printf '  %s\n' "${skill_dead[@]}"
fi
exit 1
