#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../../../../" && pwd)"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

assert_file() {
  [[ -f "$1" ]] || fail "expected file: $1"
}

assert_absent() {
  [[ ! -e "$1" ]] || fail "expected path to be absent: $1"
}

assert_contains() {
  grep -Fq -- "$2" "$1" || fail "expected $1 to contain: $2"
}

assert_not_contains() {
  if grep -Fq -- "$2" "$1"; then
    fail "expected $1 not to contain: $2"
  fi
}

release_skill="$PROJECT_ROOT/.agents/skills/release-sync/SKILL.md"
release_rules="$PROJECT_ROOT/spec/releases/release-rules.md"

assert_absent "$PROJECT_ROOT/.agents/rules"
assert_absent "$PROJECT_ROOT/.agents/workflows"
assert_file "$release_skill"
assert_contains "$release_skill" "spec/releases/release-rules.md"
assert_contains "$release_skill" "apps/desktop/src/renderer/i18n/locales"
assert_contains "$release_skill" "pnpm verify:release"
assert_not_contains "$release_skill" '`src/renderer/i18n/locales'
assert_contains "$release_rules" ".agents/skills/release-sync/SKILL.md"

assert_file \
  "$PROJECT_ROOT/spec/changes/_templates/change/specs/domain/spec.md"
assert_absent \
  "$PROJECT_ROOT/spec/changes/_templates/change/specs/example-domain"
assert_absent "$PROJECT_ROOT/spec/changes/active/spec-structure-rename"
assert_file \
  "$PROJECT_ROOT/spec/changes/archive/2026/07/2026-07-10-spec-structure-rename/implementation.md"

node "$PROJECT_ROOT/scripts/generate-spec-change-index.mjs" --check

printf 'spec governance single source: passed\n'
