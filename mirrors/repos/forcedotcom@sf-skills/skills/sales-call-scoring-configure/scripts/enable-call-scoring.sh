#!/bin/bash

# Enable Call Coaching (a.k.a. AI Call Scoring / Coaching Competencies) on a
# Salesforce org via SOAP Metadata API.
#
# Handles the PRD-scoped org states for the ECI arm:
#   1. Not available          → refuse with PRD-verbatim message.
#   2. Available, not enabled → enable Einstein GenAI if off, flip
#                               enableECICallScoring.
#   3. Enabled, no competencies → exit 0 with "ready for competency setup".
#   4. Enabled, competencies exist → exit 0 with "already enabled, N competencies".
#
# River Rush (Momentum) arm detection is deferred until that arm goes live —
# see SKILL.md. Re-add it as a 5th state / advisory when it does.
#
# Usage: ./enable-call-scoring.sh <org-alias>

set -euo pipefail

export NO_COLOR=1
export FORCE_COLOR=0

ORG_ALIAS="${1:-}"

if [[ -z "$ORG_ALIAS" ]]; then
  echo "Error: Missing org alias"
  echo "Usage: $0 <org-alias>"
  exit 1
fi

echo "Enabling Call Coaching for org: $ORG_ALIAS"
echo ""

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=shared/auth.sh
source "$SCRIPT_DIR/shared/auth.sh"

# SOAP Metadata API embeds the session token in the request body (see
# soap_read below). This is the only caller in the skill that still needs
# the raw ACCESS_TOKEN in shell scope — everything else goes through
# `sf api request rest`. See shared/auth.sh header for the rationale.
resolve_org_auth_with_token "$ORG_ALIAS" || exit 1

# Deliberately no "Org ID: ..." / "Instance URL: ..." banner here — those are
# admin-comms leaks (rule #5). The org alias is already the admin's mental
# handle; the record Id and pod URL belong in --verbose debug output only.

# ---------------------------------------------------------------------------
# Phase 0: ECI purchase gate — ConversationPilot OrgPermission
# ---------------------------------------------------------------------------
# ConversationPilot reflects whether the org is licensed for Einstein
# Conversation Insights at all, independent of whether an admin has flipped
# enableCallCoaching on in Setup. Checking it first lets us tell "you don't
# have ECI, go buy it" apart from "you have ECI, just turn it on" instead of
# inferring a license gap from a readMetadata fault on enableCallCoaching.
#
# Some org shapes (older sandboxes, non-EinsteinConversationInsights-provisioned
# orgs) reject the OrganizationSettingsDetail query with INVALID_TYPE. That's
# not a licensing signal — it's a metadata-availability signal. Treat any
# non-conclusive result as "unknown, defer to SOAP" and only refuse when the
# query explicitly comes back "false" (W-24022554).
CONVERSATIONPILOT_ENABLED=""
if CONVERSATIONPILOT_RAW=$(sf data query --target-org "$ORG_ALIAS" --use-tooling-api \
    --query "SELECT SettingValue FROM OrganizationSettingsDetail WHERE SettingName='ConversationPilot' AND DataType='OrgPermissionSettings'" \
    --json 2>/dev/null); then
  CONVERSATIONPILOT_JSON=$(echo "$CONVERSATIONPILOT_RAW" | awk '/^{/,EOF')
  if echo "$CONVERSATIONPILOT_JSON" | jq -e '.status == 0' >/dev/null 2>&1; then
    CONVERSATIONPILOT_ENABLED=$(echo "$CONVERSATIONPILOT_JSON" | jq -r '.result.records[0].SettingValue // empty')
  fi
fi

if [[ "$CONVERSATIONPILOT_ENABLED" == "false" ]]; then
  echo "Call Coaching couldn't be turned on because this org doesn't have Einstein Conversation"
  echo "   Insights, which is required to use Call Coaching. To proceed, an admin can go to Setup →"
  echo "   Salesforce Go → Einstein Conversation Insights, or contact their sales representative,"
  echo "   to understand how to purchase ECI."
  exit 1
fi
# If unknown (query rejected / no row), skip this pre-check and let the SOAP
# state detection below classify the org. TYPE_UNAVAILABLE on the SOAP read
# is the authoritative "you need Agentforce for Sales" signal.

# enableECICallScoring exposes at v68+ only.
SOAP_ENDPOINT="${INSTANCE_URL}/services/Soap/m/68.0"

