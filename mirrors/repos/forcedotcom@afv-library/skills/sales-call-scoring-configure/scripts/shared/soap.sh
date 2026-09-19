#!/bin/bash
# Shared library for SOAP Metadata API response parsing
#
# Functions:
#   redact_token <input> - Redacts session IDs and Bearer tokens from error messages
#   parse_soap_response <xml> <field> <http_status> - Classifies SOAP responses
#
# Returns:
#   "true" - field is enabled
#   "false" - field is explicitly disabled or omitted (setting is off)
#   "AUTH_ERROR:<fault>" - authentication/authorization failure
#   "TYPE_UNAVAILABLE:<fault>" - org lacks license/edition for this feature
#   "WRITE_ERROR:<statusCode>[:<message>]" - updateMetadata returned a well-formed
#       response with <success>false</success> and an <errors> block. The server
#       accepted the request and reports a specific reason for refusal (e.g.
#       INSUFFICIENT_ACCESS_OR_READONLY during a provisioning window). Callers
#       decide whether the statusCode is transient (retryable) or terminal.
#   "NETWORK_ERROR" - network/service error (empty response, 5xx, malformed XML)

# Redact session IDs and Bearer tokens from error messages
# Args: $1 = input string
# Returns: string with tokens replaced by [REDACTED]
#
# Salesforce session IDs start with the 15/18-char org id (00D...) followed by
# '!' and a signature segment that contains '.', '=', '-', '+' in addition to
# alphanumerics. Match greedily up to the next whitespace or XML tag boundary
# ('<') so the whole token tail is redacted, not just its leading run.
redact_token() {
  local input="$1"
  printf '%s' "$input" | sed 's/00D[^ <]*/[REDACTED]/g; s/Bearer [^ ]*/Bearer [REDACTED]/g'
}

