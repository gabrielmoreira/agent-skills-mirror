#!/bin/bash
# sales_call_scoring: story="custom-competency-crud" owner="W-CUSTOM-CRUD"
#
# Fetch a competency's full record, or just a single field. Used by S8
# (improvement suggestions) to load current EvaluationInstructions into
# Claude's context before drafting an edit.
#
# Companion of create-custom-competency.sh — parallel to get-competency.sh
# so the custom-CRUD story can extend it (e.g. --raw json without cleanup,
# --fields Field1,Field2 for multi-field cherry-pick) without touching the
# OOTB-owned read surface.
#
# Usage:
#   ./get-custom-competency.sh <org-alias> <name-or-id>                  # full record JSON
#   ./get-custom-competency.sh <org-alias> <name-or-id> --field <name>   # raw field value

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"
IDENT="${2:-}"
FIELD=""

if [[ -z "$ORG_ALIAS" || -z "$IDENT" ]]; then
  echo "Usage: $0 <org-alias> <name-or-id> [--field <field>]"
  exit 1
fi

if [[ "${3:-}" == "--field" ]]; then
  FIELD="${4:-}"
  if [[ -z "$FIELD" ]]; then
    echo "Error: --field requires a field name"; exit 1
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
# Resolve identifier → record
# ---------------------------------------------------------------------------
if [[ "$IDENT" =~ ^1nA[0-9a-zA-Z]{12,15}$ ]]; then
  WHERE="Id='${IDENT}'"
else
  SAFE=$(soql_escape "$IDENT")
  WHERE="DeveloperName='${SAFE}' OR MasterLabel='${SAFE}'"
fi

QUERY_ENC=$(printf 'SELECT Id, DeveloperName, MasterLabel, Description, IsActive, EvaluationScope, EvaluationConditions, EvaluationInstructions, SourceCompetencyTemplate FROM EnablementCompetencyDef WHERE %s' "$WHERE" | jq -sRr @uri)
LOOKUP=$(sf api request rest "${TOOLING_BASE}/query/?q=${QUERY_ENC}" --target-org "$ORG_ALIAS" 2>/dev/null || true)
RC=$(echo "$LOOKUP" | jq -r '.totalSize // 0' 2>/dev/null || echo "0")

if [[ "$RC" == "0" ]]; then echo "No competency matched: $IDENT" >&2; exit 1; fi
if [[ "$RC" != "1" ]]; then
  echo "Multiple competencies matched '$IDENT':" >&2
  echo "$LOOKUP" | jq -r '.records[] | "   \(.Id)  \(.MasterLabel)"' >&2
  exit 1
fi

RECORD=$(echo "$LOOKUP" | jq '.records[0] | del(.attributes)')

if [[ -n "$FIELD" ]]; then
  echo "$RECORD" | jq -r --arg f "$FIELD" 'if has($f) then .[$f] else "Field not found: \($f)" | halt_error(1) end'
else
  echo "$RECORD"
fi
