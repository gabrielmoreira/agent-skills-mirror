#!/usr/bin/env bash
# REST API version of retrieve_flow.sh - no SF CLI execution dependencies
#
# Retrieve a Flow from a Salesforce org via Tooling API using the 2-step pattern
# from project-codey PR #975:
#   1. GET /tooling/query to resolve Flow version ID from API name
#   2. GET /tooling/sobjects/Flow/{id} to read Metadata JSON
#   3. Convert JSON → XML via json_to_flow_xml.py
#
# Usage: retrieve_flow_rest.sh <FlowApiName> <org-alias> [output-dir]
#   output-dir defaults to /tmp

set -euo pipefail

FLOW_NAME="${1:-}"
ALIAS="${2:-}"
OUT_DIR="${3:-/tmp}"

if [[ -z "$FLOW_NAME" || -z "$ALIAS" ]]; then
  echo "Usage: retrieve_flow_rest.sh <FlowApiName> <org-alias> [output-dir]" >&2
  exit 2
fi

# Validate Flow API name (alphanumeric + underscore, starting with letter)
if ! [[ "$FLOW_NAME" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]]; then
  echo "ERROR: Invalid Flow API name: '$FLOW_NAME'" >&2
  echo "Must be alphanumeric + underscore, starting with a letter." >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

echo "Retrieving Flow '$FLOW_NAME' from org '$ALIAS' via Tooling API..." >&2

# Get access token and instance URL
AUTH_JSON=$(sf org display --target-org "$ALIAS" --json 2>&1)
if [[ $? -ne 0 ]]; then
  echo "ERROR: Failed to authenticate to org '$ALIAS'" >&2
  echo "$AUTH_JSON" >&2
  exit 1
fi

ACCESS_TOKEN=$(echo "$AUTH_JSON" | jq -r '.result.accessToken // empty')
INSTANCE_URL=$(echo "$AUTH_JSON" | jq -r '.result.instanceUrl // empty')

if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
  echo "ERROR: Could not get access token for org '$ALIAS'" >&2
  echo "Run: sf org login web --alias $ALIAS" >&2
  exit 1
fi

if [[ -z "$INSTANCE_URL" || "$INSTANCE_URL" == "null" ]]; then
  echo "ERROR: Could not get instance URL for org '$ALIAS'" >&2
  exit 1
fi

# Put the auth header in a curl config file rather than -H argv: command-line
# arguments are visible to any local user via `ps`/`/proc` and would leak the
# access token, and argv would also show up in a `set -x` trace.
umask 077
TEMP_JSON=""
CURL_CFG=$(mktemp -t flow-curl-cfg.XXXXXX)
cleanup() { rm -f "${CURL_CFG:-}" "${TEMP_JSON:-}" 2>/dev/null || true; }
trap cleanup EXIT
XTRACE_WAS_ON=0
case "$-" in *x*) XTRACE_WAS_ON=1; set +x ;; esac
{
  printf 'header = "Authorization: Bearer %s"\n' "$ACCESS_TOKEN"
  echo 'header = "Content-Type: application/json"'
} > "$CURL_CFG"
[[ "$XTRACE_WAS_ON" -eq 1 ]] && set -x
unset ACCESS_TOKEN

# Step 1: Resolve Flow version ID from API name
echo "  [1/3] Resolving Flow version ID..." >&2

SOQL="SELECT Id, LatestVersionId, ActiveVersionId FROM FlowDefinition WHERE DeveloperName='${FLOW_NAME}'"
ENCODED_SOQL=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''${SOQL}'''))")

QUERY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  "${INSTANCE_URL}/services/data/v67.0/tooling/query?q=${ENCODED_SOQL}" \
  --config "$CURL_CFG")

HTTP_CODE=$(echo "$QUERY_RESPONSE" | tail -n1)
BODY=$(echo "$QUERY_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "ERROR: Tooling API query failed (HTTP $HTTP_CODE)" >&2
  echo "$BODY" | jq -r '.[0].message // .message // "Unknown error"' >&2
  exit 1
fi

RECORD_COUNT=$(echo "$BODY" | jq -r '.totalSize // 0')
if [[ "$RECORD_COUNT" -eq 0 ]]; then
  echo "ERROR: Flow '$FLOW_NAME' not found in org '$ALIAS'" >&2
  echo "Check the Flow API name and ensure it exists in the org." >&2
  exit 1
fi

VERSION_ID=$(echo "$BODY" | jq -r '.records[0].LatestVersionId // empty')
if [[ -z "$VERSION_ID" || "$VERSION_ID" == "null" ]]; then
  echo "ERROR: FlowDefinition found but LatestVersionId is null" >&2
  echo "$BODY" | jq '.' >&2
  exit 1
fi

echo "  [1/3] Resolved Flow version ID: $VERSION_ID" >&2

# Step 2: Read Metadata JSON
echo "  [2/3] Reading Flow Metadata JSON..." >&2

METADATA_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  "${INSTANCE_URL}/services/data/v67.0/tooling/sobjects/Flow/${VERSION_ID}" \
  --config "$CURL_CFG")

HTTP_CODE=$(echo "$METADATA_RESPONSE" | tail -n1)
BODY=$(echo "$METADATA_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "ERROR: Failed to read Flow Metadata (HTTP $HTTP_CODE)" >&2
  echo "$BODY" | jq -r '.[0].message // .message // "Unknown error"' >&2
  exit 1
fi

METADATA_JSON=$(echo "$BODY" | jq '.Metadata')
if [[ "$METADATA_JSON" == "null" || -z "$METADATA_JSON" ]]; then
  echo "ERROR: Flow response missing 'Metadata' field" >&2
  echo "$BODY" | jq '.' >&2
  exit 1
fi

echo "  [2/3] Retrieved Metadata JSON ($(echo "$METADATA_JSON" | jq -r 'keys | length') top-level keys)" >&2

# Step 3: Convert JSON → XML
echo "  [3/3] Converting JSON to Flow XML..." >&2

TEMP_JSON=$(mktemp -t flow-metadata.XXXXXX.json)

echo "$METADATA_JSON" > "$TEMP_JSON"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_XML="${OUT_DIR}/${FLOW_NAME}.flow-meta.xml"

python3 "${SCRIPT_DIR}/json_to_flow_xml.py" "$TEMP_JSON" "$OUTPUT_XML" 2>&1
if [[ $? -ne 0 ]]; then
  echo "ERROR: JSON to XML conversion failed" >&2
  exit 1
fi

echo "  [3/3] Conversion complete" >&2
echo "" >&2
echo "[OK] Flow retrieved successfully: $OUTPUT_XML" >&2

# Print output path (for script chaining)
echo "$OUTPUT_XML"
