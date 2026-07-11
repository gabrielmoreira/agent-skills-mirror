#!/usr/bin/env bash
# Mint a signed OrgJWT (sfap_api scope) via the OAuth 2.0 client_credentials
# flow and print it to stdout. This is the value Claude Code sends as
# `Authorization: Bearer <jwt>` to the Salesforce Models API.
#
# Credentials come from an env file passed as $1 (recommended — that's what the
# generated settings.json does), or from the environment:
#   SF_INSTANCE_URL   e.g. https://my-org.my.salesforce.com
#   SF_CLIENT_ID      connected-app consumer key   (app needs the sfap_api scope
#   SF_CLIENT_SECRET  connected-app consumer secret  + client_credentials enabled)
#
# Usage (as apiKeyHelper):  bash get-orgjwt.sh /path/to/.orgjwt.env
set -euo pipefail

command -v jq >/dev/null 2>&1 || { echo "get-orgjwt: jq is required but not found on PATH" >&2; exit 1; }

CREDS="${1:-${SFGW_CREDS:-}}"
if [ -n "$CREDS" ]; then
  [ -f "$CREDS" ] || { echo "get-orgjwt: creds file not found: $CREDS" >&2; exit 1; }
  # Read only the three expected KEY=VALUE assignments. We deliberately do NOT
  # `source` the file — sourcing would execute any shell code a malformed or
  # tampered creds file happened to contain (e.g. command substitution).
  while IFS='=' read -r key val; do
    case "$key" in
      SF_INSTANCE_URL|SF_CLIENT_ID|SF_CLIENT_SECRET)
        val="${val%\"}"; val="${val#\"}"   # strip surrounding double quotes
        export "$key=$val" ;;
    esac
  done < "$CREDS"
fi
: "${SF_INSTANCE_URL:?set SF_INSTANCE_URL (in creds file or env)}"
: "${SF_CLIENT_ID:?set SF_CLIENT_ID}"
: "${SF_CLIENT_SECRET:?set SF_CLIENT_SECRET}"

RESPONSE=$(curl -s --location "${SF_INSTANCE_URL%/}/services/oauth2/token" \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "client_id=${SF_CLIENT_ID}" \
  --data-urlencode "client_secret=${SF_CLIENT_SECRET}" \
  --data-urlencode 'grant_type=client_credentials')

TOKEN=$(printf '%s' "$RESPONSE" | jq -r '.access_token // empty')
if [ -z "$TOKEN" ]; then
  ERR=$(printf '%s' "$RESPONSE" | jq -r '.error_description // .error // empty' 2>/dev/null)
  [ -n "$ERR" ] || ERR="check connected-app creds / sfap_api scope / client_credentials flow"
  echo "get-orgjwt: token request failed — $ERR" >&2
  exit 1
fi
printf '%s' "$TOKEN"