# Bounds every curl call below so a hung network call can't stall the run
# indefinitely. 30s matches the Pipeline reference skill's setup-all.sh
# CURL_TIMEOUT — the only existing timeout precedent in this repo's
# SOAP-calling scripts.
readonly CURL_TIMEOUT=30

# ---------------------------------------------------------------------------
# SOAP helpers
# ---------------------------------------------------------------------------
# shellcheck source=shared/soap.sh
source "$SCRIPT_DIR/shared/soap.sh"

soap_read() {
  local settings_type="$1"
  local full_name="$2"
  soap_call "readMetadata" "<?xml version='1.0' encoding='utf-8'?>
<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:met='http://soap.sforce.com/2006/04/metadata'>
  <soapenv:Header><met:SessionHeader><met:sessionId>${ACCESS_TOKEN}</met:sessionId></met:SessionHeader></soapenv:Header>
  <soapenv:Body><met:readMetadata><met:type>${settings_type}</met:type><met:fullNames>${full_name}</met:fullNames></met:readMetadata></soapenv:Body>
</soapenv:Envelope>"
}

# classify_field / normalize_class / describe_failure now live in
# shared/soap.sh (sourced above) so install-ootb-competencies.sh's SOAP
# fallback can reuse them without duplicating this logic.

# ---------------------------------------------------------------------------
# Availability detection: read all three settings + count competencies.
# ---------------------------------------------------------------------------
echo "Detecting org state..."
echo ""

CI_RAW=$(soap_read "ConversationalIntelligenceSettings" "ConversationalIntelligence")
ECI_CLASS=$(classify_field "$CI_RAW" "enableCallCoaching")
CS_CLASS=$(classify_field "$CI_RAW" "enableECICallScoring")
ECI_ENABLED=$(normalize_class "$ECI_CLASS")
CALL_SCORING_ENABLED=$(normalize_class "$CS_CLASS")

GENAI_RAW=$(soap_read "EinsteinGptSettings" "EinsteinGpt")
GENAI_CLASS=$(classify_field "$GENAI_RAW" "enableEinsteinGptPlatform")
GENAI_ENABLED=$(normalize_class "$GENAI_CLASS")

# River Rush (Momentum) detection deferred until that arm goes live.

# Competency count via Tooling API. (sf may prepend a warning to stdout; strip.)
COMPETENCY_COUNT=""
if COMP_RAW=$(sf data query --target-org "$ORG_ALIAS" --use-tooling-api \
    --query "SELECT COUNT() FROM EnablementCompetencyDef" --json 2>/dev/null); then
  COMP_JSON=$(echo "$COMP_RAW" | awk '/^{/,EOF')
  COMPETENCY_COUNT=$(echo "$COMP_JSON" | jq -r '.result.totalSize // empty' 2>/dev/null || echo "")
fi

echo "  Einstein Conversation Insights:       ${ECI_ENABLED:-unknown}"
echo "  Einstein Generative AI Platform:      ${GENAI_ENABLED:-unknown}"
echo "  Call Coaching:                        ${CALL_SCORING_ENABLED:-unknown}"
echo "  Configured competencies:              ${COMPETENCY_COUNT:-unknown}"
echo ""

# ---------------------------------------------------------------------------
# State machine (PRD § "Behavior by org state")
# ---------------------------------------------------------------------------

# State 1a: NOT AVAILABLE — CI settings unreadable. Distinguish *why*: a
# confirmed licensing gap (TYPE_UNAVAILABLE) is a different admin action than
# a transient auth/network failure, which should be retried, not reported as
# "you need Agentforce for Sales."
if [[ -z "$ECI_ENABLED" ]]; then
  case "$ECI_CLASS" in
    TYPE_UNAVAILABLE:*)
      echo "AI call coaching is not available in this org and they need Agentforce for Sales."
      echo ""
      echo "   (This skill covers Einstein Conversation Insights (ECI) orgs only —"
      echo "    the org's ECI license appears to be missing.)"
      ;;
    AUTH_ERROR:*)
      echo "Could not check org state — authentication/permission error:"
      echo "   ${ECI_CLASS#AUTH_ERROR:}"
      echo ""
      echo "   Verify the CLI session is valid (sf org login web --alias $ORG_ALIAS) and re-run."
      ;;
    *)
      echo "Could not reach Salesforce to check org state (network/timeout error)."
      echo "   Try again in a moment; if it persists, check the org's availability."
      ;;
  esac
  exit 1
