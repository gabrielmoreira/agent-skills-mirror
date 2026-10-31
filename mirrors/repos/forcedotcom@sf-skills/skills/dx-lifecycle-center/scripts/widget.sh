#!/usr/bin/env bash
# Fill one of this skill's HXL widgets (assets/widgets/<name>/<name>.json), check it
# with card-policy.jq, and print one line for the chat:
#   CARD_JSON {"nodes": <tree>}   call render_widget once with exactly this JSON as its arguments
#   CARD_UNAVAILABLE <reason>     show no card; give the same facts in text instead
# Usage: widget.sh <name> '<attrs json>'   (connect-org.md, Steps 2 and 5, hub mode)
# Always exits 0: the card is optional, the facts the other scripts print are not.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="${1:-}" ATTRS="${2:-}"
MAX_BYTES="${CARD_MAX_BYTES:-8192}"
TEMPLATE="$HERE/../assets/widgets/$NAME/$NAME.json"
unavailable() { echo "CARD_UNAVAILABLE $1"; exit 0; }
if ! [[ "$NAME" =~ ^[a-z0-9-]+$ ]] || [ ! -f "$TEMPLATE" ]; then
  unavailable "template: no widget named '$NAME'"
fi
if ! TREE=$(jq -c --argjson attrs "$ATTRS" -f "$HERE/fill-widget.jq" "$TEMPLATE" 2>&1); then
  TREE=${TREE%%$'\n'*}
  unavailable "fill: ${TREE##*): }"
fi
if ! PROBLEM=$(printf '%s' "$TREE" | jq -r -f "$HERE/card-policy.jq" 2>/dev/null); then
  unavailable "policy: the check failed"
fi
[ -z "$PROBLEM" ] || unavailable "$PROBLEM"
ARGS=$(printf '%s' "$TREE" | jq -c '{nodes: .}')
BYTES=$(printf '%s' "$ARGS" | wc -c | tr -d ' ')
[ "$BYTES" -le "$MAX_BYTES" ] || unavailable "size: $BYTES bytes, more than $MAX_BYTES"
echo "CARD_JSON $ARGS"
