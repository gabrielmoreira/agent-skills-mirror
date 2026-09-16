#!/usr/bin/env bash
# Tests for compute_diff.py using fixture data.
# Validates diff computation, drift score, and report output.
#
# Usage: bash tests/test_compute_diff.sh
# Exit 0 on all-pass, 1 on any failure.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPUTE="$SCRIPT_DIR/../scripts/compute_diff.py"
FIXTURES="$SCRIPT_DIR/fixtures"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

# ============================================================
echo "=== Test 1: Produces JSON and markdown output ==="
# ============================================================

python3 "$COMPUTE" \
  --org-a "$FIXTURES/org_a.json" \
  --org-b "$FIXTURES/org_b.json" \
  --output "$TMPDIR/diff" \
  --format both \
  --org-a-label "OrgA" \
  --org-b-label "OrgB" >/dev/null 2>&1

if [[ -f "$TMPDIR/diff.json" ]]; then
  pass "JSON output created"
else
  fail "JSON output not created"
fi

if [[ -f "$TMPDIR/diff.md" ]]; then
  pass "Markdown output created"
else
  fail "Markdown output not created"
fi

# ============================================================
echo ""
echo "=== Test 2: JSON structure has required keys ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  for key in "metadata_stats" "permissions" "org_values" "drift"; do
    if python3 -c "import json; d=json.load(open('$TMPDIR/diff.json')); assert '$key' in d" 2>/dev/null; then
      pass "JSON has key '$key'"
    else
      fail "JSON missing key '$key'"
    fi
  done
fi

# ============================================================
echo ""
echo "=== Test 3: Drift score is computed correctly ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
d = json.load(open('$TMPDIR/diff.json'))['drift']
assert 0 <= d['overall'] <= 100, f'overall out of range: {d[\"overall\"]}'
assert 0 <= d['metadata'] <= 100
assert 0 <= d['permission'] <= 100
assert 0 <= d['profile'] <= 100
assert d['level'] in ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')
print(f'  overall={d[\"overall\"]}% level={d[\"level\"]}')
" 2>/dev/null && pass "Drift score valid and in range" || fail "Drift score invalid"
fi

# ============================================================
echo ""
echo "=== Test 4: Metadata diff detects known differences ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
stats = json.load(open('$TMPDIR/diff.json'))['metadata_stats']
apex = [s for s in stats if s['type'] == 'ApexClass'][0]
assert apex['a_only'] == 1, f'Expected 1 a_only ApexClass, got {apex[\"a_only\"]}'
assert apex['b_only'] == 1, f'Expected 1 b_only ApexClass, got {apex[\"b_only\"]}'
assert apex['shared'] == 1, f'Expected 1 shared ApexClass, got {apex[\"shared\"]}'
assert 'OnlyInA' in apex['a_only_names']
assert 'OnlyInB' in apex['b_only_names']
assert 'SharedClass' in apex['shared_names']
co = [s for s in stats if s['type'] == 'CustomObject'][0]
assert co['a_only'] == 1 and co['b_only'] == 0
" 2>/dev/null && pass "Metadata diff correct for fixtures" || fail "Metadata diff wrong"
fi

# ============================================================
echo ""
echo "=== Test 5: Permission diff detects known differences ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
p = json.load(open('$TMPDIR/diff.json'))['permissions']
assert 'ApiEnabled' in p['a_only'], f'ApiEnabled should be a_only'
assert 'ApexRest' in p['a_only'], f'ApexRest should be a_only'
assert 'DisabledInA' in p['b_only'], f'DisabledInA should be b_only'
assert 'OnlyInB' in p['b_only'], f'OnlyInB should be b_only'
assert p['shared_count'] == 1, f'Expected 1 shared perm, got {p[\"shared_count\"]}'
" 2>/dev/null && pass "Permission diff correct for fixtures" || fail "Permission diff wrong"
fi

# ============================================================
echo ""
echo "=== Test 6: Org values diff detects known differences ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
v = json.load(open('$TMPDIR/diff.json'))['org_values']
names = [d['name'] for d in v['diffs']]
assert 'OrgEdition' in names, 'OrgEdition should differ'
assert 'MaxCustomObjects' in names, 'MaxCustomObjects should differ'
assert 'DataStorage' in names, 'DataStorage should differ'
assert 'SharedValue' not in names, 'SharedValue should not differ'
assert v['total'] == 4, f'Expected 4 total values, got {v[\"total\"]}'
assert len(v['diffs']) == 3, f'Expected 3 diffs, got {len(v[\"diffs\"])}'
" 2>/dev/null && pass "Org values diff correct for fixtures" || fail "Org values diff wrong"
fi

# ============================================================
echo ""
echo "=== Test 7: Managed packages excluded from diff ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
stats = json.load(open('$TMPDIR/diff.json'))['metadata_stats']
apex = [s for s in stats if s['type'] == 'ApexClass'][0]
assert 'ManagedPkg' not in apex['a_only_names'], 'ManagedPkg should be excluded'
assert apex['a_count'] == 2, f'Expected 2 custom ApexClass in A (excl managed), got {apex[\"a_count\"]}'
" 2>/dev/null && pass "Managed packages excluded" || fail "Managed packages not excluded"
fi