fi

# State 4: ENABLED, competencies exist.
if [[ "$CALL_SCORING_ENABLED" == "true" && -n "$COMPETENCY_COUNT" && "$COMPETENCY_COUNT" -gt 0 ]]; then
  echo "Call Coaching is already enabled — $COMPETENCY_COUNT competency record(s) exist."
  echo "   Ready for edit / deactivate / create-new / improvement-suggestion flows."
  echo ""
  echo "Next: $SCRIPT_DIR/list-competencies.sh \"$ORG_ALIAS\""
  exit 0
fi

# State 3.5: ENABLED, competency count unreadable. Distinguish "we couldn't
# read the count" from "the count is genuinely zero" — falling into State 3
# tells the admin "no competencies configured" when the org may actually
# have several. Route to list-competencies to let the admin see the truth.
if [[ "$CALL_SCORING_ENABLED" == "true" && -z "$COMPETENCY_COUNT" ]]; then
  echo "Call Coaching is already enabled — competency count could not be read."
  echo "   Ready for edit / deactivate / create-new flows."
  echo ""
  echo "Next: $SCRIPT_DIR/list-competencies.sh \"$ORG_ALIAS\" (to inspect the configured set)"
  exit 0
fi

# State 3: ENABLED, no competencies.
if [[ "$CALL_SCORING_ENABLED" == "true" ]]; then
  echo "Call Coaching is already enabled — no competencies configured yet."
  echo "   Ready for OOTB competency install / custom competency creation."
  echo ""
  echo "Next: $SCRIPT_DIR/install-ootb-competencies.sh --list (show the OOTB set, then ask OOTB vs custom)"
  exit 0
fi

# State 2: AVAILABLE, NOT ENABLED — enable path.

# 2a-pre. License gate — catch unlicensed orgs BEFORE the "ECI not enabled"
# refusal below. ConversationalIntelligenceSettings returns HTTP 200 with
# enableCallCoaching=false on BOTH licensed-ECI-off and genuinely unlicensed
# orgs (the two are indistinguishable at that read), so State 1a above
# doesn't catch the unlicensed case. EinsteinGptSettings faulting with
# TYPE_UNAVAILABLE is the strongest license-gap signal we have without
# doing a write — Einstein GenAI Platform is a hard prerequisite for AI
# Call Scoring, so an org that can't even see that settings type won't be
# able to enable Call Coaching regardless of what the ECI toggle says.
# W-24026047.
#
# Not perfect: an org could have the GenAI platform present but still lack
# the specific Call Scoring license. State 2c's ECICallScoringAI
# OrgPermission check catches that residual case after GenAI is enabled.
if [[ "$GENAI_CLASS" == TYPE_UNAVAILABLE:* ]]; then
  echo "AI call coaching is not available in this org."
  echo ""
  echo "   You need Agentforce for Sales to enable AI Call Scoring."
  echo "   Without Agentforce for Sales, you can still set up manual call scoring"
  echo "   by navigating to Salesforce Go setup in your org."
  exit 1
fi

echo "State: AVAILABLE, NOT ENABLED — proceeding with enable flow."
echo ""

# 2a. License gate — ECICallScoringAI OrgPermission is the authoritative
# license signal and must be checked BEFORE the "ECI not enabled" refusal
# below. ConversationalIntelligenceSettings reads enableCallCoaching=false on
# BOTH a licensed-but-toggled-off org and a genuinely unlicensed one — those
# are indistinguishable at that read. Checking here, ahead of 2b, prevents a
# no-license org from being misdiagnosed as "just flip ECI in Setup" (a
# regression this skill's eval guards against — see the NoLicense dataset).
ECICALLSCORINGAI_ENABLED=""
if ECICALLSCORINGAI_RAW=$(sf data query --target-org "$ORG_ALIAS" --use-tooling-api \
    --query "SELECT SettingValue FROM OrganizationSettingsDetail WHERE SettingName='ECICallScoringAI' AND DataType='OrgPermissionSettings'" \
    --json 2>/dev/null); then
  ECICALLSCORINGAI_JSON=$(echo "$ECICALLSCORINGAI_RAW" | awk '/^{/,EOF')
  if echo "$ECICALLSCORINGAI_JSON" | jq -e '.status == 0' >/dev/null 2>&1; then
    ECICALLSCORINGAI_ENABLED=$(echo "$ECICALLSCORINGAI_JSON" | jq -r '.result.records[0].SettingValue // "false"')
  fi
