---
name: field-service-data-capture-migrate
description: "Fully automated migration of Field Service Mobile flows (processType='FieldServiceMobile') to DataCaptureFlow. Retrieves flow XML from the org, runs a transformer script to restructure the execution graph and convert all field types, deploys the migrated flow as Draft only (activation is always a separate manual admin step after validation), and reports functional-equivalence differences. Handles most flows end-to-end without manual intervention. Always use this skill even for changes that look trivial, like removing one component or reordering one element — Data Capture's runtime behaves differently from Flow Builder previews, in ways only the transformer script accounts for. Use when a user wants to migrate, modernize, convert, audit, or replace legacy Field Service Mobile flow `.flow` / `.flow-meta.xml` files with Data Capture, or assess migration readiness. Do not use to edit an existing Data Capture flow or author a new one from scratch — covers only the one-time legacy migration."
metadata:
  version: "1.1"
  domains: ["Field Service"]
  minApiVersion: "67.0"
  cliTools:
    - tool: ["curl"]
      semver: ">=7.0.0"
    - tool: ["jq"]
      semver: ">=1.6.0"
    - tool: ["python3"]
      semver: ">=3.9.0"
    - tool: ["sf"]
      semver: ">=2.0.0"
  mcpTools:
    slack:
      tools: ["slack_create_canvas", "slack_send_message"]
      semver: ">=1.0.0"
  accessCheck:
    - type: "license"
      value: "Field Service"
---

# Migrate Field Service Mobile Flows to Data Capture

This skill migrates legacy Field Service mobile flows (`processType='FieldServiceMobile'`) to `DataCaptureFlow` using a fully automated XML transformer. The transformer handles all known migration patterns including field type conversion, execution graph restructuring, variable deduplication, and platform-event removal.

**Goal:** Get Field Service customers off Mobile Screen Flows and onto Data Capture — the strategic direction for Field Service digital forms.

```bash
SKILL_ROOT="${SKILL_ROOT:-${PLUGIN_ROOT:-$HOME/.vibe/skills}/field-service-data-capture-migrate}"
SCR="$SKILL_ROOT/scripts"
OUT="${FSM_OUT:-$PWD}"  # *_DC files land in cwd; override via FSM_OUT.
```

---

## Why migrate

| Capability | Mobile Screen Flow | Data Capture Flow |
|---|---|---|
| Conditional Visibility | No — workaround via separate screens | Yes — built-in, within a single screen |
| Cross-Field Validation | No — validates on "Next" only | Yes — real-time, immediate feedback |
| Offline | Yes — good (Briefcase priming) | Yes — better, offline-first, autosave/pause |
| Repeatable Sections | Yes — medium UX (Loop + screens) | Yes — better UX (native Repeater) |
| Mobile UX | Yes — good | Yes — better, fewer clicks, in-screen logic |
| Dependent Picklists | Yes — mobile only | Partial — conditional filtering only (roadmap) |
| Backoffice Completion | Yes — supported | No — roadmap |
| Form Edit after Submit | No — limited | No — roadmap |
| Future Proofing | No — legacy path | Yes — AI, Voice to Form, ongoing investment |

---

## Automated migration workflow

### Step 0 — Clarify migration scope FIRST

**Before querying the org, determine the user's intent.** If the request is ambiguous (e.g. "migrate flows", "migrate my org's flows"), ask explicitly whether they mean one specific flow, several named flows, or ALL Field Service Mobile flows in the org. **Only proceed to Step 1 after the scope is clear.** Never query all flows unless the user explicitly wants that.

### Step 1 — Discover flows

**REST API endpoint:** `GET /services/data/v67.0/tooling/query`, auth via `Authorization: Bearer <token>`. Use `curl --config` — `-H` leaks via `ps`/`/proc`.

