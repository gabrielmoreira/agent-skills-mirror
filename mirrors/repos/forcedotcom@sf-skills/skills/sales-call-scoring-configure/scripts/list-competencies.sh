#!/bin/bash

# List existing Coaching Competencies on the org.
# Reads EnablementCompetencyDef (setup entity, keyPrefix 1nA) via Tooling API.
#
# Output modes (per SKILL.md rule #5 — admin-safe by default):
#   default   — MasterLabel + IsActive + Scope + Description only.
#               No record Ids, DeveloperNames, or Template enum keys.
#   --verbose — Everything the default shows, PLUS DeveloperName, Id, and
#               SourceCompetencyTemplate. Use when the admin explicitly
#               asks to debug or share with support.
#   --json    — Raw record JSON for the calling agent to parse. Never
#               forward this to the admin directly.
#
# Usage:
#   ./list-competencies.sh <org-alias>
#   ./list-competencies.sh <org-alias> --verbose
#   ./list-competencies.sh <org-alias> --json

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
FORMAT="${2:-text}"

if [[ -z "$ORG_ALIAS" ]]; then
  echo "Error: Missing org alias"
  echo "Usage: $0 <org-alias> [--verbose|--json]"
  exit 1
fi

case "$FORMAT" in
  text|--verbose|--json) ;;
  *) echo "Error: Unknown flag: $FORMAT (expected --verbose or --json)"; exit 1 ;;
esac

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"

resolve_org_auth "$ORG_ALIAS" || exit 1

QUERY="SELECT Id, DeveloperName, MasterLabel, Description, IsActive, EvaluationScope, SourceCompetencyTemplate FROM EnablementCompetencyDef ORDER BY MasterLabel"

RAW=$(sf data query --target-org "$ORG_ALIAS" --use-tooling-api \
  --query "$QUERY" --json 2>/dev/null)

# sf can prepend update-available warnings to stdout — extract the JSON body.
RAW_JSON=$(echo "$RAW" | awk '/^{/,EOF')

if ! echo "$RAW_JSON" | jq -e '.status == 0' >/dev/null 2>&1; then
  echo "Error: Tooling API query failed:"
  echo "$RAW" | jq -r '.message // .' 2>/dev/null || echo "$RAW"
  exit 1
fi
RAW="$RAW_JSON"

if [[ "$FORMAT" == "--json" ]]; then
  echo "$RAW" | jq '.result.records'
  exit 0
fi

TOTAL=$(echo "$RAW" | jq -r '.result.totalSize')
ACTIVE=$(echo "$RAW" | jq -r '[.result.records[] | select(.IsActive == true)] | length')

echo "Coaching Competencies on $ORG_ALIAS"
echo ""
echo "   Total: $TOTAL   Active: $ACTIVE / 8 (max)"
echo ""

if [[ "$TOTAL" == "0" ]]; then
  echo "   (none configured yet — run install-ootb-competencies.sh to seed the OOTB set)"
  exit 0
fi

if [[ "$FORMAT" == "--verbose" ]]; then
  # Full technical detail — Ids, DeveloperNames, Template enum keys.
  # Only show this when the admin explicitly asks to debug or share with support.
  echo "$RAW" | jq -r '.result.records[] |
    "   \(if .IsActive then "" else "" end)  \(.MasterLabel)
         Scope:         \(.EvaluationScope)
         Description:   \(.Description // "(none)")
         DeveloperName: \(.DeveloperName)\(if .SourceCompetencyTemplate != null and .SourceCompetencyTemplate != "" then "
         Template:      \(.SourceCompetencyTemplate)" else "" end)
         Id:            \(.Id)
    "'
else
  # Default admin-safe view — no Ids, DeveloperNames, or Template enum keys.
  echo "$RAW" | jq -r '.result.records[] |
    "   \(if .IsActive then "" else "" end)  \(.MasterLabel)
         Scope:       \(.EvaluationScope)
         Description: \(.Description // "(none)")
    "'
fi
