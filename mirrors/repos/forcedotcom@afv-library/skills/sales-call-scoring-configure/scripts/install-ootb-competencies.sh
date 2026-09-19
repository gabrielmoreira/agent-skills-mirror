#!/bin/bash

# Install the 6 OOTB Coaching Competencies from PRD-canonical prompt bodies.
# Creates EnablementCompetencyDef records via Tooling API (per its entity XML,
# EnablementCompetencyDef has perApiAccess sobjectFamily="TOOLING" with
# isApiInsertable=true, so this is the sanctioned CRUD surface).
#
# Idempotent: skips any competency whose DeveloperName already exists.
#
# Usage: ./install-ootb-competencies.sh <org-alias> [--dry-run]
#        ./install-ootb-competencies.sh --list

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_FILE="$SCRIPT_DIR/../assets/ootb-competencies.json"

if [[ ! -f "$ASSETS_FILE" ]]; then
  echo "Cannot find $ASSETS_FILE"
  exit 1
fi

# --list is read-only and org-agnostic — it just renders the asset file so
# Claude can show the admin what the OOTB set contains *before* they choose
# between OOTB and custom. No auth needed, no state touched.
if [[ "${1:-}" == "--list" ]]; then
  echo "| Competency | What it evaluates |"
  echo "|---|---|"
  jq -r '.competencies[] | "| " + .MasterLabel + " | " + .Description + " |"' "$ASSETS_FILE"
  exit 0
fi

ORG_ALIAS="${1:-}"
DRY_RUN="${2:-}"

if [[ -z "$ORG_ALIAS" ]]; then
  echo "Error: Missing org alias"
  echo "Usage: $0 <org-alias> [--dry-run]"
  echo "       $0 --list"
  exit 1
fi

echo "Installing OOTB Coaching Competencies on org: $ORG_ALIAS"
if [[ "$DRY_RUN" == "--dry-run" ]]; then
  echo "   (DRY RUN — will not create records)"
fi
echo ""

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"

# Needs the raw ACCESS_TOKEN (not just resolve_org_auth) because the
# Tooling API precheck below can fall back to a SOAP Metadata sessionId
# call — same documented exception as enable-call-scoring.sh.
resolve_org_auth_with_token "$ORG_ALIAS" || exit 1

TOOLING_BASE="services/data/v68.0/tooling"

# shellcheck source=shared/soap.sh
source "$SCRIPT_DIR/shared/soap.sh"

# enableECICallScoring exposes at v68+ only.
SOAP_ENDPOINT="${INSTANCE_URL}/services/Soap/m/68.0"
readonly CURL_TIMEOUT=30

# ---------------------------------------------------------------------------
# Precondition: Call Coaching must be enabled before writing competencies.
# EnablementCompetencyDef inserts aren't rejected server-side when Call
# Coaching is off, so without this check the script would silently create
# orphaned records the admin can't see or use until enable-call-scoring.sh
# runs. Fail fast with a pointer instead.
#
# The Tooling API SOQL query below can throw a hard server-side exception
# (observed: UNKNOWN_EXCEPTION) on some orgs/pods, independent of the
# actual pref value — reproduced 3x over ~95s against callscoring-dev while
# SOAP readMetadata concurrently confirmed enableECICallScoring=true. The
# original code treated any query failure the same as a clean "false" read
# (via `// false`), so a transient/org-specific API exception silently
# collapsed into "Call Coaching is not enabled" even when it demonstrably
# was. Distinguish "query succeeded and says false" (trust it) from "query
# itself errored" (fall back to the same SOAP read enable-call-scoring.sh
# treats as source of truth) rather than conflating the two.
# ---------------------------------------------------------------------------
CALL_SCORING_RAW=$(sf data query --target-org "$ORG_ALIAS" --use-tooling-api \
  --query "SELECT IsEciCallScoringEnabled FROM ConversationalIntelligenceSettings" \
  --json 2>/dev/null) || true
CALL_SCORING_JSON=$(echo "$CALL_SCORING_RAW" | awk '/^{/,EOF')
QUERY_STATUS=$(echo "$CALL_SCORING_JSON" | jq -r '.status // empty' 2>/dev/null)

if [[ "$QUERY_STATUS" == "0" ]]; then
  CALL_SCORING_ENABLED=$(echo "$CALL_SCORING_JSON" | jq -r '.result.records[0].IsEciCallScoringEnabled // false' 2>/dev/null || echo "false")