fi

if [[ -z "$ECICALLSCORINGAI_ENABLED" ]]; then
  echo "Could not determine AI call coaching license state — ECICallScoringAI query failed."
  echo "   Verify the CLI session is valid (sf org login web --alias $ORG_ALIAS) and re-run."
  exit 1
fi

if [[ "$ECICALLSCORINGAI_ENABLED" != "true" ]]; then
  echo "AI call coaching is not available in this org and org requires Agentforce for Sales license."
  exit 1
fi

# 2b. ECI must be enabled — this skill is ECI-only.
if [[ "$ECI_ENABLED" != "true" ]]; then
  echo "Error: ECI (Einstein Conversation Insights) is not enabled."
  echo "   Setup → Salesforce Go → Einstein Conversation Insights → Turn ON, then re-run."
  exit 1
fi

# 2c. Enable Einstein GenAI if off (PRD explicitly authorizes this).
if [[ "$GENAI_ENABLED" != "true" ]]; then
  echo "Enabling Einstein Generative AI Platform (required for AI scoring)..."
  GENAI_ENABLE_REQ=$(cat <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
  <soapenv:Header>
    <met:SessionHeader><met:sessionId>{{ACCESS_TOKEN}}</met:sessionId></met:SessionHeader>
  </soapenv:Header>
  <soapenv:Body>
    <met:updateMetadata>
      <met:metadata xsi:type="met:EinsteinGptSettings" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <met:fullName>EinsteinGpt</met:fullName>
        <met:enableEinsteinGptPlatform>true</met:enableEinsteinGptPlatform>
      </met:metadata>
    </met:updateMetadata>
  </soapenv:Body>
</soapenv:Envelope>
EOF
)
  GENAI_ENABLE_REQ="${GENAI_ENABLE_REQ//\{\{ACCESS_TOKEN\}\}/$ACCESS_TOKEN}"
  GENAI_RESULT=$(classify_field "$(soap_call "update" "$GENAI_ENABLE_REQ")" "success")
  if [[ "$GENAI_RESULT" == "true" ]]; then
    echo "   Einstein GenAI enabled"
  else
    case "$GENAI_RESULT" in
      TYPE_UNAVAILABLE:*|false)
        # Org isn't licensed for EinsteinGptSettings, or the update was
        # explicitly refused with no fault and no <errors> detail — either
        # way, this is a licensing gap, not a transient error, so point at
        # the actual fix instead of telling the admin to just retry.
        echo "   Einstein Generative AI Platform cannot be enabled — $(describe_failure "$GENAI_RESULT")."
        echo ""
        echo "   You need Agentforce for Sales to enable AI Call Scoring."
        echo "   Without Agentforce for Sales, you can still set up manual call scoring"
        echo "   by navigating to Salesforce Go setup in your org."
        ;;
      UPDATE_REJECTED:*)
        # Salesforce returned success=false with an <errors> block — surface
        # the actual statusCode/message instead of guessing at a cause.
        echo "   Einstein GenAI enable failed: $(describe_failure "$GENAI_RESULT")"
        ;;
      AUTH_ERROR:*)
        echo "   Einstein GenAI enable failed: $(describe_failure "$GENAI_RESULT")"
        echo ""
        echo "   Verify the CLI session is valid (sf org login web --alias $ORG_ALIAS) and re-run."
        ;;
      *)
        echo "   Einstein GenAI enable failed: $(describe_failure "$GENAI_RESULT")"
        echo ""
        echo "   Try again in a moment; if it persists, check the org's availability."
        ;;
    esac
    exit 1
  fi
  echo ""
else
  echo "Einstein Generative AI Platform is already enabled — skipping."
  echo ""
fi

