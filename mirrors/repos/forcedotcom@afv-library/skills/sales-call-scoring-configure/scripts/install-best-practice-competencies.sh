#!/bin/bash

# Install best-practice Coaching Competencies (Momentum reference prompts,
# 7 total) from PRD-canonical prompt bodies. Parallel to install-ootb-*
# but reads from assets/best-practice-competencies.json.
#
# The prompt bodies here are the full PURPOSE / KEY AREAS / positive-
# negative-indicators / EXAMPLE structure — NOT the terse OOTB defaults.
# When installed, each record's EvaluationInstructions is the best-practice
# prompt, so Codey scores calls against the richer reference criteria.
#
# Idempotent: skips any competency whose SourceCompetencyTemplate already
# exists on the org.
#
# Usage:
#   ./install-best-practice-competencies.sh <org-alias>
#   ./install-best-practice-competencies.sh <org-alias> --dry-run
#   ./install-best-practice-competencies.sh <org-alias> --only "Discovery Excellence,Product Knowledge"

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
DRY_RUN=""
ONLY_LIST=""

# Parse args after alias
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    --only)    ONLY_LIST="${2:-}"; shift 2 ;;
    *) echo "Error: Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$ORG_ALIAS" ]]; then
  echo "Error: Missing org alias"
  echo "Usage: $0 <org-alias> [--dry-run] [--only 'Name1,Name2,...']"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_FILE="$SCRIPT_DIR/../assets/best-practice-competencies.json"

if [[ ! -f "$ASSETS_FILE" ]]; then
  echo "Cannot find $ASSETS_FILE"
  exit 1
fi

echo "Installing Best-Practice Coaching Competencies on org: $ORG_ALIAS"
if [[ "$DRY_RUN" == "--dry-run" ]]; then
  echo "   (DRY RUN — will not create records)"
fi
if [[ -n "$ONLY_LIST" ]]; then
  echo "   Subset: $ONLY_LIST"
fi
echo ""

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"

resolve_org_auth "$ORG_ALIAS" || exit 1

TOOLING_BASE="services/data/v68.0/tooling"

# shellcheck source=shared/cap.sh
source "$SCRIPT_DIR/shared/cap.sh"

# Detect cap state once up-front. New installs land inactive (with a clear
# warning) rather than being refused — the admin activates later.
CAP_HIT="false"
INITIAL_ACTIVE_COUNT=$(query_active_count "$ORG_ALIAS")
if [[ "$INITIAL_ACTIVE_COUNT" -ge "$MAX_ACTIVE_COMPETENCIES" ]]; then
  print_cap_report "$ORG_ALIAS" "installing best-practice Coaching Competencies"
  echo "    Any new records created by this run will land INACTIVE. Activate them" >&2
  echo "    once you free a slot with toggle-custom-competency.sh." >&2
  echo "" >&2
  CAP_HIT="true"
fi

# ---------------------------------------------------------------------------
# Build the working list (all 7 or --only subset)
# ---------------------------------------------------------------------------
if [[ -n "$ONLY_LIST" ]]; then
  # Comma-separated MasterLabels → jq array filter
  ONLY_ARR=$(echo "$ONLY_LIST" | jq -Rc 'split(",") | map(gsub("^\\s+|\\s+$"; ""))')
  WORKING=$(jq --argjson only "$ONLY_ARR" \
    '.competencies | map(select(.MasterLabel as $ml | $only | index($ml)))' \
    "$ASSETS_FILE")
  # Validate: warn on any --only entry that didn't match.
  # Iterate via NUL separator so labels with spaces survive intact.
  while IFS= read -r -d '' req; do
    HIT=$(echo "$WORKING" | jq --arg r "$req" '[.[] | select(.MasterLabel == $r)] | length')
    if [[ "$HIT" == "0" ]]; then
      echo "Warning: --only entry not found in asset file: '$req'"
    fi
  done < <(echo "$ONLY_ARR" | jq -jr '.[] + "\u0000"')
else
  WORKING=$(jq '.competencies' "$ASSETS_FILE")
fi

COUNT=$(echo "$WORKING" | jq 'length')
if [[ "$COUNT" == "0" ]]; then
  echo "No competencies matched — nothing to install"
  exit 1
fi

echo "Working set: $COUNT competencies"
echo ""

# ---------------------------------------------------------------------------
# Iterate
# ---------------------------------------------------------------------------
CREATED=0
SKIPPED=0
FAILED=0

