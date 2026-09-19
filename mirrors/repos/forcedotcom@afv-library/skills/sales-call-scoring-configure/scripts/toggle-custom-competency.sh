#!/bin/bash
# sales_call_scoring: story="custom-competency-crud" owner="W-CUSTOM-CRUD"
#
# Activate or deactivate a Coaching Competency by DeveloperName or Id.
# Toggles IsActive via Tooling API PATCH.
#
# Deactivation preserves historical EnablementCompetencyEval scores (per the
# entity XML comment on IsActive) so a rehired competency picks up its
# existing evaluation history.
#
# Companion of create-custom-competency.sh — parallel to toggle-competency.sh
# so the custom-CRUD story can iterate the activate/deactivate surface
# independently.
#
# Usage: ./toggle-custom-competency.sh <org-alias> <name-or-id> <activate|deactivate>

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
IDENT="${2:-}"
ACTION="${3:-}"

if [[ -z "$ORG_ALIAS" || -z "$IDENT" || -z "$ACTION" ]]; then
  echo "Usage: $0 <org-alias> <name-or-id> <activate|deactivate>"
  exit 1
fi

if [[ "$ACTION" != "activate" && "$ACTION" != "deactivate" ]]; then
  echo "Action must be 'activate' or 'deactivate'"
  exit 1
fi

TARGET=$([[ "$ACTION" == "activate" ]] && echo "true" || echo "false")

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"
# shellcheck source=shared/soql.sh
source "$SCRIPT_DIR/shared/soql.sh"

resolve_org_auth "$ORG_ALIAS" || exit 1

TOOLING_BASE="services/data/v68.0/tooling"

# ---------------------------------------------------------------------------
# Resolve identifier
# ---------------------------------------------------------------------------
if [[ "$IDENT" =~ ^1nA[0-9a-zA-Z]{12,15}$ ]]; then
  WHERE="Id='${IDENT}'"
else
  SAFE=$(soql_escape "$IDENT")
  WHERE="DeveloperName='${SAFE}' OR MasterLabel='${SAFE}'"
fi

QUERY="SELECT+Id,MasterLabel,IsActive+FROM+EnablementCompetencyDef+WHERE+$(printf '%s' "$WHERE" | jq -sRr @uri)"
LOOKUP=$(sf api request rest "${TOOLING_BASE}/query/?q=${QUERY}" --target-org "$ORG_ALIAS" 2>/dev/null || true)

RECORD_COUNT=$(echo "$LOOKUP" | jq -r '.totalSize // 0' 2>/dev/null || echo "0")
if [[ "$RECORD_COUNT" == "0" ]]; then
  echo "No competency found matching: $IDENT"
  exit 1
fi
if [[ "$RECORD_COUNT" != "1" ]]; then
  echo "Multiple competencies matched '$IDENT' — refusing to bulk-toggle."
  echo "$LOOKUP" | jq -r '.records[] | "   \(.Id)  \(.MasterLabel)"'
  exit 1
fi

REC_ID=$(echo "$LOOKUP" | jq -r '.records[0].Id')
REC_LABEL=$(echo "$LOOKUP" | jq -r '.records[0].MasterLabel')
REC_STATE=$(echo "$LOOKUP" | jq -r '.records[0].IsActive')

echo "$REC_LABEL ($REC_ID) — currently IsActive=$REC_STATE"

# Idempotency
if [[ "$REC_STATE" == "$TARGET" ]]; then
  echo "Already $ACTION'd — no-op."
  exit 0
fi

# Enforce 8-active cap when activating. Refuse with a rich report — the
# activate path can't auto-fallback because "activate to inactive" is a
# no-op; the admin must actively free a slot.
if [[ "$ACTION" == "activate" ]]; then
  # shellcheck source=shared/cap.sh
  source "$SCRIPT_DIR/shared/cap.sh"

  ACTIVE_COUNT=$(query_active_count "$ORG_ALIAS")
  if [[ "$ACTIVE_COUNT" -ge "$MAX_ACTIVE_COMPETENCIES" ]]; then
    echo "Cannot activate '$REC_LABEL' — org is at the 8-active competency cap."
    print_cap_report "$ORG_ALIAS" "activating '$REC_LABEL'"
    echo "    Once a slot is free, retry:"
    echo ""
    echo "      $0 $ORG_ALIAS $REC_ID activate"
    echo ""
    exit 1
  fi
fi

# ---------------------------------------------------------------------------
# PATCH
# ---------------------------------------------------------------------------
PAYLOAD=$(jq -n --argjson v "$TARGET" '{IsActive: $v}')

# sf api request rest exits non-zero on HTTP failure; success on Tooling
# PATCH is HTTP 204 (empty body). Capture both stdout and exit status.
if RESP_BODY=$(sf api request rest "${TOOLING_BASE}/sobjects/EnablementCompetencyDef/${REC_ID}" \
    --target-org "$ORG_ALIAS" \
    --method PATCH \
    --header 'Content-Type: application/json' \
    --body "$PAYLOAD" \
    2>&1); then
  echo "${ACTION}d $REC_LABEL — IsActive now $TARGET"
  exit 0
else
  echo "Error: PATCH failed"
  echo "   $RESP_BODY"
  exit 1
fi
