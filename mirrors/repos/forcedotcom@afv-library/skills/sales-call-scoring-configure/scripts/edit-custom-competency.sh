#!/bin/bash
# sales_call_scoring: story="custom-competency-crud" owner="W-CUSTOM-CRUD"
#
# Edit a Coaching Competency's MasterLabel, Description, and/or
# EvaluationInstructions.
# Preserves Id, DeveloperName, IsActive, EvaluationScope, SourceCompetencyTemplate.
#
# --label renames the admin-facing display name (MasterLabel). DeveloperName
# is NOT renamed — it's the API name used by any downstream references and
# would risk breaking integrations to change.
#
# Companion of create-custom-competency.sh. Kept as its own file so the
# custom-CRUD story can extend it (e.g. accept scope change to
# SpecificCallsOnly + EvaluationConditions) without conflicting with the
# OOTB story's edit surface.
#
# Usage:
#   ./edit-custom-competency.sh <org-alias> <name-or-id> --label "<new-label>"
#   ./edit-custom-competency.sh <org-alias> <name-or-id> --instructions-file <file>
#   ./edit-custom-competency.sh <org-alias> <name-or-id> --description "<new-desc>"
#   ./edit-custom-competency.sh <org-alias> <name-or-id> --instructions "<literal>"
#   (combine flags to update multiple fields at once)

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
IDENT="${2:-}"
shift 2 || true

if [[ -z "$ORG_ALIAS" || -z "$IDENT" ]]; then
  echo "Usage: $0 <org-alias> <name-or-id> [--label \"<text>\"] [--instructions-file <file>] [--description \"<text>\"] [--instructions \"<text>\"]"
  exit 1
fi

NEW_LABEL=""
NEW_INSTRUCTIONS=""
NEW_DESCRIPTION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)
      NEW_LABEL="$2"
      shift 2
      ;;
    --instructions-file)
      if [[ ! -f "$2" ]]; then
        echo "File not found: $2"; exit 1
      fi
      NEW_INSTRUCTIONS=$(cat "$2")
      shift 2
      ;;
    --instructions)
      NEW_INSTRUCTIONS="$2"
      shift 2
      ;;
    --description)
      NEW_DESCRIPTION="$2"
      shift 2
      ;;
    *)
      echo "Error: Unknown flag: $1"; exit 1
      ;;
  esac
done

if [[ -z "$NEW_LABEL" && -z "$NEW_INSTRUCTIONS" && -z "$NEW_DESCRIPTION" ]]; then
  echo "Nothing to update — pass --label, --instructions[-file], and/or --description"
  exit 1
fi

