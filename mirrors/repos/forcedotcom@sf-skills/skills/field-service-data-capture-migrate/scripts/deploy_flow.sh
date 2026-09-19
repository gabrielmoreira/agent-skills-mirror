#!/usr/bin/env bash
# Deploy migrated DataCaptureFlow output to a customer org, capturing a
# pre-deploy rollback snapshot first. Demo-ready implementation of FR-013
# (deploy kickoff) and FR-014 (rollback snapshot).
#
# Order of operations:
#   1. FR-014 snapshot  — query each target flow's prior state in the org and
#      write a rollback manifest BEFORE anything is written. Reversibility first.
#   2. Confirmation     — deploy NEVER runs automatically; the SE must confirm
#      (interactive prompt, or --yes for demo automation). Hard product constraint.
#   3. FR-013 deploy    — `sf project deploy start` (real deploy). Every deploy
#      copy is force-set to <status>Draft</status> regardless of the source
#      file's on-disk status, in the leaves-first order the caller passes
#      (Step 3b dependency order). Activation is never done by this script —
#      it is a manual admin action in the org UI (SKILL.md Step 8), after
#      validation and device testing.
#
# Offline-safe: with no org alias, nothing is queried or written and the skill
# still succeeds (validation/deploy deferred until an org is available).
#
# Usage: deploy_flow.sh [--yes] <org-alias> <flow-file> [<flow-file> ...]
#   --yes        : skip the interactive confirmation prompt (demo automation)
#   arg 1        : org alias ("" = offline, skip deploy)
#   args 2..N    : paths to .flow-meta.xml files, in deploy order (leaves first)
#
# Exit codes:
#   0  deploy succeeded
#   1  deploy failed (or a flow file was not found)
#   2  usage error (no flow files given)
#   3  deploy skipped (no target org) — nothing was written
#   4  aborted by SE (declined confirmation) — nothing was written

set -uo pipefail

SKIP_MSG="No target org configured. Deploy skipped (nothing written)."
SNAPSHOT_ROOT="${FSM_ROLLBACK_ROOT:-/tmp/fsm-migration/rollback}"

ASSUME_YES=0
while [[ "${1:-}" == "--yes" ]]; do
  ASSUME_YES=1
  shift
done

ALIAS="${1:-}"
shift || true
FLOWS=("$@")

