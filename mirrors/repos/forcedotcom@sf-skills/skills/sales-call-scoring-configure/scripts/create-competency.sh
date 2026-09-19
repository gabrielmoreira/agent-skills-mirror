#!/bin/bash

# Create a single custom Coaching Competency from a JSON payload.
# Payload must contain: MasterLabel, EvaluationInstructions.
# Optional: DeveloperName (auto-generated if omitted), Description,
# EvaluationScope (defaults AllCalls), IsActive (defaults true),
# SourceCompetencyTemplate (empty for custom).
#
# This is the deterministic write primitive for S5 (custom conversational
# competency creation). Claude drives the conversational drafting;
# once the prompt is approved, it writes the payload to a temp JSON and
# invokes this script.
#
# Usage: ./create-competency.sh <org-alias> <payload.json>

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
PAYLOAD_FILE="${2:-}"

if [[ -z "$ORG_ALIAS" || -z "$PAYLOAD_FILE" ]]; then
  echo "Usage: $0 <org-alias> <payload.json>"
  exit 1
fi
if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "Payload file not found: $PAYLOAD_FILE"
  exit 1
fi

# ---------------------------------------------------------------------------
# Validate payload
# ---------------------------------------------------------------------------
MASTER_LABEL=$(jq -r '.MasterLabel // empty' "$PAYLOAD_FILE")
INSTRUCTIONS=$(jq -r '.EvaluationInstructions // empty' "$PAYLOAD_FILE")

if [[ -z "$MASTER_LABEL" ]]; then echo "MasterLabel is required"; exit 1; fi
if [[ -z "$INSTRUCTIONS" ]]; then echo "EvaluationInstructions is required"; exit 1; fi

INSTR_LEN=${#INSTRUCTIONS}
if [[ "$INSTR_LEN" -gt 16000 ]]; then
  echo "EvaluationInstructions is $INSTR_LEN chars — max 16000"
  exit 1
fi

DESCRIPTION=$(jq -r '.Description // ""' "$PAYLOAD_FILE")
DESC_LEN=${#DESCRIPTION}
if [[ "$DESC_LEN" -gt 255 ]]; then
  echo "Description is $DESC_LEN chars — max 255"
  exit 1
fi

SCOPE=$(jq -r '.EvaluationScope // "AllCalls"' "$PAYLOAD_FILE")
if [[ "$SCOPE" != "AllCalls" && "$SCOPE" != "SpecificCallsOnly" ]]; then
  echo "EvaluationScope must be AllCalls or SpecificCallsOnly (got: $SCOPE)"
  exit 1
fi

# jq's // treats false as absent; use explicit null-check to preserve IsActive:false.
IS_ACTIVE=$(jq -r 'if has("IsActive") then .IsActive else true end' "$PAYLOAD_FILE")
TEMPLATE=$(jq -r '.SourceCompetencyTemplate // ""' "$PAYLOAD_FILE")
DEV_NAME=$(jq -r '.DeveloperName // empty' "$PAYLOAD_FILE")

if [[ -z "$DEV_NAME" ]]; then
  SANITIZED=$(echo "$MASTER_LABEL" | tr -cd '[:alnum:]' | cut -c1-30)
  SUFFIX=$(hexdump -n 3 -e '"%06x"' /dev/urandom)
  DEV_NAME="CCH_${SANITIZED}_${SUFFIX}"
fi

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"

resolve_org_auth "$ORG_ALIAS" || exit 1

TOOLING_BASE="services/data/v68.0/tooling"

# ---------------------------------------------------------------------------
# 8-active cap: auto-fallback to inactive so the admin's work isn't blocked.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=shared/cap.sh
source "$SCRIPT_DIR/shared/cap.sh"
# shellcheck source=shared/soql.sh
source "$SCRIPT_DIR/shared/soql.sh"

CAP_FELL_BACK="false"
if [[ "$IS_ACTIVE" == "true" ]]; then
  ACTIVE_COUNT=$( (sf api request rest \
    "${TOOLING_BASE}/query/?q=SELECT+COUNT()+FROM+EnablementCompetencyDef+WHERE+IsActive=true" \
    --target-org "$ORG_ALIAS" 2>/dev/null || true) | jq -r '.totalSize // 0' 2>/dev/null)
  ACTIVE_COUNT="${ACTIVE_COUNT:-0}"
  if [[ "$ACTIVE_COUNT" -ge "$MAX_ACTIVE_COMPETENCIES" ]]; then
    echo "Warning: Org is at the 8-active competency cap — creating this one as inactive."
    echo "   Deactivate an existing competency, then re-activate this one to promote it."
    IS_ACTIVE="false"
    CAP_FELL_BACK="true"
  fi
fi

# ---------------------------------------------------------------------------
# Uniqueness check by MasterLabel (to avoid silent duplicates)
# ---------------------------------------------------------------------------
LABEL_ENC=$(printf "SELECT Id FROM EnablementCompetencyDef WHERE MasterLabel='%s'" "$(soql_escape "$MASTER_LABEL")" | jq -sRr @uri)
DUP=$( (sf api request rest "${TOOLING_BASE}/query/?q=${LABEL_ENC}" --target-org "$ORG_ALIAS" 2>/dev/null || true) \
  | jq -r '.totalSize // 0' 2>/dev/null)
DUP="${DUP:-0}"
if [[ "$DUP" != "0" ]]; then
  echo "A competency with MasterLabel '$MASTER_LABEL' already exists — refusing to duplicate."
  echo "   Use edit-competency.sh to update, or choose a different name."
  exit 1
fi

# ---------------------------------------------------------------------------
# Build final payload + POST
# ---------------------------------------------------------------------------
FINAL=$(jq -n \
  --arg mn "$MASTER_LABEL" \
  --arg dn "$DEV_NAME" \
  --arg tp "$TEMPLATE" \
  --arg de "$DESCRIPTION" \
  --arg ei "$INSTRUCTIONS" \
  --arg sc "$SCOPE" \
  --argjson ia "$IS_ACTIVE" \
  '{
     MasterLabel: $mn,
     DeveloperName: $dn,
     Description: $de,
     EvaluationInstructions: $ei,
     EvaluationScope: $sc,
     IsActive: $ia
   } + (if $tp == "" then {} else {SourceCompetencyTemplate: $tp} end)')

echo "Creating: $MASTER_LABEL"
# No DeveloperName / char count / entity-field leak — rule #5. Scope is
# admin-facing content ("AllCalls" / "SpecificCallsOnly") so it stays.
echo "   Scope: $SCOPE   Active: $IS_ACTIVE"

RESP=$(sf api request rest "${TOOLING_BASE}/sobjects/EnablementCompetencyDef" \
  --target-org "$ORG_ALIAS" \
  --method POST \
  --header 'Content-Type: application/json' \
  --body "$FINAL" \
  2>/dev/null) || true

if echo "$RESP" | jq -e '.success == true' >/dev/null 2>&1; then
  NEW_ID=$(echo "$RESP" | jq -r '.id')
  # No record Id leak on the primary success line — rule #5. Cap-fallback
  # hint helper prints the activate-later reminder without exposing the Id.
  if [[ "$CAP_FELL_BACK" == "true" ]]; then
    echo "Created inactive (8-active cap), activate later"
    print_cap_footer_activate_hint "$NEW_ID"
  else
    echo "Created"
  fi
  exit 0
else
  echo "Error: Create failed:"
  echo "$RESP" | jq -c '.' 2>/dev/null || echo "$RESP"
  exit 1
fi