# ============================================================
echo ""
echo "=== Test 8: Markdown report has required sections ==="
# ============================================================

if [[ -f "$TMPDIR/diff.md" ]]; then
  for section in "Drift Score" "Summary Statistics" "Detailed Differences" "Org Permissions" "Org Values"; do
    if grep -qF "$section" "$TMPDIR/diff.md"; then
      pass "Markdown has section: $section"
    else
      fail "Markdown missing section: $section"
    fi
  done
fi

# ============================================================
echo ""
echo "=== Test 9: Markdown uses provided labels ==="
# ============================================================

if [[ -f "$TMPDIR/diff.md" ]]; then
  if grep -qF "OrgA" "$TMPDIR/diff.md" && grep -qF "OrgB" "$TMPDIR/diff.md"; then
    pass "Markdown uses custom labels OrgA/OrgB"
  else
    fail "Markdown not using custom labels"
  fi
fi

# ============================================================
echo ""
echo "=== Test 10: Installed package diff ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
p = json.load(open('$TMPDIR/diff.json'))['installed_packages']
assert p['a_total'] == 3, f'Expected 3 packages in A, got {p[\"a_total\"]}'
assert p['b_total'] == 3, f'Expected 3 packages in B, got {p[\"b_total\"]}'
assert len(p['a_only']) == 1, f'Expected 1 a_only package, got {len(p[\"a_only\"])}'
assert p['a_only'][0]['namespace'] == 'apkg', f'Expected apkg, got {p[\"a_only\"][0][\"namespace\"]}'
assert len(p['b_only']) == 1, f'Expected 1 b_only package, got {len(p[\"b_only\"])}'
assert p['b_only'][0]['namespace'] == 'bpkg'
assert len(p['version_mismatches']) == 1, f'Expected 1 version mismatch, got {len(p[\"version_mismatches\"])}'
assert p['version_mismatches'][0]['namespace'] == 'vmpkg'
assert p['version_mismatches'][0]['a_version'] == '3.1'
assert p['version_mismatches'][0]['b_version'] == '4.0'
assert len(p['identical']) == 1, f'Expected 1 identical package, got {len(p[\"identical\"])}'
assert p['identical'][0]['namespace'] == 'sharedpkg'
" 2>/dev/null && pass "Package diff correct for fixtures" || fail "Package diff wrong"
fi

# ============================================================
echo ""
echo "=== Test 11: Markdown has installed packages section ==="
# ============================================================

if [[ -f "$TMPDIR/diff.md" ]]; then
  if grep -qF "Installed Packages" "$TMPDIR/diff.md"; then
    pass "Markdown has Installed Packages section"
  else
    fail "Markdown missing Installed Packages section"
  fi
  if grep -qF "Version Mismatch" "$TMPDIR/diff.md" && grep -qF "vmpkg" "$TMPDIR/diff.md"; then
    pass "Markdown shows version mismatch details"
  else
    fail "Markdown missing version mismatch details"
  fi
fi

# ============================================================
echo ""
echo "=== Test 12: License diff ==="
# ============================================================

if [[ -f "$TMPDIR/diff.json" ]]; then
  python3 -c "
import json
lic = json.load(open('$TMPDIR/diff.json'))['licenses']
u = lic['user']
assert u['a_count'] == 3 and u['b_count'] == 3
assert len(u['a_only']) == 1, f'Expected 1 a_only user license, got {len(u[\"a_only\"])}'
assert u['a_only'][0]['Name'] == 'OnlyInA License'
assert len(u['b_only']) == 1
assert u['b_only'][0]['Name'] == 'OnlyInB License'
assert len(u['diffs']) == 1, f'Expected 1 user license diff, got {len(u[\"diffs\"])}'
assert u['diffs'][0]['name'] == 'Salesforce'
assert u['diffs'][0]['a_total'] == 10
assert u['diffs'][0]['b_total'] == 25
ps = lic['permission_set']
assert len(ps['diffs']) == 1
assert ps['diffs'][0]['name'] == 'SalesforceCPQ'
" 2>/dev/null && pass "License diff correct for fixtures" || fail "License diff wrong"
fi

# ============================================================
echo ""
echo "=== Test 13: Markdown has licenses section ==="
# ============================================================

if [[ -f "$TMPDIR/diff.md" ]]; then
  if grep -qF "Licenses" "$TMPDIR/diff.md"; then
    pass "Markdown has Licenses section"
  else
    fail "Markdown missing Licenses section"
  fi
fi

# ============================================================
echo ""
echo "=== Test 14: Exits 1 on missing input file ==="
# ============================================================

python3 "$COMPUTE" \
  --org-a "/nonexistent/file.json" \
  --org-b "$FIXTURES/org_b.json" \
  --output "$TMPDIR/fail" 2>/dev/null

if [[ $? -eq 1 ]]; then
  pass "Exits 1 on missing input"
else
  fail "Should exit 1 on missing input"
fi

# ============================================================
echo ""
echo "================================================"
echo "Results: $PASS passed, $FAIL failed"
echo "================================================"

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0
