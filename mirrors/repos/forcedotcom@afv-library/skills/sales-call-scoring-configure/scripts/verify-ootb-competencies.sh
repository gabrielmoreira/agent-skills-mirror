#!/bin/bash

# Verify that a set of expected Coaching Competencies exist and are active,
# displaying each one's name + EvaluationInstructions in a markdown table so
# the admin can review what's actually configured. Defaults to the 6 OOTB
# competencies (assets/ootb-competencies.json); pass explicit names to verify
# a custom subset instead (e.g. after the admin chose only some of the OOTB
# set, or created custom competencies).
#
# Exit 0 only if every expected name exists AND is active. Exit 1 otherwise,
# listing what's missing or inactive.
#
# Usage:
#   ./verify-ootb-competencies.sh <org-alias>                       # verify full OOTB set
#   ./verify-ootb-competencies.sh <org-alias> "Name One" "Name Two" # verify specific names

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
shift || true

if [[ -z "$ORG_ALIAS" ]]; then
  echo "Error: Missing org alias"
  echo "Usage: $0 <org-alias> [\"Competency Name\" ...]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_FILE="$SCRIPT_DIR/../assets/ootb-competencies.json"

# ---------------------------------------------------------------------------
# Expected names: caller-supplied args, else the full OOTB set.
# ---------------------------------------------------------------------------
EXPECTED_NAMES=()
if [[ "$#" -gt 0 ]]; then
  EXPECTED_NAMES=("$@")
else
  if [[ ! -f "$ASSETS_FILE" ]]; then
    echo "Cannot find $ASSETS_FILE"
    exit 1
  fi
  while IFS= read -r name; do
    EXPECTED_NAMES+=("$name")
  done < <(jq -r '.competencies[].MasterLabel' "$ASSETS_FILE")
fi

echo "Verifying Coaching Competencies on org: $ORG_ALIAS"
echo ""
echo "   Expecting ${#EXPECTED_NAMES[@]} competenc$([[ ${#EXPECTED_NAMES[@]} == 1 ]] && echo "y" || echo "ies"):"
for n in "${EXPECTED_NAMES[@]}"; do
  echo "     - $n"
done
echo ""

# ---------------------------------------------------------------------------
# Fetch all existing competencies once, then check expected names against them.
# Auth is handled internally by `sf api request rest` (no token extraction).
# ---------------------------------------------------------------------------
EXISTING_RAW=$(sf api request rest \
  "services/data/v68.0/tooling/query/?q=SELECT+Id,DeveloperName,MasterLabel,Description,EvaluationInstructions,IsActive,EvaluationScope,SourceCompetencyTemplate+FROM+EnablementCompetencyDef" \
  --target-org "$ORG_ALIAS" 2>/dev/null)

if ! echo "$EXISTING_RAW" | jq -e 'has("records")' >/dev/null 2>&1; then
  echo "Error: Tooling API query failed. Is the org authenticated?"
  echo "$EXISTING_RAW" | jq -r '.[0].message // .message // .' 2>/dev/null || echo "$EXISTING_RAW"
  exit 1
fi

MISSING=()
INACTIVE=()
OK=()
ROWS=()

for NAME in "${EXPECTED_NAMES[@]}"; do
  MATCH=$(echo "$EXISTING_RAW" | jq -c --arg n "$NAME" '.records[] | select(.MasterLabel == $n)' | head -1)

  if [[ -z "$MATCH" ]]; then
    MISSING+=("$NAME")
    ROWS+=("missing | $NAME | _not found on this org_")
    continue
  fi

  IS_ACTIVE=$(echo "$MATCH" | jq -r '.IsActive')
  INSTRUCTIONS=$(echo "$MATCH" | jq -r '.EvaluationInstructions // "(none)"' | tr '\n' ' ' | sed 's/|/\\|/g')

  if [[ "$IS_ACTIVE" == "true" ]]; then
    OK+=("$NAME")
    STATUS_ICON="OK"
  else
    INACTIVE+=("$NAME")
    STATUS_ICON="--"
  fi

  ROWS+=("$STATUS_ICON | $NAME | $INSTRUCTIONS")
done

echo "Results:"
echo ""
echo "| | Competency | Evaluation Instructions |"
echo "|---|---|---|"
for ROW in "${ROWS[@]}"; do
  echo "| $ROW |"
done
echo ""

echo "Summary: ${#OK[@]} ok, ${#INACTIVE[@]} inactive, ${#MISSING[@]} missing (of ${#EXPECTED_NAMES[@]} expected)"

if [[ "${#MISSING[@]}" -gt 0 || "${#INACTIVE[@]}" -gt 0 ]]; then
  exit 1
fi

echo "All expected competencies exist and are active."
exit 0
