#!/usr/bin/env bash
# Consistency tests for dx-org-analyze SKILL.md and scripts.
# Verifies skill structure, script references, and report contract.
#
# Usage: bash tests/test_consistency.sh
# Exit 0 on all-pass, 1 on any failure.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="$SCRIPT_DIR/../SKILL.md"
SCRIPTS_DIR="$SCRIPT_DIR/../scripts"

if [[ ! -f "$SKILL_FILE" ]]; then
  echo "FAIL: SKILL.md not found at $SKILL_FILE"
  exit 1
fi

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

# ============================================================
echo "=== Test 1: YAML frontmatter is well-formed ==="
# ============================================================

if head -1 "$SKILL_FILE" | grep -q "^---$"; then
  CLOSE_LINE=$(awk 'NR>1 && /^---$/ {print NR; exit}' "$SKILL_FILE")
  if [[ -n "$CLOSE_LINE" ]]; then
    pass "YAML frontmatter opens and closes (line $CLOSE_LINE)"
  else
    fail "YAML frontmatter has no closing ---"
  fi
else
  fail "SKILL.md does not start with ---"
fi

# ============================================================
echo ""
echo "=== Test 2: Required frontmatter fields ==="
# ============================================================

CLOSE_LINE=$(awk 'NR>1 && /^---$/ {print NR; exit}' "$SKILL_FILE")
if [[ -n "$CLOSE_LINE" ]]; then
  FRONTMATTER=$(sed -n "1,${CLOSE_LINE}p" "$SKILL_FILE")
  for field in "name:" "description:" "metadata:"; do
    if echo "$FRONTMATTER" | grep -q "$field"; then
      pass "Frontmatter has '$field'"
    else
      fail "Frontmatter missing '$field'"
    fi
  done
  SKILL_NAME=$(echo "$FRONTMATTER" | grep "^name:" | awk '{print $2}')
  EXPECTED_NAME=$(basename "$(cd "$SCRIPT_DIR/.." && pwd)")
  if [[ "$SKILL_NAME" == "$EXPECTED_NAME" ]]; then
    pass "Skill name '$SKILL_NAME' matches directory name"
  else
    fail "Skill name '$SKILL_NAME' doesn't match directory name '$EXPECTED_NAME'"
  fi
  if echo "$FRONTMATTER" | grep -q "version:"; then
    pass "Frontmatter has 'metadata.version'"
  else
    fail "Frontmatter missing 'metadata.version'"
  fi
fi

# ============================================================
echo ""
echo "=== Test 3: SKILL.md references both scripts ==="
# ============================================================

if grep -qF "collect_org_data.py" "$SKILL_FILE"; then
  pass "References collect_org_data.py"
else
  fail "Missing reference to collect_org_data.py"
fi

if grep -qF "compute_diff.py" "$SKILL_FILE"; then
  pass "References compute_diff.py"
else
  fail "Missing reference to compute_diff.py"
fi

# ============================================================
echo ""
echo "=== Test 4: Scripts exist and are executable ==="
# ============================================================

for script in "collect_org_data.py" "compute_diff.py"; do
  SPATH="$SCRIPTS_DIR/$script"
  if [[ -f "$SPATH" ]]; then
    pass "Script exists: $script"
  else
    fail "Script missing: $script"
  fi
  if [[ -x "$SPATH" ]]; then
    pass "Script is executable: $script"
  else
    fail "Script not executable: $script"
  fi
  if head -1 "$SPATH" | grep -q "python3"; then
    pass "Script has python3 shebang: $script"
  else
    fail "Script missing python3 shebang: $script"
  fi
done

# ============================================================
echo ""
echo "=== Test 5: Scripts accept --help ==="
# ============================================================

for script in "collect_org_data.py" "compute_diff.py"; do
  if python3 "$SCRIPTS_DIR/$script" --help >/dev/null 2>&1; then
    pass "$script --help exits 0"
  else
    fail "$script --help failed"
  fi
done

# ============================================================
echo ""
echo "=== Test 6: collect_org_data.py has required flags ==="
# ============================================================

HELP_COLLECT=$(python3 "$SCRIPTS_DIR/collect_org_data.py" --help 2>&1)
for flag in "org-alias" "output" "skip-deep-data"; do
  if echo "$HELP_COLLECT" | grep -qF -- "--$flag"; then
    pass "collect_org_data.py supports --$flag"
  else
    fail "collect_org_data.py missing flag: --$flag"
  fi
done

# ============================================================
echo ""
echo "=== Test 7: compute_diff.py has required flags ==="
# ============================================================

HELP_DIFF=$(python3 "$SCRIPTS_DIR/compute_diff.py" --help 2>&1)
for flag in "org-a" "org-b" "output" "format" "org-a-label" "org-b-label"; do
  if echo "$HELP_DIFF" | grep -qF -- "--$flag"; then
    pass "compute_diff.py supports --$flag"
  else
    fail "compute_diff.py missing flag: --$flag"
  fi