if [[ ${#FLOWS[@]} -eq 0 ]]; then
  echo "Usage: deploy_flow.sh [--yes] <org-alias> <flow-file> [<flow-file> ...]" >&2
  exit 2
fi

if [[ -z "$ALIAS" ]]; then
  echo "$SKIP_MSG"
  echo "DEPLOY SUMMARY: skipped (no target org)"
  exit 3
fi

# Verify every file exists before touching the org.
for FLOW in "${FLOWS[@]}"; do
  if [[ ! -f "$FLOW" ]]; then
    echo "ERROR: flow file not found: $FLOW" >&2
    echo "DEPLOY SUMMARY: 0 deployed, aborted (missing file)"
    exit 1
  fi
done

# API name = filename minus the .flow-meta.xml suffix.
API_NAMES=()
for FLOW in "${FLOWS[@]}"; do
  API_NAMES+=("$(basename "$FLOW" .flow-meta.xml)")
done

# ── Step 1 — FR-014 rollback snapshot (READ-only, before any write) ──────────
# Query each target flow's current state in the org so a later restore knows the
# pre-deploy version/status. A flow with no prior state is a brand-new deploy
# (nothing to roll back to except removal — out of scope per work item).
# The snapshot is safety-critical: any failure to capture or render it aborts
# the deploy (we never write without a snapshot in hand).
STAMP=$(date +%Y%m%d-%H%M%S)-$$
SNAPSHOT_DIR="$SNAPSHOT_ROOT/$STAMP"
mkdir -p "$SNAPSHOT_DIR"
MANIFEST="$SNAPSHOT_DIR/snapshot.json"

abort_snapshot() {
  echo "ERROR: $1 — refusing to deploy without a rollback snapshot." >&2
  echo "DEPLOY SUMMARY: 0 deployed, aborted (snapshot failed)"
  exit 1
}

# Build a SOQL IN-list of the target API names.
IN_LIST=""
for NAME in "${API_NAMES[@]}"; do
  [[ -n "$IN_LIST" ]] && IN_LIST+=","
  IN_LIST+="'$NAME'"
done

# NOTE: no `2>&1` — the CLI prints warnings (update notices, apiVersion) to
# stderr even on success, and merging them would corrupt the JSON we parse.
SNAP_QUERY="SELECT ApiName, Label, IsActive, ActiveVersionId, LatestVersionId FROM FlowDefinitionView WHERE ApiName IN ($IN_LIST)"
SNAP_OUT=$(sf data query --target-org "$ALIAS" --query "$SNAP_QUERY" --json)
SNAP_RC=$?
[[ $SNAP_RC -ne 0 ]] && abort_snapshot "rollback snapshot query failed (sf exit $SNAP_RC)"

# Render the manifest: one entry per REQUESTED flow, marking whether it already
# existed in the org (existedBeforeDeploy) and its prior state if so. The
# renderer prints the existing-flow count on its last stdout line so the shell
# doesn't have to re-parse the manifest. Any parse/render error exits nonzero.
EXISTING=$(printf '%s' "$SNAP_OUT" | ORG="$ALIAS" STAMP="$STAMP" NAMES="${API_NAMES[*]}" MANIFEST="$MANIFEST" python3 -c '
import sys, json, os
try:
    data = json.load(sys.stdin)
except Exception as e:
    sys.stderr.write("could not parse snapshot query JSON: %s\n" % e)
    sys.exit(1)
records = {r["ApiName"]: r for r in data.get("result", {}).get("records", [])}
requested = os.environ["NAMES"].split()
flows, existing = [], 0
for name in requested:
    r = records.get(name)
    if r:
        existing += 1
        flows.append({
            "apiName": name,
            "existedBeforeDeploy": True,
            "priorLabel": r.get("Label"),
            "priorIsActive": r.get("IsActive"),
            "priorActiveVersionId": r.get("ActiveVersionId"),
            "priorLatestVersionId": r.get("LatestVersionId"),
        })
    else:
        flows.append({"apiName": name, "existedBeforeDeploy": False})
manifest = {"capturedAt": os.environ["STAMP"], "org": os.environ["ORG"], "flows": flows}
with open(os.environ["MANIFEST"], "w") as f:
    json.dump(manifest, f, indent=2)
print(existing)
')
[[ $? -ne 0 ]] && abort_snapshot "rollback snapshot could not be rendered"

NEW_COUNT=$(( ${#API_NAMES[@]} - EXISTING ))
echo "Rollback snapshot: $MANIFEST"
echo "  ${#API_NAMES[@]} flow(s) targeted; $EXISTING already exist in $ALIAS (restorable), $NEW_COUNT new."

# ── Step 2 — Confirmation (no auto-deploy) ───────────────────────────────────
# Deploy is always Draft — see Step 3 below for the force-Draft rewrite.
DEPLOY_STATUS="Draft"
if [[ $ASSUME_YES -ne 1 ]]; then
  echo
  echo "About to deploy ${#FLOWS[@]} flow(s) to org '$ALIAS' as $DEPLOY_STATUS:"
  for NAME in "${API_NAMES[@]}"; do echo "  - $NAME"; done
  printf "Proceed? [y/N] "
  read -r REPLY < /dev/tty || REPLY=""
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    echo "Aborted by user. Nothing deployed. Snapshot retained at $MANIFEST"
    echo "DEPLOY SUMMARY: 0 deployed, aborted (user declined)"
    exit 4
  fi
fi

# ── Step 3 — FR-013 deploy (real, leaves-first) ──────────────────────────────
# Deploy-boundary guarantee: every copy is force-set to <status>Draft</status>
# here, unconditionally — regardless of what transform_flow.py wrote, and
# regardless of what a hand-edited or non-transformer source file contains.
# This script never deploys an Active flow. The only way a migrated flow goes
# Active is a human clicking Activate in the org UI after validation and
# device testing (SKILL.md Step 8) — never a flag on this script.
WORKDIR=$(mktemp -d -t dcflow-deploy.XXXXXX)
trap 'rm -rf "$WORKDIR"' EXIT
mkdir -p "$WORKDIR/force-app/main/default/flows"
for FLOW in "${FLOWS[@]}"; do
  DEST="$WORKDIR/force-app/main/default/flows/$(basename "$FLOW")"
  cp "$FLOW" "$DEST"
  # Force <status>Draft</status> in the deploy copy. If the file has no
  # <status> element, inject one before </Flow>. Portable across BSD/GNU sed
  # via a Python one-liner. Source file on disk is never modified.
  SRC="$DEST" python3 - <<'PY'
import os, re
p = os.environ["SRC"]
s = open(p).read()
if re.search(r"<status>.*?</status>", s, flags=re.S):
    s = re.sub(r"<status>.*?</status>", "<status>Draft</status>", s, count=1, flags=re.S)
else:
    s = s.replace("</Flow>", "    <status>Draft</status>\n</Flow>", 1)
open(p, "w").write(s)
PY
done
cat > "$WORKDIR/sfdx-project.json" <<'JSON'
{
  "packageDirectories": [{"path": "force-app", "default": true}],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "67.0"
}
JSON

# No `2>&1`: keep CLI stderr warnings out of the JSON we parse. Deploy errors
# come back through --json as componentFailures.
OUTPUT=$(cd "$WORKDIR" && sf project deploy start \
  --source-dir "force-app/main/default/flows" \
  --target-org "$ALIAS" \
  --wait 60 \
  --json)
RC=$?

# Renderer prints the human status lines to stderr and the deployed/error counts
# ("<deployed> <errors>") on its single stdout line for the summary.
COUNTS=$(printf '%s' "$OUTPUT" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.stderr.write("      (could not parse sf output)\n"); print("? ?"); sys.exit(0)
r = d.get("result", {})
sys.stderr.write("Status: %s  Deployed: %s  Errors: %s\n" % (
    r.get("status"), r.get("numberComponentsDeployed", 0), r.get("numberComponentErrors", 0)))
for e in r.get("details", {}).get("componentFailures", []):
    sys.stderr.write("  ERROR: %s — %s\n" % (e.get("fullName"), e.get("problem")))
print("%s %s" % (r.get("numberComponentsDeployed", 0), r.get("numberComponentErrors", 0)))
')
DEPLOYED="${COUNTS% *}"
ERRS="${COUNTS#* }"

if [[ $RC -eq 0 ]]; then
  echo "DEPLOY SUMMARY: $DEPLOYED deployed as $DEPLOY_STATUS, $ERRS errors (org: $ALIAS)"
  echo "To roll back, see snapshot: $MANIFEST"
  exit 0
else
  echo "DEPLOY SUMMARY: deploy failed (org: $ALIAS) — see errors above. Snapshot: $MANIFEST"
  exit 1
fi