```bash
# All Field Service Mobile flows:
# SOQL: SELECT Id, MasterLabel, ProcessType, Status, VersionNumber FROM Flow
#       WHERE ProcessType = 'FieldServiceMobile' AND Status IN ('Active','Draft')
#       ORDER BY MasterLabel, VersionNumber DESC
curl -X GET "https://<instance>.my.salesforce.com/services/data/v67.0/tooling/query?q=SELECT+Id%2C+MasterLabel%2C+ProcessType%2C+Status%2C+VersionNumber+FROM+Flow+WHERE+ProcessType+%3D+%27FieldServiceMobile%27+AND+Status+IN+%28%27Active%27%2C%27Draft%27%29+ORDER+BY+MasterLabel%2C+VersionNumber+DESC" \
  --config <(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN")

# One or more named flows — add: AND MasterLabel IN ('Work Order Wizard', 'Asset Inspection')
```

**Response format:**
```json
{
  "size": 2, "totalSize": 2, "done": true,
  "records": [
    {"Id": "301xx000000001", "MasterLabel": "Asset Inspection", "ProcessType": "FieldServiceMobile", "Status": "Active", "VersionNumber": 5}
  ]
}
```

URL-encoding: space → `+`/`%20`, `'`→`%27`, `,`→`%2C`, `(`/`)`→`%28`/`%29`, `=`→`%3D`.

**Surface the query results to the user** (table or list). If the user named specific flows and any are missing, report that immediately.

### Step 2 — Retrieve flow XML

**Handed the flow file(s) directly, no org?** Skip Steps 1–2 — run Step 4 on each in place (subflows first, `--is-subflow`), writing `<Name>_DC.flow-meta.xml` to the current dir, then skip Steps 5–6 (org-only). Otherwise retrieve from the org:

```bash
mkdir -p /tmp/fsm-migration/project && cd /tmp/fsm-migration/project
echo '{"packageDirectories":[{"path":"force-app","default":true}],"namespace":"","sourceApiVersion":"67.0"}' > sfdx-project.json

# Single flow:
sf project retrieve start --metadata "Flow:<FlowApiName>" --target-org <alias>
# Multiple (comma-separated, no spaces after commas):
sf project retrieve start --metadata "Flow:<Flow1>,Flow:<Flow2>" --target-org <alias>
# All flows (ONLY if the user explicitly confirmed "all" in Step 0):
sf project retrieve start --metadata "Flow" --target-org <alias>
```

**Critical:** `--metadata` must match the user's Step 0 selection — never retrieve all flows unless explicitly confirmed. (No REST equivalent exists yet for this step — see `references/architecture-notes.md`.)

### Step 3 — Validate migration candidates

Only flows with BOTH `FieldServiceMobile` processType AND at least one `<screens>` element are valid candidates:

```bash
migratable=()
for f in force-app/main/default/flows/*.flow-meta.xml; do
  base=$(basename "$f" .flow-meta.xml)
  if grep -q "FieldServiceMobile" "$f"; then
    if grep -q "<screens>" "$f"; then
      echo "[MIGRATABLE] $base"; migratable+=("$f")
    else
      echo "[NO SCREENS] $base — cannot migrate (pure automation flow)"
    fi
  else
    processType=$(grep -oP '(?<=<processType>)[^<]+' "$f" || echo "unknown")
    echo "[NOT FSM] $base — processType is '$processType'"
  fi
done | sort
echo "Migratable flows: ${#migratable[@]}"
```

If the user specified particular flows and any fail validation, **STOP and report the issue** — don't proceed with partial migration unless the user confirms skipping the invalid ones. If the user confirmed "migrate all", this filters to the migratable subset — report counts before proceeding. Pure automation flows (no `<screens>`) should stay as-is or become AutoLaunched flows; flag but don't migrate them.

### Step 3b — Resolve the subflow dependency tree (composed flows)

Flows that call subflows must migrate **leaves-first** — a caller can't validate until every `_DC` subflow it references exists in the deploy set:

