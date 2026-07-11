#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd -- "$SKILL_ROOT/../../.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

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

for language in zh en; do
  target_dir="$TEMP_ROOT/$language"
  bash "$SKILL_ROOT/scripts/spec-init.sh" "$target_dir" \
    --name "Governance Fixture" --type cli --lang "$language" >/dev/null
  assert_file "$target_dir/docs/rules/commit-rules.md"
  assert_file "$target_dir/docs/rules/document-archive-rules.md"
  assert_contains "$target_dir/spec-init.topology.yml" "workflow_phases:"
  assert_contains "$target_dir/spec-init.topology.yml" "analyze:"
  assert_contains "$target_dir/spec-init.topology.yml" "converge:"
  assert_contains "$target_dir/AGENTS.md" "analyze"
  assert_contains "$target_dir/AGENTS.md" "converge"
  assert_contains \
    "$target_dir/docs/changes/active/CHG-0001-template/verification.md" \
    "Analyze"
done

assert_file "$SKILL_ROOT/assets/templates/project/zh/docs/04-verification/README.md.tmpl"
assert_absent "$SKILL_ROOT/assets/templates/project/zh/docs/04-tdd"
assert_contains "$SKILL_ROOT/SKILL.md" "references/prompthub-profile.md"

assert_contains "$PROJECT_ROOT/spec-init.topology.yml" "workflow_phases:"
pnpm --dir "$PROJECT_ROOT" exec prettier --check \
  "$PROJECT_ROOT/spec-init.topology.yml" >/dev/null
assert_contains "$PROJECT_ROOT/AGENTS.md" "analyze"
assert_contains "$PROJECT_ROOT/AGENTS.md" "converge"
assert_file "$PROJECT_ROOT/spec/rules/document-archive-rules.md"
assert_contains \
  "$PROJECT_ROOT/spec/rules/document-archive-rules.md" \
  "ISS-YYYYMMDD-NNN"
assert_contains \
  "$PROJECT_ROOT/spec/rules/document-archive-rules.md" \
  "不重命名"

for file_name in \
  01-test-strategy-and-quality-gates.md \
  02-test-standards.md \
  03-test-design-methodology.md \
  04-test-case-matrix.md \
  05-regression-suite.md \
  06-test-data-and-fixtures.md \
  07-coverage-map.md; do
  assert_file "$PROJECT_ROOT/spec/workflow/04-verification/$file_name"
done

assert_contains \
  "$PROJECT_ROOT/spec/changes/_templates/change/tasks.md" \
  "Analyze"
assert_file \
  "$PROJECT_ROOT/spec/changes/_templates/change/specs/domain/spec.md"
assert_file "$PROJECT_ROOT/scripts/generate-spec-change-index.mjs"
assert_file "$PROJECT_ROOT/spec/changes/index.md"
node "$PROJECT_ROOT/scripts/generate-spec-change-index.mjs" --check

printf 'spec-init governance alignment: passed\n'
