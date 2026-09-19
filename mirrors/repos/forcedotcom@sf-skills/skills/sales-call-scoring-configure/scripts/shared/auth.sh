#!/bin/bash
# Shared library for org authentication resolution.
#
# Two entry points, deliberately separate:
#
#   resolve_org_auth <alias>            → validate alias, confirm reachable,
#                                         confirm HTTPS. Does NOT extract
#                                         ACCESS_TOKEN. Use this if the caller
#                                         only ever hits Salesforce through
#                                         `sf api request rest --target-org`
#                                         or `sf data query --target-org`,
#                                         which authenticate via the CLI's own
#                                         session and never need the raw token
#                                         in shell scope.
#
#   resolve_org_auth_with_token <alias> → does everything above, PLUS extracts
#                                         and exports ACCESS_TOKEN. Use this
#                                         ONLY when a caller must embed the
#                                         token in a request body (e.g. SOAP
#                                         Metadata API sessionId — see
#                                         enable-call-scoring.sh).
#
# The split exists because passing ACCESS_TOKEN on a curl command line
# ("curl -H 'Authorization: Bearer $ACCESS_TOKEN' ...") exposes the token in
# the OS process table (ps / /proc/*/cmdline). Callers that don't strictly
# need the raw token should not extract it. See W-23934530.
#
# Both functions cache results on RESOLVED_ORG_ALIAS so back-to-back invocations
# in the same shell don't re-hit `sf org display`.

# Common gate — alias validation + reachability + HTTPS. Exports INSTANCE_URL
# (needed by SOAP callers to build the endpoint). Does NOT export a token.
resolve_org_auth() {
  local org_alias="$1"

  if [[ -z "$org_alias" ]]; then
    echo "Error: Missing org alias"
    return 1
  fi

  if [[ ! "$org_alias" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ ]]; then
    echo "Invalid org alias: '$org_alias'"
    return 1
  fi

  # Cache hit — but re-check HTTPS in case the cached INSTANCE_URL was set by
  # something other than a prior resolve_org_auth call.
  if [[ -n "${INSTANCE_URL:-}" && "${RESOLVED_ORG_ALIAS:-}" == "$org_alias" ]]; then
    if [[ ! "$INSTANCE_URL" =~ ^https:// ]]; then
      echo "Cached instance URL is not HTTPS: $INSTANCE_URL"
      echo "   Refusing to authenticate over an insecure connection."
      return 1
    fi
    return 0
  fi

  # Capture stderr too — some CLI versions emit auth errors there — then strip
  # any warning lines the sf CLI prepends to stdout before the JSON body.
  local org_display org_json
  org_display=$(sf org display --target-org "$org_alias" --json 2>&1)
  org_json=$(echo "$org_display" | awk '/^{/,EOF')

  INSTANCE_URL=$(echo "$org_json" | jq -r '.result.instanceUrl // empty' 2>/dev/null)
  if [[ -z "$INSTANCE_URL" ]]; then
    echo "Cannot connect to org '$org_alias'. Run: sf org login web --alias $org_alias"
    return 1
  fi

  if [[ ! "$INSTANCE_URL" =~ ^https:// ]]; then
    echo "Instance URL is not HTTPS: $INSTANCE_URL"
    echo "   Refusing to authenticate over an insecure connection."
    return 1
  fi

  export INSTANCE_URL
  RESOLVED_ORG_ALIAS="$org_alias"
  export RESOLVED_ORG_ALIAS
  return 0
}

# Superset — resolve_org_auth + extract ACCESS_TOKEN. Used ONLY by callers
# that must place the token inside a request body (SOAP sessionId). New code
# should not use this; prefer `sf api request rest --target-org` instead.
resolve_org_auth_with_token() {
  local org_alias="$1"

  resolve_org_auth "$org_alias" || return 1

  # Cache hit on token too.
  if [[ -n "${ACCESS_TOKEN:-}" && "${ACCESS_TOKEN}" != "null" \
        && "${RESOLVED_ORG_ALIAS:-}" == "$org_alias" \
        && "${ACCESS_TOKEN_RESOLVED:-}" == "1" ]]; then
    return 0
  fi

  local org_display org_json
  org_display=$(sf org display --target-org "$org_alias" --json 2>&1)
  org_json=$(echo "$org_display" | awk '/^{/,EOF')

  ACCESS_TOKEN=$(echo "$org_json" | jq -r '.result.accessToken // empty' 2>/dev/null)
  if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" || "$ACCESS_TOKEN" == *"REDACTED"* ]]; then
    # CLI ~2.108+ redacts accessToken in `org display` — fall back to the
    # dedicated command that always returns the real token.
    ACCESS_TOKEN=$(echo "y" | sf org auth show-access-token --target-org "$org_alias" --no-prompt --json 2>/dev/null | jq -r '.result.accessToken // empty')
  fi

  if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
    echo "Cannot extract access token. Re-authenticate: sf org login web --alias $org_alias"
    return 1
  fi

  export ACCESS_TOKEN
  ACCESS_TOKEN_RESOLVED="1"
  export ACCESS_TOKEN_RESOLVED
  return 0
}