```bash
python3 "$SCR/discover_subflow_tree.py" \
  force-app/main/default/flows \
  force-app/main/default/flows/<CallerFlowApiName>.flow-meta.xml \
  --json /tmp/fsm-migration/subflow-tree.json
```

| Exit | Meaning | Action |
|---|---|---|
| `0` | Every node is migratable | Transform in the printed order (Step 4), then bundle-validate (Step 5) |
| `1` | ≥1 dependency blocked (not FSM, no screens, cycle) or missing | **STOP — do not deploy the caller.** Report the blocking node(s). |
| `2` | Usage error | Pass a flows dir and at least one caller path (or `--all`) |

Use the JSON `order` array as the transform order for Step 4 and the file list for Step 5.

### Step 4 — Transform each flow

```bash
OUT="${FSM_OUT:-$PWD}"; mkdir -p "$OUT"
# Input: the retrieved project path below, or just <FlowApiName>.flow-meta.xml if handed the file.
python3 "$SCR/transform_flow.py" \
  force-app/main/default/flows/<FlowApiName>.flow-meta.xml \
  "$OUT/<FlowApiName>_DC.flow-meta.xml"
```

**Pass `--is-subflow` for every node the Step 3b tree reports at `depth > 0`.** A DataCaptureFlow subflow cannot contain Create/Update/Delete — `--is-subflow` excises CUD unconditionally (not just reordering it) and routes CUD fault-path violations through the fault-severing pre-pass; the plain treatment is correct only for the top-level caller (`depth == 0`). Skipping it on a real subflow reproduces the "You can't use Create, Update, or Delete elements in a Data Capture flow subflow" deploy failure Step 3b prevents.

Use `python3 "$SCR/subflow_names.py" <FlowApiName>` to derive the correct output filename — for overridden names a plain `_DC` suffix won't match the caller's rewritten reference and the bundle dry-run will fail.

The transformer reports fields converted, CUD fixes, and warnings. Unsupported elements (Apex/action calls, subflows, fault paths, custom components, unknown field types) produce an `_incompleteMigration` list and an `<!-- INCOMPLETE MIGRATION ... -->` XML comment; unsupported field slots become read-only `DisplayText` placeholders, never silent `ShortText` inputs.

**Batch transform in parallel** — each flow's transform is independent, so use a bounded `xargs -P4` instead of a sequential loop. When Step 3b produced `subflow-tree.json`, look up each flow's `depth` there to decide whether to add `--is-subflow`; a flow absent from the tree (no composed dependencies) is always the top-level caller:

```bash
OUT="${FSM_OUT:-$PWD}"; mkdir -p "$OUT"
TREE=/tmp/fsm-migration/subflow-tree.json
find force-app/main/default/flows -maxdepth 1 -name '*.flow-meta.xml' -print0 \
  | while IFS= read -r -d '' f; do
      grep -q "FieldServiceMobile" "$f" && grep -q "<screens>" "$f" && printf '%s\0' "$f"
    done \
  | xargs -0 -I{} -P4 bash -c '
      f="{}"; base=$(basename "$f" .flow-meta.xml)
      dcname=$(python3 "'"$SCR"'/subflow_names.py" "$base")
      subflowFlag=""
      if [ -f "'"$TREE"'" ]; then
        depth=$(jq -r --arg n "$base" "(.order[] | select(.apiName == \$n) | .depth) // 0" "'"$TREE"'")
        [ "$depth" -gt 0 ] 2>/dev/null && subflowFlag="--is-subflow"
      fi
      python3 "'"$SCR"'/transform_flow.py" "$f" "'"$OUT"'/${dcname}.flow-meta.xml" $subflowFlag 2>&1 \
        | grep -E "(Transformed|SKIPPED|CUD|Warning)"
    '
```

Safe even for a composed tree — each transform reads no leaf output (one flow in, one flow out), so nothing needs sequencing here; the leaves-first order from Step 3b only matters for the Step 5 bundle dry-run.

