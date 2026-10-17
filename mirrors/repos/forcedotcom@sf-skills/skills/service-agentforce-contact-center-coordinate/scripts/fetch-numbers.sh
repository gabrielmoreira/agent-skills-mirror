#!/usr/bin/env bash
# Fetch available default phone numbers for a country + phone-number type.
# Usage: fetch-numbers.sh <org-alias> <country> <phone-type> [search-param]
#   country:      US | CA
#   phone-type:   10DLC | "Toll Free"
#   search-param: optional — area code (10DLC) or prefix (Toll Free) to narrow
#                 results. Appended as the API's `searchParam` query param. Omit
#                 (or pass empty) to list all available numbers for the type.
# Output: JSON { "phoneNumbers": [...] } on stdout.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

if [[ "${1:-}" == "--help" || $# -lt 3 ]]; then
  echo "Usage: fetch-numbers.sh <org-alias> <country> <phone-type> [search-param]" >&2
  [[ "${1:-}" == "--help" ]] && exit 0 || exit 2
fi

ALIAS="$1"; COUNTRY="$2"; PHONE_TYPE="$3"; SEARCH_PARAM="${4:-}"

QUERY="countryCode=${COUNTRY}&phoneNumberType=$(urlenc_spaces "$PHONE_TYPE")"
[[ -n "$SEARCH_PARAM" ]] && QUERY="${QUERY}&searchParam=$(urlenc "$SEARCH_PARAM")"

sf api request rest \
  "/${NM_BASE}/numbers?${QUERY}" \
  --target-org "$ALIAS"