if [[ -n "$NEW_LABEL" ]]; then
  LEN=${#NEW_LABEL}
  # MasterLabel is a standard platform label field, capped at 80 chars.
  if [[ "$LEN" -gt 80 ]]; then
    echo "MasterLabel is ${LEN} chars — max is 80."
    exit 1
  fi
fi

if [[ -n "$NEW_INSTRUCTIONS" ]]; then
  LEN=${#NEW_INSTRUCTIONS}
  if [[ "$LEN" -gt 16000 ]]; then
    echo "EvaluationInstructions is ${LEN} chars — max is 16000."
    exit 1
  fi
fi

if [[ -n "$NEW_DESCRIPTION" ]]; then
  LEN=${#NEW_DESCRIPTION}
  if [[ "$LEN" -gt 255 ]]; then
    echo "Description is ${LEN} chars — max is 255."
    exit 1
  fi
fi

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
QUERY_ENC=$(printf 'SELECT Id,MasterLabel,IsActive FROM EnablementCompetencyDef WHERE %s' "$WHERE" | jq -sRr @uri)
LOOKUP=$(sf api request rest "${TOOLING_BASE}/query/?q=${QUERY_ENC}" --target-org "$ORG_ALIAS" 2>/dev/null || true)
RC=$(echo "$LOOKUP" | jq -r '.totalSize // 0' 2>/dev/null || echo "0")

if [[ "$RC" == "0" ]]; then echo "No competency matched: $IDENT"; exit 1; fi
if [[ "$RC" != "1" ]]; then
  echo "Multiple competencies matched '$IDENT' — refusing to bulk-edit."
  echo "$LOOKUP" | jq -r '.records[] | "   \(.Id)  \(.MasterLabel)"'
  exit 1
fi

REC_ID=$(echo "$LOOKUP" | jq -r '.records[0].Id')
REC_LABEL=$(echo "$LOOKUP" | jq -r '.records[0].MasterLabel')
REC_ACTIVE=$(echo "$LOOKUP" | jq -r '.records[0].IsActive')

echo "$REC_LABEL ($REC_ID) — IsActive=$REC_ACTIVE"

# ---------------------------------------------------------------------------
# Uniqueness gate for rename — mirrors the check create-custom-competency.sh
# runs on create. Excludes the target record's own Id so a no-op rename
# doesn't self-collide.
# ---------------------------------------------------------------------------
if [[ -n "$NEW_LABEL" && "$NEW_LABEL" != "$REC_LABEL" ]]; then
  LABEL_ENC=$(printf "SELECT Id FROM EnablementCompetencyDef WHERE MasterLabel='%s' AND Id!='%s'" \
    "$(soql_escape "$NEW_LABEL")" "$REC_ID" | jq -sRr @uri)
  DUP=$( (sf api request rest "${TOOLING_BASE}/query/?q=${LABEL_ENC}" --target-org "$ORG_ALIAS" 2>/dev/null || true) \
    | jq -r '.totalSize // 0' 2>/dev/null)
  DUP="${DUP:-0}"
  if [[ "$DUP" != "0" ]]; then
    echo "Another competency already uses label '$NEW_LABEL' — refusing to duplicate."
    echo "   Choose a different label, or edit the existing record instead."
    exit 1
  fi
fi

# ---------------------------------------------------------------------------
# Build PATCH payload
# ---------------------------------------------------------------------------
PAYLOAD='{}'
if [[ -n "$NEW_LABEL" ]]; then
  PAYLOAD=$(echo "$PAYLOAD" | jq --arg v "$NEW_LABEL" '. + {MasterLabel: $v}')
fi
if [[ -n "$NEW_INSTRUCTIONS" ]]; then
  PAYLOAD=$(echo "$PAYLOAD" | jq --arg v "$NEW_INSTRUCTIONS" '. + {EvaluationInstructions: $v}')
fi
if [[ -n "$NEW_DESCRIPTION" ]]; then
  PAYLOAD=$(echo "$PAYLOAD" | jq --arg v "$NEW_DESCRIPTION" '. + {Description: $v}')
fi

# sf api request rest exits non-zero on HTTP failure; success on Tooling
# PATCH is HTTP 204 (empty body). Capture both stdout and exit status.
if RESP_BODY=$(sf api request rest "${TOOLING_BASE}/sobjects/EnablementCompetencyDef/${REC_ID}" \
    --target-org "$ORG_ALIAS" \
    --method PATCH \
    --header 'Content-Type: application/json' \
    --body "$PAYLOAD" \
    2>&1); then
  if [[ -n "$NEW_LABEL" && "$NEW_LABEL" != "$REC_LABEL" ]]; then
    echo "Renamed '$REC_LABEL' → '$NEW_LABEL'"
  else
    echo "Updated $REC_LABEL"
  fi
  [[ -n "$NEW_INSTRUCTIONS" ]] && echo "   EvaluationInstructions: ${#NEW_INSTRUCTIONS} chars"
  [[ -n "$NEW_DESCRIPTION" ]]  && echo "   Description:            ${#NEW_DESCRIPTION} chars"
  exit 0
else
  echo "Error: PATCH failed"
  echo "   $RESP_BODY"
  exit 1
fi