else
  SOAP_RAW=$(soap_call "readMetadata" "<?xml version='1.0' encoding='utf-8'?>
<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:met='http://soap.sforce.com/2006/04/metadata'>
  <soapenv:Header><met:SessionHeader><met:sessionId>${ACCESS_TOKEN}</met:sessionId></met:SessionHeader></soapenv:Header>
  <soapenv:Body><met:readMetadata><met:type>ConversationalIntelligenceSettings</met:type><met:fullNames>ConversationalIntelligence</met:fullNames></met:readMetadata></soapenv:Body>
</soapenv:Envelope>")
  SOAP_CLASS=$(classify_field "$SOAP_RAW" "enableECICallScoring")
  CALL_SCORING_ENABLED=$(normalize_class "$SOAP_CLASS")

  if [[ -z "$CALL_SCORING_ENABLED" ]]; then
    echo "Could not determine whether Call Coaching is enabled — $(describe_failure "$SOAP_CLASS")."
    exit 1
  fi
fi

if [[ "$CALL_SCORING_ENABLED" != "true" ]]; then
  echo "Call Coaching is not enabled on this org — refusing to install competencies."
  echo "   Run enable-call-scoring.sh first: $SCRIPT_DIR/enable-call-scoring.sh \"$ORG_ALIAS\""
  exit 1
fi

# shellcheck source=shared/cap.sh
source "$SCRIPT_DIR/shared/cap.sh"

# Detect cap state once up-front. New installs land inactive (with a clear
# warning) rather than being refused — the admin can activate later.
CAP_HIT="false"
INITIAL_ACTIVE_COUNT=$(query_active_count "$ORG_ALIAS")
if [[ "$INITIAL_ACTIVE_COUNT" -ge "$MAX_ACTIVE_COMPETENCIES" ]]; then
  print_cap_report "$ORG_ALIAS" "installing OOTB Coaching Competencies"
  echo "    Any new records created by this run will land INACTIVE. Activate them" >&2
  echo "    once you free a slot with toggle-custom-competency.sh." >&2
  echo "" >&2
  CAP_HIT="true"
fi

# ---------------------------------------------------------------------------
# Idempotency: fetch existing DeveloperNames
# ---------------------------------------------------------------------------
EXISTING_RAW=$(sf api request rest "${TOOLING_BASE}/query/?q=SELECT+DeveloperName+FROM+EnablementCompetencyDef" \
  --target-org "$ORG_ALIAS" 2>/dev/null) || true
EXISTING=$(echo "$EXISTING_RAW" | jq -r '.records[]?.DeveloperName // empty' 2>/dev/null || echo "")

# ---------------------------------------------------------------------------
# Iterate competencies
# ---------------------------------------------------------------------------
COUNT=$(jq '.competencies | length' "$ASSETS_FILE")
CREATED=0
SKIPPED=0
FAILED=0

for i in $(seq 0 $((COUNT - 1))); do
  MASTER_LABEL=$(jq -r ".competencies[$i].MasterLabel" "$ASSETS_FILE")
  DEV_NAME_BASE=$(jq -r ".competencies[$i].DeveloperNameBase" "$ASSETS_FILE")
  TEMPLATE=$(jq -r ".competencies[$i].SourceCompetencyTemplate" "$ASSETS_FILE")
  DESCRIPTION=$(jq -r ".competencies[$i].Description" "$ASSETS_FILE")
  INSTRUCTIONS=$(jq -r ".competencies[$i].EvaluationInstructions" "$ASSETS_FILE")
  SCOPE=$(jq -r ".competencies[$i].EvaluationScope" "$ASSETS_FILE")

  # Idempotency check by SourceCompetencyTemplate (canonical OOTB template key).
  # Skips if any record with the same template already exists (regardless of
  # DeveloperName suffix); safer than by-name since names can be renamed.
  ALREADY_INSTALLED=$( (sf api request rest \
    "${TOOLING_BASE}/query/?q=SELECT+Id+FROM+EnablementCompetencyDef+WHERE+SourceCompetencyTemplate='${TEMPLATE}'" \
    --target-org "$ORG_ALIAS" 2>/dev/null || true) | jq -r '.totalSize // 0' 2>/dev/null)
  ALREADY_INSTALLED="${ALREADY_INSTALLED:-0}"

  if [[ "$ALREADY_INSTALLED" != "0" ]]; then
    # No Template enum leak here — rule #5. Idempotency detail lives in --verbose diagnostics only.
    echo "  $MASTER_LABEL — already installed, skipping"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # DeveloperName must be unique. Append a short random suffix to match the
  # naming convention used by the Setup wizard LWC (CCH_<Sanitized>_<hex>).
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
       SourceCompetencyTemplate: $tp,
       Description: $de,
       EvaluationInstructions: $ei,
       EvaluationScope: $sc,
       IsActive: $ia
     }')

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    # No DeveloperName leak here — rule #5.
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
    # No record Id leak on the primary line — rule #5. Calling agent that
    # needs the Id can re-query via list-competencies.sh --verbose or --json.
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
