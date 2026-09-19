#!/usr/bin/env bash
# Optionally validate migrated DataCaptureFlow output via a non-destructive
# `sf project deploy start --dry-run`. Offline-safe: with no org alias, the
# skill still succeeds and validation is skipped.
#
# Usage: validate_flow.sh <org-alias> <flow-file> [<flow-file> ...]
#   arg 1        : org alias ("" = offline, skip validation)
#   args 2..N    : paths to .flow-meta.xml files
#
# Exit codes:
#   0  all flows passed dry-run
#   1  >=1 flow failed dry-run
#   2  usage error (no flow files given)
#   3  validation skipped (no target org) — output was still produced

set -uo pipefail

SKIP_MSG="Output generated. Deployment validation skipped (no target org configured)."

BUNDLE=0
if [[ "${1:-}" == "--bundle" ]]; then
  BUNDLE=1
  shift
fi

ALIAS="${1:-}"
shift || true
FLOWS=("$@")

if [[ ${#FLOWS[@]} -eq 0 ]]; then
  echo "Usage: validate_flow.sh [--bundle] <org-alias> <flow-file> [<flow-file> ...]" >&2
  exit 2
fi

if [[ -z "$ALIAS" ]]; then
  echo "$SKIP_MSG"
  echo "VALIDATION SUMMARY: skipped (no target org)"
  exit 3
fi

# ── Bundle mode: dry-run the whole migrated set in ONE project so intra-tree
#    subflow (_DC) references resolve within the deploy set (no real deploy). ──
if [[ $BUNDLE -eq 1 ]]; then
  # Verify every file exists first.
  for FLOW in "${FLOWS[@]}"; do
    if [[ ! -f "$FLOW" ]]; then
      echo "FAIL  (bundle)"
      echo "      ERROR: flow file not found: $FLOW"
      echo "VALIDATION SUMMARY: 0 passed, 1 failed, 0 skipped (org: $ALIAS)"
      exit 1
    fi
  done

  WORKDIR=$(mktemp -d -t dcflow-bundle.XXXXXX)
  trap 'rm -rf "$WORKDIR"' EXIT
  mkdir -p "$WORKDIR/force-app/main/default/flows"
  for FLOW in "${FLOWS[@]}"; do
    cp "$FLOW" "$WORKDIR/force-app/main/default/flows/$(basename "$FLOW")"
  done
  cat > "$WORKDIR/sfdx-project.json" <<'JSON'
{
  "packageDirectories": [{"path": "force-app", "default": true}],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "67.0"
}
JSON

  OUTPUT=$(cd "$WORKDIR" && sf project deploy start \
    --dry-run \
    --source-dir "force-app/main/default/flows" \
    --target-org "$ALIAS" \
    --json 2>&1)
  RC=$?
  rm -rf "$WORKDIR"

  if [[ $RC -eq 0 ]]; then
    echo "PASS  (bundle: ${#FLOWS[@]} flows)"
    echo "VALIDATION SUMMARY: ${#FLOWS[@]} passed, 0 failed, 0 skipped (org: $ALIAS)"
    exit 0
  else
    echo "FAIL  (bundle)"
    while IFS= read -r line; do
      echo "      $line"
    done <<< "$OUTPUT"
    echo "VALIDATION SUMMARY: 0 passed, 1 failed, 0 skipped (org: $ALIAS)"
    exit 1
  fi
fi

passed=0
failed=0
WORKDIR=""

for FLOW in "${FLOWS[@]}"; do
  NAME=$(basename "$FLOW")

  if [[ ! -f "$FLOW" ]]; then
    echo "FAIL  $NAME"
    echo "      ERROR: flow file not found: $FLOW"
    failed=$((failed + 1))
    continue
  fi

  # Bootstrap a minimal SFDX project per flow for isolated dry-run attribution.
  WORKDIR=$(mktemp -d -t dcflow-validate.XXXXXX)
  trap 'rm -rf "$WORKDIR"' EXIT
  mkdir -p "$WORKDIR/force-app/main/default/flows"
  cp "$FLOW" "$WORKDIR/force-app/main/default/flows/$NAME"
  cat > "$WORKDIR/sfdx-project.json" <<'JSON'
{
  "packageDirectories": [{"path": "force-app", "default": true}],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "67.0"
}
JSON

  # Non-destructive validation: --dry-run validates but never saves to the org.
  OUTPUT=$(cd "$WORKDIR" && sf project deploy start \
    --dry-run \
    --source-dir "force-app/main/default/flows" \
    --target-org "$ALIAS" \
    --json 2>&1)
  RC=$?

  rm -rf "$WORKDIR"

  if [[ $RC -eq 0 ]]; then
    echo "PASS  $NAME"
    passed=$((passed + 1))
  else
    echo "FAIL  $NAME"
    # Full SF CLI error output, verbatim, indented for readability (AC #5).
    while IFS= read -r line; do
      echo "      $line"
    done <<< "$OUTPUT"
    failed=$((failed + 1))
  fi
done

echo "VALIDATION SUMMARY: $passed passed, $failed failed, 0 skipped (org: $ALIAS)"

if [[ $failed -gt 0 ]]; then
  exit 1
fi
exit 0
