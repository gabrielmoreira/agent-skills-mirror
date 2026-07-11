#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

assert_contains() {
  local file_path="$1"
  local expected="$2"
  if ! grep -Fq -- "$expected" "$file_path"; then
    printf 'Expected %s to contain: %s\n' "$file_path" "$expected" >&2
    exit 1
  fi
}

for language in zh en; do
  target_dir="$TEMP_ROOT/$language"
  bash "$SKILL_ROOT/scripts/spec-init.sh" "$target_dir" \
    --name "Commit Rules Fixture" \
    --type cli \
    --lang "$language" >/dev/null

  test -f "$target_dir/docs/rules/commit-rules.md"
  assert_contains "$target_dir/AGENTS.md" "docs/rules/commit-rules.md"
  assert_contains "$target_dir/docs/rules/README.md" "docs/rules/commit-rules.md"
done

assert_contains "$TEMP_ROOT/zh/docs/rules/commit-rules.md" "提交正文"
assert_contains "$TEMP_ROOT/zh/docs/rules/commit-rules.md" "测试状态"
assert_contains "$TEMP_ROOT/en/docs/rules/commit-rules.md" "commit body"
assert_contains "$TEMP_ROOT/en/docs/rules/commit-rules.md" "Test status"

printf 'spec-init commit rules scaffold: passed\n'