done

# ============================================================
echo ""
echo "=== Test 8: SF CLI authentication documented ==="
# ============================================================

if grep -qF "sf org list" "$SKILL_FILE"; then
  pass "Documents 'sf org list' for listing authenticated orgs"
else
  fail "Missing: sf org list"
fi

if grep -qF "sf data query" "$SKILL_FILE"; then
  pass "Documents 'sf data query' for validating connectivity"
else
  fail "Missing: sf data query"
fi

if grep -qF "sf org login web" "$SKILL_FILE"; then
  pass "Documents 'sf org login web' for authentication"
else
  fail "Missing: sf org login web"
fi

# ============================================================
echo ""
echo "=== Test 9: Drift score constants in compute_diff.py ==="
# ============================================================

DIFF_SCRIPT="$SCRIPTS_DIR/compute_diff.py"
for term in "WEIGHT_METADATA" "WEIGHT_PERMISSION" "WEIGHT_PROFILE" "DRIFT_LEVELS"; do
  if grep -qF "$term" "$DIFF_SCRIPT"; then
    pass "Drift constant '$term' in compute_diff.py"
  else
    fail "Missing drift constant: '$term'"
  fi
done

if grep -qF "0.6" "$DIFF_SCRIPT" && grep -qF "0.3" "$DIFF_SCRIPT" && grep -qF "0.1" "$DIFF_SCRIPT"; then
  pass "Weights are 0.6 / 0.3 / 0.1"
else
  fail "Drift weights don't match expected 0.6 / 0.3 / 0.1"
fi

for level in "LOW" "MODERATE" "HIGH" "CRITICAL"; do
  if grep -qF "\"$level\"" "$DIFF_SCRIPT"; then
    pass "Severity level '$level' defined"
  else
    fail "Missing severity level: '$level'"
  fi
done

# ============================================================
echo ""
echo "=== Test 10: System permissions support ==="
# ============================================================

COLLECT_SCRIPT="$SCRIPTS_DIR/collect_org_data.py"

if grep -qF "collect_system_permissions" "$COLLECT_SCRIPT"; then
  pass "collect_org_data.py has collect_system_permissions function"
else
  fail "collect_org_data.py missing collect_system_permissions"
fi

if grep -qF "PermissionsXxx" "$COLLECT_SCRIPT" || grep -qF "Permissions" "$COLLECT_SCRIPT" && grep -qF "PermissionSet" "$COLLECT_SCRIPT"; then
  pass "collect_org_data.py queries PermissionsXxx fields on PermissionSet"
else
  fail "Missing PermissionsXxx/PermissionSet query"
fi

if grep -qF "system_permissions" "$COLLECT_SCRIPT"; then
  pass "collect_org_data.py outputs system_permissions in result"
else
  fail "Missing system_permissions in output"
fi

DIFF_SCRIPT="$SCRIPTS_DIR/compute_diff.py"

if grep -qF "diff_system_permissions" "$DIFF_SCRIPT"; then
  pass "compute_diff.py has diff_system_permissions function"
else
  fail "compute_diff.py missing diff_system_permissions"
fi

if grep -qF "System Permissions" "$DIFF_SCRIPT"; then
  pass "compute_diff.py renders System Permissions section in report"
else
  fail "Missing System Permissions section in markdown report"
fi

# ============================================================
echo ""
echo "=== Test 11: collect_org_data.py uses SF CLI and public APIs ==="
# ============================================================

COLLECT_SCRIPT="$SCRIPTS_DIR/collect_org_data.py"

if grep -qF "sf org list metadata-types" "$COLLECT_SCRIPT" || grep -qF "metadata-types" "$COLLECT_SCRIPT"; then
  pass "Uses sf CLI metadata-types for type discovery"
else
  fail "Missing sf CLI metadata type discovery"
fi

if grep -qF "sf org list metadata" "$COLLECT_SCRIPT" || grep -qF "list metadata" "$COLLECT_SCRIPT"; then
  pass "Uses sf CLI to list metadata components"
else
  fail "Missing sf CLI metadata listing"
fi

if grep -qF "OrganizationSettingsDetail" "$COLLECT_SCRIPT"; then
  pass "Uses OrganizationSettingsDetail for org settings (public API)"
else
  fail "Missing OrganizationSettingsDetail — must use public API for settings"
fi

if grep -qF "/limits/" "$COLLECT_SCRIPT"; then
  pass "Uses REST /limits/ endpoint for org limits"
else
  fail "Missing /limits/ endpoint — must use public API for org limits"
fi

if grep -q "exit(2)\|sys.exit(2)" "$COLLECT_SCRIPT"; then
  pass "Exits 2 on session expiry"
else
  fail "Missing exit code 2 for session expiry"
fi