**Output name collisions:** two source flows must never resolve to the same `dcname` via `subflow_names.py` — under `-P4` that's a concurrent write to the same file. If the batch has any name overrides, spot-check afterward: `find "${FSM_OUT:-$PWD}" -maxdepth 1 -name '*_DC.flow-meta.xml' | sort | uniq -d`.

### Step 4b — Generate migration summary

```bash
SUM=/tmp/fsm-migration/summaries; mkdir -p $SUM /tmp/fsm-migration/spec
find force-app/main/default/flows -maxdepth 1 -name '*.flow-meta.xml' -print0 \
  | while IFS= read -r -d '' f; do
      grep -q "FieldServiceMobile" "$f" && grep -q "<screens>" "$f" && printf '%s\0' "$f"
    done \
  | xargs -0 -I{} -P4 bash -c '
      f="{}"; base=$(basename "$f" .flow-meta.xml)
      python3 "'"$SCR"'/convert_to_dc_spec.py" "$f" "/tmp/fsm-migration/spec/${base}.json"
      python3 "'"$SCR"'/generate_summary.py" \
        "/tmp/fsm-migration/spec/${base}.json" \
        "'"$SUM"'/${base}-migration-summary.md"
    '
```

The summary lists the component mapping (`[OK]`/`[WARNING]`/`[ERROR]` prefixes), conditional-logic decisions, unsupported components, behavioral notes, an offline-priming warning, a manual Review Checklist, and a clearly-labeled Advisory placeholder (the only place AI-generated prose belongs). `generate_summary.py` is deterministic and always writes this `.md` — it's both the input to the canvas in Step 4c and the offline fallback artifact.

### Step 4c — Ask how to deliver the review, then publish

**Ask explicitly, if interactive — never silently default:** "Post the migration summary to Slack, or download it as an `.md` file?" The per-flow `.md` from Step 4b exists either way; this only decides whether a Slack canvas also gets created.