# Parse SOAP Metadata API response and classify the result
# Args:
#   $1 = raw SOAP XML response
#   $2 = field name to extract (e.g., "enableEinsteinGptPlatform")
#   $3 = HTTP status code (e.g., "200", "503")
# Returns: classification string (see header comments)
parse_soap_response() {
  local xml_response="$1"
  local field_name="$2"
  local http_status="$3"

  # Validate field_name to prevent regex injection in grep patterns below
  if [[ ! "$field_name" =~ ^[A-Za-z0-9_]+$ ]]; then
    echo "NETWORK_ERROR"
    return 0
  fi

  # Disable pipefail locally to allow grep failures without aborting
  local old_opts="$-"
  set +e

  # An empty response body is always a network error, regardless of status.
  if [[ -z "$xml_response" ]]; then
    # Restore pipefail before returning
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "NETWORK_ERROR"
    return 0
  fi

  # Check for SOAP Fault (auth, permission, or type errors) *before* the
  # generic non-2xx-status check below — Salesforce commonly returns real
  # SOAP Faults (invalid session, insufficient access, unlicensed type) with
  # an HTTP 500 status, so gating on status first would silently reclassify
  # every such fault as a generic "network/timeout error" and hide the
  # actual auth/licensing diagnosis from the admin.
  # Handle both standard and namespace-prefixed faults
  local fault_code=""
  if echo "$xml_response" | grep -q "<soapenv:Fault>\\|<sf:Fault>\\|<Fault>"; then
    # Extract faultcode - try multiple patterns for different namespace conventions
    fault_code=$(echo "$xml_response" | grep -o "<faultcode>[^<]*</faultcode>" | sed 's/<[^>]*>//g' | head -1)
    if [[ -z "$fault_code" ]]; then
      fault_code=$(echo "$xml_response" | grep -o "<sf:faultcode>[^<]*</sf:faultcode>" | sed 's/<[^>]*>//g' | head -1)
    fi
    if [[ -z "$fault_code" ]]; then
      # Handle fully-qualified fault codes like "sf:INVALID_SESSION_ID"
      fault_code=$(echo "$xml_response" | grep -oE "faultcode>[^<]*</.*faultcode" | sed 's/<[^>]*>//g' | sed 's/.*://' | head -1)
    fi

    if [[ -n "$fault_code" ]]; then
      # Extract faultstring for context (will be redacted)
      local fault_string=""
      fault_string=$(echo "$xml_response" | grep -o "<faultstring>[^<]*</faultstring>" | sed 's/<[^>]*>//g' | head -1 || echo "")
      if [[ -z "$fault_string" ]]; then
        fault_string=$(echo "$xml_response" | grep -o "<sf:faultstring>[^<]*</sf:faultstring>" | sed 's/<[^>]*>//g' | head -1 || echo "")
      fi

      # Redact tokens from fault string
      if [[ -n "$fault_string" ]]; then
        fault_string=$(redact_token "$fault_string")
      fi

      # Classify by fault type
      # INVALID_TYPE = org lacks license/edition - distinct from auth failures
      if echo "$fault_code" | grep -qi "INVALID_TYPE"; then
        if [[ "$old_opts" =~ e ]]; then set -e; fi
        echo "TYPE_UNAVAILABLE:${fault_code}${fault_string:+:$fault_string}"
        return 0
      fi

      # All other faults are auth/permission errors
      if [[ "$old_opts" =~ e ]]; then set -e; fi
      echo "AUTH_ERROR:${fault_code}${fault_string:+:$fault_string}"
      return 0
    fi
  fi

  # No fault matched above — a non-2xx status at this point is a genuine
  # network/service error (not a classifiable SOAP-level failure).
  if [[ "$http_status" != "200" && "$http_status" != "201" ]]; then
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "NETWORK_ERROR"
    return 0
  fi

  # Check if response is valid XML with the expected structure
  # If it's HTML or malformed XML, treat as network error
  if ! echo "$xml_response" | grep -q "<readMetadataResponse>\\|<updateMetadataResponse>"; then
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "NETWORK_ERROR"
    return 0
  fi

  # Check for closing envelope tag - if missing, XML is truncated
  if ! echo "$xml_response" | grep -q "</soapenv:Envelope>"; then
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "NETWORK_ERROR"
    return 0
  fi

  # Well-formed updateMetadataResponse with an <errors> block: the server
  # accepted the request, reports success=false, and names the reason via
  # <statusCode> (e.g. INSUFFICIENT_ACCESS_OR_READONLY when a dependent field
  # is temporarily read-only during ECI's async provisioning window — see
  # W-23968462). Without this branch, the fallback field-value grep below
  # would find <success>false</success> and collapse to bare "false", losing
  # the statusCode the admin needs to distinguish transient from terminal.
  # Scoped to updateMetadataResponse to avoid a false positive on readMetadata
  # responses that happen to contain an <errors> element in metadata content.
  if echo "$xml_response" | grep -q "<updateMetadataResponse>" \
     && echo "$xml_response" | grep -q "<errors>"; then
    local status_code=""
    local err_message=""
    status_code=$(echo "$xml_response" | grep -o "<statusCode>[^<]*</statusCode>" | sed 's/<[^>]*>//g' | head -1)
    err_message=$(echo "$xml_response" | grep -o "<message>[^<]*</message>" | sed 's/<[^>]*>//g' | head -1)
    if [[ -n "$err_message" ]]; then
      err_message=$(redact_token "$err_message")
    fi
    if [[ -n "$status_code" ]]; then
      if [[ "$old_opts" =~ e ]]; then set -e; fi
      echo "WRITE_ERROR:${status_code}${err_message:+:$err_message}"
      return 0
    fi
  fi

  # Extract field value - try to find <field>true/false</field>
  # head -1 collapses multi-record responses to the first match so two records
  # never produce a two-line value that fails the == comparisons below.
  local field_value=""
  field_value=$(echo "$xml_response" | grep -o "<${field_name}>[^<]*</${field_name}>" | grep -o "true\\|false" | head -1 || echo "")

  if [[ "$field_value" == "true" ]]; then
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "true"
    return 0
  fi

  # An update call reporting success=false has no SOAP fault, but the
  # response still carries an <errors> block (statusCode + message) with the
  # actual reason — e.g. INSUFFICIENT_ACCESS_OR_READONLY. Surface it instead
  # of silently collapsing to a bare "false" the caller can't act on.
  if [[ "$field_name" == "success" && "$field_value" == "false" ]]; then
    local err_status_code="" err_message=""
    err_status_code=$(echo "$xml_response" | grep -o "<statusCode>[^<]*</statusCode>" | sed 's/<[^>]*>//g' | head -1)
    if [[ -z "$err_status_code" ]]; then
      err_status_code=$(echo "$xml_response" | grep -o "<sf:statusCode>[^<]*</sf:statusCode>" | sed 's/<[^>]*>//g' | head -1)
    fi
    err_message=$(echo "$xml_response" | grep -o "<message>[^<]*</message>" | sed 's/<[^>]*>//g' | head -1)
    if [[ -z "$err_message" ]]; then
      err_message=$(echo "$xml_response" | grep -o "<sf:message>[^<]*</sf:message>" | sed 's/<[^>]*>//g' | head -1)
    fi
    if [[ -n "$err_message" ]]; then
      err_message=$(redact_token "$err_message")
    fi
    if [[ -n "$err_status_code" || -n "$err_message" ]]; then
      if [[ "$old_opts" =~ e ]]; then set -e; fi
      echo "UPDATE_REJECTED:${err_status_code:-UNKNOWN}${err_message:+:$err_message}"
      return 0
    fi
  fi

  # If field is explicitly false OR field is omitted entirely, treat as disabled.
  # Salesforce omits boolean settings fields when they're off rather than
  # emitting <field>false</field>, so an absent field inside an otherwise valid
  # readMetadataResponse is the disabled state, not an error.
  if [[ "$field_value" == "false" ]] || [[ -z "$field_value" ]]; then
    if [[ "$old_opts" =~ e ]]; then set -e; fi
    echo "false"
    return 0
  fi

  # Shouldn't reach here, but if we do, treat as network error (unexpected response format)
  if [[ "$old_opts" =~ e ]]; then set -e; fi
  echo "NETWORK_ERROR"
  return 0
}

