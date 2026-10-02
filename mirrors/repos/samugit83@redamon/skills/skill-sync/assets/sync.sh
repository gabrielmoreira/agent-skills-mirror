#!/usr/bin/env bash
#
# sync.sh - compile every skill's routing declaration into the generated
#           "### Auto-invoke Skills" tables inside the AGENTS.md files.
#
# Source of truth is each skills/*/SKILL.md frontmatter:
#     name                 -> the skill name printed in the table
#     metadata.scope       -> which AGENTS.md(s) receive the rows
#     metadata.auto_invoke -> one table row per entry (string OR list)
#
# The table is a BUILD ARTIFACT. Never hand-edit it; edit the skill and re-run.
# A skill missing scope OR auto_invoke is SKIPPED and listed at the end under
# "missing sync metadata" - it is never silently dropped.
#
# Flags:
#     --dry-run        show what would change, write nothing
#     --scope <name>   only regenerate that one scope's AGENTS.md
#
# ---------------------------------------------------------------------------
# CONFIGURE HERE: scope name -> directory holding that scope's AGENTS.md,
# relative to the repository root. "root" is the repository root itself.
# Add a line when you add a scope (and create that dir's AGENTS.md).
# ---------------------------------------------------------------------------
declare -A SCOPE_DIRS=(
  [root]="."
  [webapp]="webapp"
  [agentic]="agentic"
  [recon]="recon"
  [recon_orchestrator]="recon_orchestrator"
  [capture_proxy]="scanners/capture_proxy"
  [supply_chain]="scanners/supply_chain_scan"
)
# ---------------------------------------------------------------------------

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/../../.." && pwd))"
SKILLS_DIR="$REPO_ROOT/skills"

MARKER="### Auto-invoke Skills"
INTRO="When performing these actions, ALWAYS invoke the corresponding skill FIRST:"

DRY_RUN=0
ONLY_SCOPE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --scope)   shift; ONLY_SCOPE="${1:-}" ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "sync.sh: unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

# --- frontmatter value extractor ------------------------------------------
# Prints the value(s) of a frontmatter key, one per line, RAW (quotes/space
# not stripped). Handles: scalar (key: v), inline array (key: [a, b]) and
# block list (key:\n  - a\n  - b). Keys are matched at any indent, so
# metadata.scope / metadata.auto_invoke resolve by their unique key names.
fm_values() {
  awk -v key="$2" '
    NR==1 && $0=="---" { infm=1; next }
    infm && $0=="---"  { exit }
    !infm { next }
    {
      if (match($0, "^[[:space:]]*" key ":")) {
        rest=$0; sub("^[[:space:]]*" key ":", "", rest)
        sub(/^[[:space:]]+/, "", rest); sub(/[[:space:]]+$/, "", rest)
        if (rest ~ /^\[.*\]$/) {
          sub(/^\[/, "", rest); sub(/\]$/, "", rest)
          n=split(rest, a, ","); for (i=1;i<=n;i++) print a[i]
          inblock=0; next
        } else if (rest != "") { print rest; inblock=0; next }
        else { inblock=1; next }
      }
      if (inblock==1) {
        if ($0 ~ /^[[:space:]]*-[[:space:]]*/) {
          item=$0; sub(/^[[:space:]]*-[[:space:]]*/, "", item); print item; next
        } else if ($0 ~ /^[[:space:]]*$/) { next }
        else { inblock=0 }
      }
    }
  ' "$1"
}