for i in $(seq 0 $((COUNT - 1))); do
  MASTER_LABEL=$(echo "$WORKING" | jq -r ".[$i].MasterLabel")
  DEV_NAME_BASE=$(echo "$WORKING" | jq -r ".[$i].DeveloperNameBase")
  TEMPLATE=$(echo "$WORKING" | jq -r ".[$i].SourceCompetencyTemplate // \"\"")
  DESCRIPTION=$(echo "$WORKING" | jq -r ".[$i].Description // \"\"")
  INSTRUCTIONS=$(echo "$WORKING" | jq -r ".[$i].EvaluationInstructions")
  SCOPE=$(echo "$WORKING" | jq -r ".[$i].EvaluationScope // \"AllCalls\"")

  # Char-cap enforcement (server rejects with a generic error; we surface up front)
  INSTR_LEN=${#INSTRUCTIONS}
  if [[ "$INSTR_LEN" -gt 16000 ]]; then
    echo "  Error: $MASTER_LABEL — EvaluationInstructions is $INSTR_LEN chars (max 16000), skipping"
    FAILED=$((FAILED + 1))
    continue
  fi

  # Idempotency check by SourceCompetencyTemplate. Best-practice templates
  # like BUSINESS_PROBLEM_DIAGNOSIS live in the same enum space as OOTB
  # (DISCOVERY_QUESTIONING etc), so this correctly prevents dup installs
  # across both installer scripts.
  if [[ -n "$TEMPLATE" ]]; then
    ALREADY_INSTALLED=$( (sf api request rest \
      "${TOOLING_BASE}/query/?q=SELECT+Id+FROM+EnablementCompetencyDef+WHERE+SourceCompetencyTemplate='${TEMPLATE}'" \
      --target-org "$ORG_ALIAS" 2>/dev/null || true) | jq -r '.totalSize // 0' 2>/dev/null)
    ALREADY_INSTALLED="${ALREADY_INSTALLED:-0}"

    if [[ "$ALREADY_INSTALLED" != "0" ]]; then
      # No Template enum leak — rule #5.
      echo "  $MASTER_LABEL — already installed, skipping"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
  fi

  # 8-active cap handled up-front by CAP_HIT: if we're at the cap, land the
  # record as inactive so the admin can activate it later. Prevents mid-batch
  # server rejections and keeps the installer non-blocking.

  SUFFIX=$(hexdump -n 3 -e '"%06x"' /dev/urandom)
  DEV_NAME="${DEV_NAME_BASE}_${SUFFIX}"

  IS_ACTIVE_JSON=$([[ "$CAP_HIT" == "true" ]] && echo "false" || echo "true")
  PAYLOAD=$(jq -n \
    --arg mn "$MASTER_LABEL" \
    --arg dn "$DEV_NAME" \
    --arg tp "$TEMPLATE" \
    --arg de "$DESCRIPTION" \
    --arg ei "$INSTRUCTIONS" \
    --arg sc "$SCOPE" \
    --argjson ia "$IS_ACTIVE_JSON" \
    '{
       MasterLabel: $mn,
       DeveloperName: $dn,
       Description: $de,
       EvaluationInstructions: $ei,
       EvaluationScope: $sc,
       IsActive: $ia
     } + (if $tp == "" then {} else {SourceCompetencyTemplate: $tp} end)')

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    # No DeveloperName / char-count leak — rule #5.
    echo "  $MASTER_LABEL — would create"
    CREATED=$((CREATED + 1))
    continue
  fi

  RESP=$(sf api request rest "${TOOLING_BASE}/sobjects/EnablementCompetencyDef" \
    --target-org "$ORG_ALIAS" \
    --method POST \
    --header 'Content-Type: application/json' \
    --body "$PAYLOAD" \
    2>/dev/null) || true

  if echo "$RESP" | jq -e '.success == true' >/dev/null 2>&1; then
    # No record Id / char-count leak — rule #5.
    if [[ "$CAP_HIT" == "true" ]]; then
      echo "  $MASTER_LABEL — created inactive (8-active cap), activate later"
    else
      echo "  $MASTER_LABEL — created"
    fi
    CREATED=$((CREATED + 1))
  else
    echo "  Error: $MASTER_LABEL — create failed:"
    echo "     $(echo "$RESP" | jq -c '.' 2>/dev/null || echo "$RESP")"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
if [[ "$CAP_HIT" == "true" && "$CREATED" -gt 0 ]]; then
  echo "Summary: $CREATED created INACTIVE (8-active cap), $SKIPPED already-installed, $FAILED failed"
  echo "         Deactivate a currently-active competency, then activate these with:"
  echo "           ./skills/sales-call-scoring-configure/scripts/toggle-custom-competency.sh $ORG_ALIAS <Id-or-name> activate"
else
  echo "Summary: $CREATED created, $SKIPPED already-installed, $FAILED failed"
fi

if [[ "$FAILED" -gt 0 ]]; then
  exit 1
fi