# Issues one SOAP Metadata API call. Requires $SOAP_ENDPOINT and
# $CURL_TIMEOUT to be set by the caller (see enable-call-scoring.sh /
# install-ootb-competencies.sh for the standard setup).
# Args: $1 = SOAPAction, $2 = request body
# Body is piped via stdin (-d @-) rather than argv so the SOAP sessionId
# — which embeds the raw ACCESS_TOKEN — is not visible in the OS process
# table (ps / /proc/*/cmdline). See W-23934530 / W-23974869.
soap_call() {
  local action="$1"
  local body="$2"
  # `|| true` — a curl failure (timeout, DNS, refused connection) must not
  # abort the script via set -e; empty output + empty status here falls
  # through to parse_soap_response's NETWORK_ERROR classification below.
  printf '%s' "$body" | curl -s -w '\nHTTPSTATUS:%{http_code}' --max-time "$CURL_TIMEOUT" -X POST "$SOAP_ENDPOINT" \
    -H "Content-Type: text/xml; charset=utf-8" \
    -H "SOAPAction: $action" \
    --data-binary @- 2>/dev/null || true
}

# Splits a soap_call() response into HTTP status + body and classifies one
# field via parse_soap_response. Unlike a plain grep, this distinguishes
# *why* a read/update didn't come back "true": an explicit false/absent
# field, a SOAP fault (auth/permission), an org that isn't licensed for the
# type (INVALID_TYPE), or a network/timeout failure.
# Args: $1 = soap_call() response, $2 = field name
classify_field() {
  local combined="$1"
  local field="$2"
  local http_status body
  # `|| true` on the grep — an empty/malformed $combined (curl failure) has
  # no HTTPSTATUS marker to match, and under pipefail that would otherwise
  # abort the script instead of yielding an empty status for NETWORK_ERROR.
  http_status=$( (echo "$combined" | grep -o 'HTTPSTATUS:[0-9]*$' || true) | cut -d: -f2)
  body=$(echo "$combined" | sed 's/HTTPSTATUS:[0-9]*$//')
  parse_soap_response "$body" "$field" "$http_status"
}

# Normalizes a classify_field() result to true/false, or "" for anything
# that isn't a clean field read (fault/error) — callers that need the fault
# detail should inspect the raw classification themselves.
normalize_class() {
  case "$1" in
    true|false) echo "$1" ;;
    *) echo "" ;;
  esac
}

# Turns a classify_field() classification into a one-line, token-redacted,
# admin-safe explanation of why a call failed.
describe_failure() {
  case "$1" in
    AUTH_ERROR:*) echo "authentication/permission error — ${1#AUTH_ERROR:}" ;;
    TYPE_UNAVAILABLE:*) echo "org isn't licensed for this setting — ${1#TYPE_UNAVAILABLE:}" ;;
    WRITE_ERROR:*) echo "server refused the change — ${1#WRITE_ERROR:}" ;;
    NETWORK_ERROR*) echo "network/timeout error reaching Salesforce — try again" ;;
    false) echo "call succeeded but reported failure (no SOAP fault returned)" ;;
    *) echo "unexpected response: $1" ;;
  esac
}