# Enable Call Coaching (enableECICallScoring) — skip the update if it's
# already on (state detection above only short-circuits when competencies
# also exist; an org can have enableECICallScoring=true with zero
# competencies and still reach here if that read raced with an out-of-band
# change).
if [[ "$CALL_SCORING_ENABLED" != "true" ]]; then
  echo "Enabling Call Coaching..."
  CS_ENABLE_REQ=$(cat <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata">
  <soapenv:Header>
    <met:SessionHeader><met:sessionId>{{ACCESS_TOKEN}}</met:sessionId></met:SessionHeader>
  </soapenv:Header>
  <soapenv:Body>
    <met:updateMetadata>
      <met:metadata xsi:type="met:ConversationalIntelligenceSettings" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <met:fullName>ConversationalIntelligence</met:fullName>
        <met:enableECICallScoring>true</met:enableECICallScoring>
      </met:metadata>
    </met:updateMetadata>
  </soapenv:Body>
</soapenv:Envelope>
EOF
)
  CS_ENABLE_REQ="${CS_ENABLE_REQ//\{\{ACCESS_TOKEN\}\}/$ACCESS_TOKEN}"
  CS_RESULT=$(classify_field "$(soap_call "update" "$CS_ENABLE_REQ")" "success")

  if [[ "$CS_RESULT" == "true" ]]; then
    echo "   Call Coaching enabled"
  else
    # ECI enablement is asynchronous — for a short window after the ECI toggle
    # flips on, the dependent enableECICallScoring field is server-side
    # read-only and updateMetadata returns INSUFFICIENT_ACCESS_OR_READONLY.
    # This is a transient state that self-resolves in a few minutes, not a
    # permanent failure — surface a wait-and-retry message instead of the
    # generic error. W-23968462.
    case "$CS_RESULT" in
      WRITE_ERROR:INSUFFICIENT_ACCESS_OR_READONLY*)
        echo "   Einstein Conversation Insights is still finishing turning on."
        echo "      Wait a few minutes, then re-run this to enable Call Coaching."
        ;;
      *)
        echo "   Call Coaching enable failed: $(describe_failure "$CS_RESULT")"
        ;;
    esac
    exit 1
  fi
else
  echo "Call Coaching is already enabled — skipping."
fi

echo ""

# Enable the CallCoachingReady OrgPermission — not a Metadata API type, so
# it's flipped via Tooling API PATCH on OrganizationSettingsDetail (the same
# object the OrgPermission reads above use), looked up by Id first.
CCR_LOOKUP=$(sf api request rest \
  "services/data/v68.0/tooling/query/?q=SELECT+Id,SettingValue+FROM+OrganizationSettingsDetail+WHERE+SettingName='CallCoachingReady'+AND+DataType='OrgPermissionSettings'" \
  --target-org "$ORG_ALIAS" 2>/dev/null) || true

CCR_COUNT=$(echo "$CCR_LOOKUP" | jq -r '.totalSize // 0' 2>/dev/null || echo 0)
if [[ "$CCR_COUNT" == "0" ]]; then
  echo "Could not locate the CallCoachingReady OrgPermission record on this org."
  exit 1
fi

CCR_ID=$(echo "$CCR_LOOKUP" | jq -r '.records[0].Id')
CCR_CURRENT=$(echo "$CCR_LOOKUP" | jq -r '.records[0].SettingValue')

if [[ "$CCR_CURRENT" == "true" ]]; then
  echo "CallCoachingReady is already enabled — skipping."
else
  echo "Enabling CallCoachingReady..."
  if CCR_PATCH_RESP=$(sf api request rest \
      "services/data/v68.0/tooling/sobjects/OrganizationSettingsDetail/${CCR_ID}" \
      --target-org "$ORG_ALIAS" \
      --method PATCH \
      --header 'Content-Type: application/json' \
      --body '{"SettingValue": true}' \
      2>/dev/null); then
    echo "   CallCoachingReady enabled"
  else
    echo "   Failed to enable CallCoachingReady"
    echo "   $CCR_PATCH_RESP"
    exit 1
  fi
fi

echo ""

# 2d. Verify.
echo "Verifying..."
sleep 2
VERIFY_CLASS=$(classify_field "$(soap_read "ConversationalIntelligenceSettings" "ConversationalIntelligence")" "enableECICallScoring")

if [[ "$VERIFY_CLASS" == "true" ]]; then
  echo "   Confirmed: Call Coaching is now enabled"
  echo ""
  echo "Call Coaching enabled. Ready for OOTB competency install / custom creation."
  echo ""
  echo "Next: $SCRIPT_DIR/install-ootb-competencies.sh --list (show the OOTB set, then ask OOTB vs custom)"
  exit 0
else
  echo "   Error: Verification failed: $(describe_failure "$VERIFY_CLASS")"
  exit 1
fi
