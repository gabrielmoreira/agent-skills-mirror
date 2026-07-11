#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../../../../" && pwd)"
GENERATOR="$PROJECT_ROOT/scripts/generate-spec-change-index.mjs"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

assert_contains() {
  grep -Fq -- "$2" "$1" || fail "expected $1 to contain: $2"
}

mkdir -p \
  "$TEMP_ROOT/spec/changes/active/implemented-change" \
  "$TEMP_ROOT/spec/changes/active/missing-notes" \
  "$TEMP_ROOT/spec/changes/archive/2026/07/2026-07-10-old-change" \
  "$TEMP_ROOT/spec/changes/legacy/old-layout"

cat >"$TEMP_ROOT/spec/changes/active/implemented-change/implementation.md" <<'EOF'
# Implementation

## Status

Implemented. Review and convergence remain.
EOF

node "$GENERATOR" --root "$TEMP_ROOT"
index_path="$TEMP_ROOT/spec/changes/index.md"

assert_contains "$index_path" '| Active | 2 |'
assert_contains "$index_path" '| Archived | 1 |'
assert_contains "$index_path" '| Legacy | 1 |'
assert_contains "$index_path" '| `implemented-change` | implemented |'
assert_contains "$index_path" '| `missing-notes` | missing implementation |'
node "$GENERATOR" --root "$TEMP_ROOT" --check

mkdir -p "$TEMP_ROOT/spec/changes/active/new-change"
if node "$GENERATOR" --root "$TEMP_ROOT" --check >/dev/null 2>&1; then
  fail 'expected stale inventory check to fail'
fi

node "$GENERATOR" --root "$TEMP_ROOT"
assert_contains "$index_path" '| Active | 3 |'

if node "$GENERATOR" --root >/dev/null 2>&1; then
  fail 'expected a missing --root value to fail'
fi

printf 'spec change inventory: passed\n'