# Verify internal tools are NOT present
if grep -qF "hoseMyOrgPlease" "$COLLECT_SCRIPT"; then
  fail "Still references hoseMyOrgPlease (internal-only tool, must be removed)"
else
  pass "No references to hoseMyOrgPlease (internal tool removed)"
fi

# ============================================================
echo ""
echo "=== Test 12: Core rules in SKILL.md ==="
# ============================================================

RULES=("Read-only" "never deploy" "session expired")

for rule in "${RULES[@]}"; do
  if grep -qiF "$rule" "$SKILL_FILE"; then
    pass "Core rule/concept present: '$rule'"
  else
    fail "Missing: '$rule'"
  fi
done

# ============================================================
echo ""
echo "=== Test 13: No hardcoded metadata type tiers ==="
# ============================================================

HARDCODED_TIERS=$(grep -cE "^\*\*Tier [0-9]" "$SKILL_FILE" || true)
if [[ "$HARDCODED_TIERS" -eq 0 ]]; then
  pass "No hardcoded tier lists in SKILL.md"
else
  fail "Found $HARDCODED_TIERS hardcoded tier lists — use describeMetadata instead"
fi

# ============================================================
echo ""
echo "=== Test 14: No internal-only references in SKILL.md ==="
# ============================================================

if grep -qF "hoseMyOrgPlease" "$SKILL_FILE"; then
  fail "SKILL.md still references hoseMyOrgPlease (internal-only)"
else
  pass "No hoseMyOrgPlease references in SKILL.md"
fi

if grep -qF "SOAP Partner API" "$SKILL_FILE" || grep -qF "SOAP Login" "$SKILL_FILE"; then
  fail "SKILL.md still references SOAP login (removed for external use)"
else
  pass "No SOAP login references in SKILL.md"
fi

if grep -qF "Web Login" "$SKILL_FILE" && grep -qF "sid cookie" "$SKILL_FILE"; then
  fail "SKILL.md still references web login with sid cookie (removed for external use)"
else
  pass "No web login/cookie references in SKILL.md"
fi

# ============================================================
echo ""
echo "=== Test 15: introspect_org.py exists and is executable ==="
# ============================================================

INTROSPECT_SCRIPT="$SCRIPTS_DIR/introspect_org.py"
if [[ -f "$INTROSPECT_SCRIPT" ]]; then
  pass "Script exists: introspect_org.py"
else
  fail "Script missing: introspect_org.py"
fi
if [[ -x "$INTROSPECT_SCRIPT" ]]; then
  pass "Script is executable: introspect_org.py"
else
  fail "Script not executable: introspect_org.py"
fi
if head -1 "$INTROSPECT_SCRIPT" | grep -q "python3"; then
  pass "Script has python3 shebang: introspect_org.py"
else
  fail "Script missing python3 shebang: introspect_org.py"
fi

# ============================================================
echo ""
echo "=== Test 16: introspect_org.py --help and flags ==="
# ============================================================

if python3 "$INTROSPECT_SCRIPT" --help >/dev/null 2>&1; then
  pass "introspect_org.py --help exits 0"
else
  fail "introspect_org.py --help failed"
fi

HELP_INTROSPECT=$(python3 "$INTROSPECT_SCRIPT" --help 2>&1)
for flag in "org" "output" "format" "label"; do
  if echo "$HELP_INTROSPECT" | grep -qF -- "--$flag"; then
    pass "introspect_org.py supports --$flag"
  else
    fail "introspect_org.py missing flag: --$flag"
  fi
done

# ============================================================
echo ""
echo "=== Test 17: SKILL.md documents introspect workflow ==="
# ============================================================

if grep -qF "introspect_org.py" "$SKILL_FILE"; then
  pass "SKILL.md references introspect_org.py"
else
  fail "SKILL.md missing reference to introspect_org.py"
fi

if grep -qiF "Introspect Workflow" "$SKILL_FILE"; then
  pass "SKILL.md has Introspect Workflow section"
else
  fail "SKILL.md missing Introspect Workflow section"
fi

if grep -qiF "single-org" "$SKILL_FILE" || grep -qiF "single org" "$SKILL_FILE"; then
  pass "SKILL.md mentions single-org mode"
else
  fail "SKILL.md missing single-org mode documentation"
fi

if grep -qiF "introspect" "$SKILL_FILE"; then
  pass "SKILL.md mentions introspect in description"
else
  fail "SKILL.md description missing introspect trigger phrases"
fi

# ============================================================
echo ""
echo "=== Test 18: introspect_org.py report sections ==="
# ============================================================

for section in "Metadata Inventory" "Installed Packages" "Org Settings" "Org Limits" "Licenses" "System Permissions" "Deep Data"; do
  if grep -qF "$section" "$INTROSPECT_SCRIPT"; then
    pass "introspect_org.py renders '$section' section"
  else
    fail "introspect_org.py missing '$section' section"
  fi
done

# ============================================================
echo ""
echo "================================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================================"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0