- **Slack:** ask for the destination channel and wait for it — never create a canvas without one (offer a remembered channel, but confirm). Canvas creation is the `slack_create_canvas` MCP tool (Python can't reach it). Per flow: read `${base}-migration-summary.md`, strip the leading `# Migration Summary: <formTitle>` H1 (the canvas takes the title separately), create a canvas titled `Migration Summary: <formTitle>` with the rest as content, `slack_send_message` posts its link into the channel, record the URL for Step 7. Remember the channel.
- **File download:** point to the `.md` path(s) already written in Step 4b — nothing further to do.

**Fallback:** no interactive user, or Slack unavailable / canvas errors — skip to the `.md` path(s); the run succeeds either way.

### Step 5 — Validate (dry-run)

Optional, non-destructive pre-deploy gate — only when an org alias is available. **Ask before running** (costs wall-clock, not required for output; offline runs skip it and still succeed): _"Run dry-run validation against `<alias>` before deploying? (yes/no)"_ If the SE declines, treat as exit `3` below: deploy **as Draft only** (the only status this skill ever deploys).

**Default to one bundle dry-run, not one per flow** — this lets intra-tree `_DC` subflow references resolve within the deploy set (an isolated per-flow dry-run fails on a caller whose subflows aren't deployed yet). Fall back to per-flow only if the bundle fails on >1 flow and you need to attribute it:

```bash
OUT="${FSM_OUT:-$PWD}"
set --
while IFS= read -r -d '' f; do set -- "$@" "$f"; done \
  < <(find "$OUT" -maxdepth 1 -name '*_DC.flow-meta.xml' -print0)
if [ "$#" -gt 0 ]; then
  "$SCR/validate_flow.sh" --bundle "<alias>" "$@"
  code=$?
  if [ "$code" -eq 1 ] && [ "$#" -gt 1 ]; then
    echo "Bundle dry-run failed — re-running per-flow to attribute the failure(s):"
    "$SCR/validate_flow.sh" "<alias>" "$@"
    code=$?
  fi
else
  echo "No migrated flows to validate."; code=0
fi
```

In per-flow fallback, a caller referencing `_DC` subflows fails even when it's fine (its subflow isn't in that isolated deploy set) — treat a `flow doesn't exist` failure on a known caller as this isolation artifact, not a real defect.

| Exit | Meaning | Action |
|---|---|---|
| `0` | All flows validated clean | Proceed to Step 6 and deploy (Draft) |
| `1` | ≥1 flow failed dry-run or file not found | Deploy as Draft if you want the output in-org for manual repair; otherwise fix the transformer gap and re-validate. |
| `2` | Usage error (zero arguments) | Should be prevented by the existence guard above |
| `3` | No target org — validation skipped | Expected offline; output is valid, validation deferred |

`deploy_flow.sh` always deploys Draft regardless of dry-run outcome — a failed dry-run just means the deploy isn't worth doing yet.

**Optional live smoke test (manual — not in CI).** The bundle dry-run proves the script's contract; running it once against a real org proves the output actually deploys:

```bash
"$SCR/validate_flow.sh" <org-alias> "${FSM_OUT:-$PWD}/<FlowApiName>_DC.flow-meta.xml"
# Expected: exit 0, "PASS  <FlowApiName>_DC.flow-meta.xml"
```

### Step 6 — Deploy (kickoff + rollback snapshot)

```bash
OUT="${FSM_OUT:-$PWD}"
set --
while IFS= read -r -d '' f; do set -- "$@" "$f"; done \
  < <(find "$OUT" -maxdepth 1 -name '*_DC.flow-meta.xml' -print0)

"$SCR/deploy_flow.sh" <alias> "$@"
```

`deploy_flow.sh` captures a **pre-deploy rollback snapshot** of every target flow's prior org state before writing anything, then deploys only after **explicit SE confirmation** (`Proceed? [y/N]`; pass `--yes` to skip for an unattended demo). Every deploy is **Draft only** — the deploy copy's `<status>` is force-rewritten to `Draft` regardless of source content, so nothing here can deploy Active. Activation is the manual Step 8 action.

| Exit | Meaning | Action |
|---|---|---|
| `0` | Deploy succeeded | Proceed to Step 7. Snapshot path is printed for rollback. |
| `1` | Deploy failed, snapshot query failed, or a flow file was missing | **STOP.** Read the component errors under `Status:`. |
| `2` | Usage error (no flow files) | `find` matched nothing — check the output dir |
| `3` | No target org — deploy skipped | Expected offline; nothing was written |
| `4` | SE declined the confirmation prompt | Nothing was written; the snapshot is retained for reference |

**Rollback snapshot:** written to `/tmp/fsm-migration/rollback/<timestamp>/snapshot.json`, recording per-flow whether it `existedBeforeDeploy` and (if so) its prior label/active-version/latest-version IDs. To restore, re-deploy the version identified in the snapshot — but confirm no one edited the deployed `_DC` flow after this deploy, or that edit is lost.

**Deploy order:** subflows (leaves) before their callers — use the `discover_subflow_tree.py` `order` sequence from Step 3b.

### Step 7 — Verify and report

```bash
# REST API: GET /services/data/v67.0/tooling/query
# SOQL: SELECT MasterLabel, Status FROM Flow
#       WHERE ProcessType = 'DataCaptureFlow' AND Status IN ('Draft','Active') ORDER BY MasterLabel
curl -X GET "https://<instance>.my.salesforce.com/services/data/v67.0/tooling/query?q=SELECT+MasterLabel%2C+Status+FROM+Flow+WHERE+ProcessType+%3D+%27DataCaptureFlow%27+AND+Status+IN+%28%27Draft%27%2C%27Active%27%29+ORDER+BY+MasterLabel" \
  --config <(printf 'header = "Authorization: Bearer %s"\n' "$TOKEN")
```

**Response format:**
```json
{
  "size": 3, "totalSize": 3, "done": true,
  "records": [
    {"MasterLabel": "Asset Inspection_DC", "Status": "Active"}
  ]
}
```

```bash
# Functional equivalence check (runs on the SOURCE FieldServiceMobile flow, not the _DC output):
python3 "$SCR/analyze_flow.py" \
  force-app/main/default/flows/<FlowApiName>.flow-meta.xml \
  /tmp/fsm-migration/analysis/<FlowApiName>.json
```

Surface any warnings to the user before they manually activate (Step 8).

**Publish the aggregate run-report** after the batch, matching the delivery picked in Step 4c. Include: flows migrated (count + names), dry-run/deploy outcomes per flow (by exit code), aggregate GREEN/YELLOW/RED/SKIP risk counts, total `[WARNING]`/`[ERROR]` component counts, and per-flow report links/paths.

- **Slack:** one aggregate canvas linking each per-flow canvas from Step 4c, posted into the same destination.
- **File download:** list the per-flow `.md` paths from Step 4b as the aggregate report — no separate file needed.

### Step 8 — Activate and deactivate legacy

The **only** way a migrated flow goes live — nothing here activates a flow automatically. Once validated in Flow Builder and tested on device: open the DC flow and click **Activate**, then deactivate the old Field Service Mobile Flow (leave it inactive; don't delete until fully validated).

---

## How the transformer works

`transform_flow.py` is a direct XML-to-XML transformer covering field-type conversion, required-element injection, label placement, and CUD-at-end graph restructuring (4 patterns, up to 50 convergence iterations) — see `references/transformer-rules.md` for the complete field-type mapping table and the full list of automatic fixes plus what changes behaviorally after migration (lookup execution order, platform events, confirmation-screen placement, constants).

## Patterns that cannot be automated (require Flow Builder redesign)

| Pattern | Why it can't be automated | Recommended redesign |
|---|---|---|
| **No screens (pure automation)** | DataCaptureFlow requires at least one screen | Keep as Field Service Mobile Flow, or convert to AutoLaunchedFlow |
| **Screen inside a loop** | DC doesn't support screens inside loops (detected + warned) | Replace loop+screen with a DC native **Repeater** field |
| **Lookup depends on just-created record** | `Create → Get (by new ID) → Create again` cycle; DC requires all CUD at end | Do all lookups before screens, accumulate in variables, batch-create at the end |
| **Confirmation screen shown after CUD** | DC requires screens before CUD | Move to a pre-CUD summary screen, or use DisplayText to preview what will be saved |
| **Backoffice/desktop completion needed** | DC forms complete only on FSL Mobile (roadmap) | Keep on Field Service Mobile Flow until roadmap ships |
| **Full dependent picklists** | DC only supports conditional filtering today (roadmap) | Use conditional visibility as workaround |

## Migration risk classification

| Risk | Criteria | Automated? |
|---|---|---|
| **GREEN** | No screens in loop, no create→lookup cycles, no platform events | Yes — fully automated |
| **YELLOW** | Platform events, hoisted post-screen lookups, constants, `isRequired` on hidden fields, or complex DisplayText formulas | Yes — automated with warnings, review before activating |
| **RED — restructurable** | CUD violations the graph restructurer fixes automatically | Yes — automated, transformer resolves these |
| **RED — requires redesign** | Screen inside loop, create→lookup cycle, `Range` slider fields | No — manual Flow Builder redesign required |
| **SKIP** | No screens — pure automation flow | No — not a DataCaptureFlow candidate |

For the authoritative DataCaptureFlow platform rules (required headers, structure rules, accessor suffixes, DisplayText limitations, Repeater specifics, global variable allowlist) — consult `references/dc-platform-rules.md` when debugging deploy errors or validating a migrated flow manually. For a table of real deploy errors and their fixes, see `references/known-deploy-errors.md`. For which steps above still require the `sf` CLI vs. REST, and why, see `references/architecture-notes.md`.

## What to check before activating

After deploying, open each DC flow in Flow Builder and verify:

1. **Review transformer warnings** — any hoisted lookup that filtered on a screen field needs manual attention
2. **Platform events removed** — if the original fired real-time dispatcher events, plan a replacement trigger (Apex or AutoLaunched flow)
3. **`isRequired` on hidden fields** — clear `isRequired` and add a `validationRule` instead, for anything the transformer flagged
4. **DisplayText formulas** — pre-calculate `IF`/`CASE`/date-math results in an Assignment and reference a simple variable instead
5. **Calculation timing** — confirm the calculation element sits on a screen BEFORE the display screen, not on the same screen
6. **Screen order and labels** — confirm the reordered screens still make sense
7. **Lookup display** — confirm Lookup fields show the right label; adjust Primary Compact Layout if needed
8. **`Range` slider fields** — replace manually with `dcNumeric` or `dcCounter`
9. **Test on FSL Mobile** — complete the form end-to-end on a device
10. **Test offline** — airplane mode + complete form → reconnect → verify sync

---

## Files in this skill

- **`scripts/transform_flow.py`** — primary migration tool; direct XML-to-XML transformer. Run on each source flow (Step 4).
- **`scripts/subflow_names.py`** — single source of truth for the migrated-subflow naming rule; imported by `transform_flow.py` and `discover_subflow_tree.py`.
- **`scripts/discover_subflow_tree.py`** — transitive subflow dependency discovery; builds the leaves-first order and classifies each node migratable/blocked/missing (Step 3b).
- **`scripts/analyze_flow.py`** — risk-assessment tool; runs on the source flow, produces JSON without modifying it (Step 7).
- **`scripts/convert_to_dc_spec.py`** — spec converter used for the migration summary (Step 4b); its JSON output must match `scripts/vendor/build_flow.py`'s input contract (see `references/converter-builder-contract.md`).
- **`scripts/generate_summary.py`** — renders the human-readable `migration-summary.md` from the spec JSON (Step 4b); deterministic and offline.
- **`scripts/validate_flow.sh`** — dry-run validator wrapping `sf project deploy start --dry-run`; exit `0`=all passed, `1`=≥1 failed, `2`=usage, `3`=skipped (no org) (Step 5).
- **`scripts/deploy_flow.sh`** — deploy kickoff + rollback snapshot; exit `0`=deployed, `1`=failed, `2`=usage, `3`=skipped, `4`=SE declined (Step 6).
- **`scripts/fsm_dc_catalog.py`** — authoritative FSM↔DC capability-parity catalog; `FIELD_TYPE_MAP` here must stay in sync with the mapping table in `references/transformer-rules.md`.
- `scripts/cud_analysis.py`, `scripts/flow_input.py`, `scripts/flow_xml_utils.py`, `scripts/json_to_flow_xml.py`, `scripts/manual_review_flags.py` — shared internals imported by the scripts above.
- `scripts/retrieve_flow_rest.sh` — experimental REST-based flow retrieval; not yet wired into Step 2 (see `references/architecture-notes.md`).
- `scripts/vendor/build_flow.py` — vendored Data Capture builder script consumed by `convert_to_dc_spec.py`'s contract.
- `references/fsm-dc-capability-catalog.md` — human-readable twin of `fsm_dc_catalog.py`; source of truth for supported/unsupported decisions.
- `references/component-mapping.md` — component equivalence table (companion to the catalog above).
- `references/converter-builder-contract.md` — authoritative JSON contract between `convert_to_dc_spec.py` and `build_flow.py`.
- `references/migration-checklist.md` — manual validation checklist for post-deploy testing.
- `assets/sample-legacy-flow.flow-meta.xml` — representative legacy `FieldServiceMobile` flow for trying the transformer end-to-end.