# trim leading/trailing whitespace and one layer of matching quotes
trim() { sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/^"(.*)"$/\1/; s/^'\''(.*)'\''$/\1/'; }

# --- collect rows ----------------------------------------------------------
ROWS_FILE="$(mktemp)"      # lines: scope<TAB>action<TAB>skill
MISSING=()                 # skills missing scope or auto_invoke
UNKNOWN_SCOPES=()          # "skill:scope" whose scope is not in SCOPE_DIRS
trap 'rm -f "$ROWS_FILE"' EXIT

shopt -s nullglob
skill_count=0
for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
  skill_count=$((skill_count+1))
  dir_name="$(basename "$(dirname "$skill_md")")"
  name="$(fm_values "$skill_md" name | head -n1 | trim)"
  [ -n "$name" ] || name="$dir_name"

  mapfile -t scopes < <(fm_values "$skill_md" scope | trim)
  mapfile -t actions < <(fm_values "$skill_md" auto_invoke | trim)

  if [ "${#scopes[@]}" -eq 0 ] || [ -z "${scopes[*]// }" ] \
     || [ "${#actions[@]}" -eq 0 ] || [ -z "${actions[*]// }" ]; then
    MISSING+=("$name")
    continue
  fi

  for scope in "${scopes[@]}"; do
    [ -n "$scope" ] || continue
    if [ -z "${SCOPE_DIRS[$scope]+x}" ]; then
      UNKNOWN_SCOPES+=("$name:$scope")
      continue
    fi
    for action in "${actions[@]}"; do
      [ -n "$action" ] || continue
      printf '%s\t%s\t%s\n' "$scope" "$action" "$name" >> "$ROWS_FILE"
    done
  done
done

# --- regenerate each scope's AGENTS.md ------------------------------------
changed=0
for scope in "${!SCOPE_DIRS[@]}"; do
  [ -z "$ONLY_SCOPE" ] || [ "$scope" = "$ONLY_SCOPE" ] || continue
  dir="${SCOPE_DIRS[$scope]}"
  if [ "$dir" = "." ]; then agents="$REPO_ROOT/AGENTS.md"; else agents="$REPO_ROOT/$dir/AGENTS.md"; fi
  if [ ! -f "$agents" ]; then
    echo "WARN: scope '$scope' -> $agents does not exist; skipping" >&2
    continue
  fi
  if ! grep -qF "$MARKER" "$agents"; then
    echo "WARN: '$MARKER' marker not found in $agents; skipping" >&2
    continue
  fi

  # build the generated body (everything BETWEEN the marker and the terminator)
  body="$(mktemp)"
  {
    printf '\n%s\n\n' "$INTRO"
    printf '| Action | Skill |\n| ------ | ----- |\n'
    # escape any literal '|' in the action/skill so it cannot break the table cell
    LC_ALL=C awk -F'\t' -v s="$scope" '$1==s{a=$2; n=$3; gsub(/\|/,"\\|",a); gsub(/\|/,"\\|",n); printf "| %s | `%s` |\n", a, n}' "$ROWS_FILE" | LC_ALL=C sort -u
    printf '\n'
  } > "$body"

  out="$(mktemp)"
  awk -v marker="$MARKER" -v bodyfile="$body" '
    $0==marker && !done {
      print
      while ((getline l < bodyfile) > 0) print l
      close(bodyfile)
      skipping=1; done=1; next
    }
    skipping && ($0 ~ /^---$/ || $0 ~ /^## /) { skipping=0; print; next }
    skipping { next }
    { print }
  ' "$agents" > "$out"

  if ! cmp -s "$out" "$agents"; then
    changed=$((changed+1))
    rel="${agents#$REPO_ROOT/}"
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "--- would update: $rel"
      diff -u "$agents" "$out" | sed -n '1,200p' || true
    else
      cp "$out" "$agents"
      echo "updated: $rel"
    fi
  fi
  rm -f "$body" "$out"
done

# --- report ----------------------------------------------------------------
echo
if [ "$skill_count" -eq 0 ]; then
  echo "No skills found in $SKILLS_DIR."
else
  total_rows=$(wc -l < "$ROWS_FILE" | tr -d ' ')
  echo "Skills: $skill_count   routed rows: $total_rows   AGENTS.md changed: $changed$( [ "$DRY_RUN" -eq 1 ] && echo ' (dry-run)')"
fi
if [ "${#UNKNOWN_SCOPES[@]}" -gt 0 ]; then
  echo "scope not in SCOPE_DIRS (rows dropped): ${UNKNOWN_SCOPES[*]}"
fi
if [ "${#MISSING[@]}" -gt 0 ]; then
  echo "missing sync metadata (skipped, add scope + auto_invoke): ${MISSING[*]}"
fi
exit 0
