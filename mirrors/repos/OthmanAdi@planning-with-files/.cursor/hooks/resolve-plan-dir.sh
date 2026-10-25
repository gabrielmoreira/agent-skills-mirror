#!/bin/sh
# planning-with-files: Cursor bash hook resolver entry point.
# Thin forwarder onto the skill-owned canonical resolver.

set -u

HOOK_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd)" || exit 0
CANONICAL_RESOLVER="${HOOK_DIR}/../skills/planning-with-files/scripts/resolve-plan-dir.sh"

[ -f "${CANONICAL_RESOLVER}" ] || exit 0
exec sh "${CANONICAL_RESOLVER}" "$@"
