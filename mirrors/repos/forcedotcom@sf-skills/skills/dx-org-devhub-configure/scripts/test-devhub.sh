#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/devhub.sh"
WORK_DIR="$(mktemp -d)"
STUB_DIR="$WORK_DIR/bin"
LOG_FILE="$WORK_DIR/sf.log"
MARKER="$WORK_DIR/trap-injection"
mkdir -p "$STUB_DIR"
trap 'rm -rf -- "$WORK_DIR"' EXIT

cat > "$STUB_DIR/sf" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SF_STUB_LOG"

case "$*" in
  "config get target-org --json")
    if [ "${SF_TEST_NO_DEFAULT:-0}" = "1" ]; then
      printf '%s\n' '{"status":0,"result":[]}'
    else
      printf '%s\n' '{"status":0,"result":[{"value":"default-org"}]}'
    fi
    ;;
  "config get target-dev-hub --json")
    if [ "${SF_TEST_NO_DEFAULT:-0}" = "1" ]; then
      printf '%s\n' '{"status":0,"result":[]}'
    else
      printf '%s\n' '{"status":0,"result":[{"value":"default-devhub"}]}'
    fi
    ;;
  "org list --json")
    if [ "${SF_TEST_HANG:-0}" = "1" ]; then
      sleep 60
    fi
    if [ "${SF_TEST_NO_ORGS:-0}" = "1" ]; then
      printf '%s\n' '{"status":0,"result":{"nonScratchOrgs":[],"scratchOrgs":[]}}'
    else
      printf '%s\n' '{"status":0,"result":{"nonScratchOrgs":[{"alias":"my-org","username":"a@b.com","connectedStatus":"Connected","isDefaultUsername":true}],"scratchOrgs":[]}}'
    fi
    ;;
  "data query --query SELECT COUNT() FROM ScratchOrgInfo"*)
    if [ "${SF_TEST_DEVHUB_ENABLED:-0}" = "1" ]; then
      printf '%s\n' '{"status":0,"result":{"totalSize":0}}'
    else
      printf '%s\n' '{"status":1,"name":"INVALID_TYPE","message":"ScratchOrgInfo unavailable"}'
      exit 1
    fi
    ;;
  "data query --query SELECT OrganizationType, IsSandbox FROM Organization"*)
    printf '%s\n' "{\"status\":0,\"result\":{\"records\":[{\"OrganizationType\":\"Developer Edition\",\"IsSandbox\":${SF_TEST_SANDBOX:-false}}]}}"
    ;;
  "api request rest /services/data/"*"/tooling/sobjects/DevHubSettings/DevHub"*)
    printf '%s\n' '{"Id":"DevHub","FullName":"DevHub","Metadata":{"enableScratchOrgManagementPref":true,"enablePackaging2":false,"enableScratchOrgSnapshotPref":true,"enableShapeExportPref":false}}'
    ;;
  "org list limits"*)
    if [ "${SF_TEST_LIMITS_FAIL:-0}" = "1" ]; then
      printf '%s\n' '{"status":1,"message":"limits unavailable"}'
      exit 1
    fi
    printf '%s\n' "{\"status\":0,\"result\":[{\"name\":\"ActiveScratchOrgs\",\"remaining\":${SF_TEST_ACTIVE_REM:-3},\"max\":${SF_TEST_ACTIVE_MAX:-3}},{\"name\":\"DailyScratchOrgs\",\"remaining\":${SF_TEST_DAILY_REM:-6},\"max\":${SF_TEST_DAILY_MAX:-6}}]}"
    ;;
  "org display"*)
    printf '%s\n' '{"status":0,"result":{"id":"00D000000000001","username":"admin@example.com","instanceUrl":"https://example.my.salesforce.com"}}'
    ;;
  "project deploy start"*)
    printf '%s\n' '{"status":0,"result":{"success":true,"checkOnly":true}}'
    ;;
  *)
    printf '%s\n' '{"status":1,"message":"unexpected sf invocation"}'
    exit 1
    ;;
esac
EOF
chmod +x "$STUB_DIR/sf"

export PATH="$STUB_DIR:$PATH"
export SF_STUB_LOG="$LOG_FILE"

pass=0
fail=0

check() {
  local name="$1" expected_rc="$2" expected_text="$3"
  shift 3
  local output rc
  : > "$LOG_FILE"
  output="$("$@" 2>&1)"
  rc=$?
  if [ "$rc" -eq "$expected_rc" ] && { [ "$expected_text" = "-" ] || printf '%s' "$output" | grep -Fq -- "$expected_text"; }; then
    pass=$((pass + 1))
    printf 'PASS: %s\n' "$name"
  else
    fail=$((fail + 1))
    printf 'FAIL: %s (exit %s, expected %s)\n%s\n' "$name" "$rc" "$expected_rc" "$output"
  fi
}

check "reject disabling the master switch" 2 "cannot be set to false" \
  "$SCRIPT" explicit-org --pref enableScratchOrgManagementPref=false

check "warn for scratch-management apply" 0 "IRREVERSIBLE" \
  env SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT" explicit-org --scratch-management --apply

check "propagate status allocation failure" 1 "Could not read org limits" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_LIMITS_FAIL=1 "$SCRIPT" explicit-org

check "require explicit target for apply" 2 "explicit org" \
  "$SCRIPT" --enable --apply

# --- new: read current DevHubSettings preferences ---
check "show-settings renders master pref ON" 0 "enableScratchOrgManagementPref" \
  env SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT" explicit-org --show-settings
check "show-settings renders packaging OFF" 0 "enablePackaging2                   OFF" \
  env SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT" explicit-org --show-settings

# --- new: pre-flight allocation thresholds ---
check "threshold WARN under 2 remaining" 0 "WARN" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_ACTIVE_REM=1 SF_TEST_ACTIVE_MAX=3 "$SCRIPT" explicit-org --allocation
check "threshold NOTE above 80 percent" 0 "usage at" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_ACTIVE_REM=0 SF_TEST_ACTIVE_MAX=3 "$SCRIPT" explicit-org --allocation

# --- new: sandbox refuses enablement, before any deploy ---
: > "$LOG_FILE"
sandbox_out="$(env SF_TEST_DEVHUB_ENABLED=0 SF_TEST_SANDBOX=true "$SCRIPT" explicit-org --scratch-management --apply 2>&1)"
sandbox_rc=$?
if [ "$sandbox_rc" -eq 1 ] && printf '%s' "$sandbox_out" | grep -qi "sandbox" && ! grep -Fq "project deploy start" "$LOG_FILE"; then
  pass=$((pass + 1)); printf 'PASS: sandbox refuses enablement without deploying\n'
else
  fail=$((fail + 1)); printf 'FAIL: sandbox refuses enablement (exit %s)\n%s\n' "$sandbox_rc" "$sandbox_out"
fi

# --- new: org discovery when no default is set ---
check "org discovery lists authenticated orgs" 2 "my-org" \
  env SF_TEST_NO_DEFAULT=1 SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT"

check "list-orgs mode lists authenticated orgs" 0 "my-org" \
  "$SCRIPT" --list-orgs

# --- removed: login flags are now unknown options ---
check "login flag rejected" 2 "Unknown option" \
  "$SCRIPT" explicit-org --login
check "instance-url flag rejected" 2 "Unknown option" \
  "$SCRIPT" explicit-org --instance-url https://x.my.salesforce.com

# --- new: show-settings refuses when Dev Hub is OFF ---
check "show-settings refuses when Dev Hub off" 1 "no DevHubSettings to read" \
  env SF_TEST_DEVHUB_ENABLED=0 "$SCRIPT" explicit-org --show-settings

# --- new: daily-limit NOTE threshold (only active was covered before) ---
check "threshold NOTE daily above 80 percent" 0 "Daily scratch org usage at" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_DAILY_REM=1 SF_TEST_DAILY_MAX=6 "$SCRIPT" explicit-org --allocation

# --- new: list-orgs with no authenticated orgs ---
check "list-orgs reports none authenticated" 0 "No orgs are authenticated" \
  env SF_TEST_NO_ORGS=1 "$SCRIPT" --list-orgs

# A hung CLI must not hold the caller for the full stub sleep.
hang_start=$(date +%s)
hang_out="$(env SF_TEST_HANG=1 "$SCRIPT" --list-orgs 2>&1)"
hang_rc=$?
hang_elapsed=$(( $(date +%s) - hang_start ))
if [ "$hang_rc" -eq 1 ] && [ "$hang_elapsed" -lt 35 ] && printf '%s' "$hang_out" | grep -Fq "Could not list authenticated orgs"; then
  pass=$((pass + 1)); printf 'PASS: list-orgs bounds a hung sf org list (%ss)\n' "$hang_elapsed"
else
  fail=$((fail + 1)); printf 'FAIL: list-orgs bounds a hung sf org list (exit %s, %ss)\n%s\n' "$hang_rc" "$hang_elapsed" "$hang_out"
fi

# --- new: JSON fidelity for the added fields ---
check "status JSON reports edition" 0 "\"edition\": \"Developer Edition\"" \
  env SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT" explicit-org --json
check "status JSON reports isSandbox false (not null) for non-sandbox" 0 "\"isSandbox\": false" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_SANDBOX=false "$SCRIPT" explicit-org --json
check "status JSON reports isSandbox true for sandbox" 0 "\"isSandbox\": true" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_SANDBOX=true "$SCRIPT" explicit-org --json
check "allocation JSON emits warnings array near limit" 0 "\"warnings\"" \
  env SF_TEST_DEVHUB_ENABLED=1 SF_TEST_ACTIVE_REM=1 SF_TEST_ACTIVE_MAX=3 "$SCRIPT" explicit-org --allocation --json
check "show-settings JSON emits settings map" 0 "enableScratchOrgSnapshotPref" \
  env SF_TEST_DEVHUB_ENABLED=1 "$SCRIPT" explicit-org --show-settings --json
check "list-orgs JSON emits normalized array" 0 "\"isDefault\"" \
  "$SCRIPT" --list-orgs --json

# --- new: a not-enabled sandbox is flagged as ineligible in status ---
check "status flags sandbox as unable to host Dev Hub" 0 "cannot host Dev Hub" \
  env SF_TEST_DEVHUB_ENABLED=0 SF_TEST_SANDBOX=true "$SCRIPT" explicit-org

# --- safety: cleanup trap treats TMPDIR content as data ---
unsafe_tmp="$WORK_DIR/unsafe'; touch $MARKER; #"
mkdir -p "$unsafe_tmp"
check "cleanup trap does not execute TMPDIR content" 0 "Dry run passed" \
  env SF_TEST_DEVHUB_ENABLED=1 TMPDIR="$unsafe_tmp" "$SCRIPT" explicit-org --packaging
if [ -e "$MARKER" ]; then
  fail=$((fail + 1))
  printf 'FAIL: cleanup trap executed TMPDIR content\n'
else
  pass=$((pass + 1))
  printf 'PASS: cleanup trap treated TMPDIR as data\n'
fi

printf '\nRESULT: %s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
