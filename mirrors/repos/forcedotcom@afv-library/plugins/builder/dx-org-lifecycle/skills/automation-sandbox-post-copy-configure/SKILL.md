---
name: automation-sandbox-post-copy-configure
description: "Apply a Salesforce sandbox post-copy automation JSON config against a target org. Use when the user asks to apply, run, execute, dry-run, or preview a post-copy or post-refresh config file (e.g. `post-copy-config.json`) against a sandbox — including activating/deactivating a Flow (PATCH `FlowDefinition.Metadata.activeVersionNumber` to the version, or `null`), re-pointing an OBM endpoint, updating a RemoteSiteSetting URL, or re-scheduling a ScheduledApex job after refresh. Also trigger for phrasings like \"apply post-copy config\", \"run post-copy automation\", \"activate Flow <name> post-refresh\", \"deactivate Flow <name>\", \"re-point outbound messages after refresh\", or \"configure sandbox after refresh\". Per entry, derive the Tooling API sobject, verify via describe, resolve the Id via SOQL, then PATCH the compound `Metadata` field (`ScheduledApex` uses anonymous Apex). DO NOT TRIGGER for generating config JSON from an SOP (use `automation-sandbox-post-copy-config-generate`) or for deploying metadata XML."
allowed-tools: Bash Read Write
metadata:
  relatedSkills:
    - "automation-sandbox-post-copy-config-generate"
    - "dx-org-permission-set-assign"
    - "platform-metadata-deploy"
  version: "1.3"
  domains: ["Automation"]
  cliTools:
    - tool: ["curl"]
      semver: ">=7.0.0"
    - tool: ["jq"]
      semver: ">=1.6"
    - tool: ["node"]
      semver: ">=18.0.0"
    - tool: ["sf"]
      semver: ">=2.0.0"
---

# Automation: Sandbox Post-Copy Configure

Apply a Salesforce sandbox post-copy automation JSON config to a target
org. Four canonical `ConfigurationName` values are pinned:
`OutboundMessages` + `RemoteSiteSettings` → compound-`Metadata` PATCH
(Steps A–E); `ScheduledApex` → anonymous-Apex (Step F) since
`CronTrigger` is read-only; `Flows` → flow-activation (Step G), same
compound-`Metadata` transport as A–E with fixed mutation key
`activeVersionNumber` + state-aware pre-flight (`ALREADY_ACTIVE` /
`ALREADY_INACTIVE`). Non-canonical names are derived + describe-verified.
Every A–E entry must pass Step B (describe 200 + `Metadata` compound
field) before any PATCH is planned; Step B skipped for `ScheduledApex`.
Unverified entries are surfaced in the summary and skipped — never
guessed at.

## Tool Restrictions

**Use ONLY the Bash tool** to execute `sf` CLI commands (`sf data query
--use-tooling-api`, `sf api request rest`, `sf org display`). Do NOT
use MCP tools like `execute_soql` — the compound `Metadata` PATCH
pattern this skill requires is not available through MCP wrappers.
Invoke `sf` **without** `--target-org` when the user didn't name an
alias (the harness sets the CLI default); never pass `--target-org
default` (`NamedOrgNotFoundError`). SOQL-over-REST is same-OAuth —
no direct DB / non-Salesforce SQL access.

## STOP — do this before making any API call

Never call the org from memory. Before the first request:

1. Read the config JSON end-to-end from the exact path the user gave
   (default `./post-copy-config.json`). Every entry must have all five
   keys (`ConfigurationName`, `Label`, `Fields`, `IsActive`,
   `ExecutionOrder`). If any entry is malformed, abort and surface the
   file path + entry index — do **not** partially apply. **Do not
   invent entries.** If the file is missing, stop and ask; never
   fabricate a plan against synthetic labels.
2. For each distinct `ConfigurationName` in the config, run the
   derivation + describe-verify step (below) **before** planning any
   PATCH. An entry whose API cannot be verified must never appear as
   a planned PATCH — it is rejected up front.
3. Confirm the target org alias with the user unless they supplied one
   explicitly. This skill mutates a live org — writing to the wrong
   org (e.g., a production alias set as default) is the most expensive
   failure mode.

If you announce "I will apply … now" without having read the config
file and run the describe-verify for every distinct
`ConfigurationName`, stop and do those first.

---

## Per-entry procedure (the core of this skill)

The skill carries a pinned mapping for the canonical types below, and
a derive-then-verify path for anything else. Follow these steps **for
every entry**, in order. `Step B` (describe-verify) is mandatory
regardless of whether the mapping came from the pinned table or the
derive path — its HTTP status must appear in the summary.

### Step A — Resolve the Tooling API sobject and lookup filter

**Pinned canonicals (authoritative — use these exactly, do NOT
substitute a different sobject name):**

| ConfigurationName | Tooling API sobject | Record-lookup SOQL |
|-------------------|---------------------|--------------------|
| `OutboundMessages`   | `WorkflowOutboundMessage` | `SELECT Id, FullName FROM WorkflowOutboundMessage WHERE EntityDefinition.QualifiedApiName = '<Fields.Object>'` — then client-side pick the row whose `FullName == '<Fields.Object>.<Label>'`. SOQL cannot filter on `FullName` directly for this sobject. |
| `RemoteSiteSettings` | `RemoteProxy`             | `SELECT Id, SiteName FROM RemoteProxy WHERE SiteName = '<Label>'`. |
| `ScheduledApex`      | `CronTrigger` (read-only — Anonymous Apex route, see Step F) | See Step F — pre-flight `SELECT Id FROM CronTrigger WHERE CronJobDetail.Name = '<escaped>'` gate. |
| `Flows`              | `FlowDefinition` (compound-`Metadata` PATCH with fixed `activeVersionNumber` mutation — see Step G) | See Step G — pre-flight `SELECT Id, DeveloperName, ActiveVersion.VersionNumber FROM FlowDefinition WHERE DeveloperName = '<Fields.FlowApiName>'`. |

For canonical entries use the pinned sobject + SOQL as-is; skip
"derive". Do not invent `OutboundMessage`, `RemoteSiteSetting`, or
`MasterLabel` variants. Field-name resolution (overrides + case rule
+ existence check) is owned by `scripts/map-metadata-key.mjs`.

**Non-canonical**: derive a candidate (usually singular of the
Metadata API type name); Step B rules out wrong guesses. Use the
generic SOQL patterns in Step C.

### Step B — Verify the candidate exists and supports Metadata writes

For each candidate, GET the describe:

```bash
sf api request rest \
  "/services/data/v<apiVersion>/tooling/sobjects/<Candidate>/describe/"
```

Accept the candidate only if **both** are true:

- HTTP 200 (the sobject exists on this org's Tooling API), AND
- The describe response's `fields` array contains a field named
  `Metadata` (compound field — this is what PATCH writes through).

If no candidate passes both gates, mark the entry
`API_NOT_IDENTIFIED` and skip. **Do not guess a REST path** — the
wrong path 404s in the best case and updates the wrong record in the
worst case.

### Step C — Resolve the record Id (SOQL-over-REST)

**For pinned canonicals**: run the SOQL from the Step A table
verbatim (substituting `<Label>` / `<Fields.Object>`). Do not
substitute a different filter column such as `MasterLabel` — the
pinned SOQL is the tested-and-correct filter for that sobject.

**For non-canonical (derived) sobjects**: query the verified sobject
for the record identified by the entry's `Label` (and `Fields.Object`
when present):

```bash
# SOQL to a variable + separate jq call — avoids the most common
# shell-quoting failure in this skill.
SOQL='SELECT Id, FullName FROM <VerifiedSobject> WHERE <UniqueFilter>'
sf data query --use-tooling-api --json --query "$SOQL" \
  > /tmp/entry-<Slug>-lookup.json
ID=$(jq -r '.result.records[0].Id // empty' /tmp/entry-<Slug>-lookup.json)
```

Pick `<UniqueFilter>` based on the queryable fields shown in the
describe response from Step B. If the row contains a `FullName` field,
SOQL usually rejects a direct `FullName = ...` filter — filter by
whichever direct column the describe surfaces (e.g.
`EntityDefinition.QualifiedApiName`, `DeveloperName`, `SiteName`) and
apply the `FullName` match client-side (`jq -r
'.result.records[] | select(.FullName == "<Object>.<Label>") | .Id'`).

Outcomes:

- Zero rows → `NOT_FOUND` (never fall back to insert).
- Multiple rows after client-side filtering → `AMBIGUOUS` (surface
  all Ids in the summary and skip; a wrong Id is worse than no Id).
- Exactly one row → proceed to Step D.

### Step D — GET current Metadata, mutate, PATCH back

`Metadata` is **replace-in-full** — omitted keys are blanked on
PATCH. Preserve every existing key from the Step D-1 GET; overlay
only the mutated keys. The summary's "planned PATCH body" (apply
and dry-run) is this full merged object — verbose or org-specific
values may render as `"<preserved-from-GET>"` in dry-run, but
every key must be present.

Every Step D filename must include the record `<Id>` from Step C
(e.g. `/tmp/entry-<Id>-meta.json`) — phase-parallel entries share
the working directory and would clobber a shared name.

1. **GET** current `Metadata` → `/tmp/entry-<Id>-meta.json`.
2. **Resolve the mutation key** (generic path only; `Flows` take
   Step G's fixed `activeVersionNumber` and `ScheduledApex` takes
   Step F's anonymous Apex — never run this script for either) —
   for each `Fields.<Xxx>`, run
   `node scripts/map-metadata-key.mjs "<ConfigurationName>"
   "<ConfigFieldName>" /tmp/entry-<Id>-meta.json`. On
   `{"status":"OK","key":...}` use the returned key. On
   `{"status":"FIELD_MAP_UNKNOWN",...}` mark the entry and skip.
   Do NOT skip this script and infer via naive first-char-lowercase:
   `RemoteSiteSettings.Fields.RemoteSiteUrl` maps to `Metadata.url`
   (not `remoteSiteUrl`); the script owns such overrides.
3. **PATCH** — heredoc-build `/tmp/entry-<Id>-mutation.json`, merge
   with `jq --slurpfile m /tmp/entry-<Id>-mutation.json
   '. + $m[0] | {Metadata: .}' /tmp/entry-<Id>-meta.json >
   /tmp/entry-<Id>-patch.json` (preserves JSON types), PATCH with
   `-b @/tmp/entry-<Id>-patch.json`, capture the response body to
   `/tmp/entry-<Id>-response.json`. Full bash in
   `references/api_endpoints.md` §Step D. Never use `--arg`
   (stringifies booleans/numbers, breaks on special chars). Wrap
   the PATCH in `for attempt in 1 2; do <cmd> && break; done` —
   retry once on shell/jq quoting failure (non-zero exit *before*
   the HTTP call goes out).
4. **Classify** — `node scripts/classify-patch-result.mjs
   "<httpCode>" /tmp/entry-<Id>-response.json`. Exit 0 → `SUCCESS`;
   exit 2 → `FAILED` (parsed error on stdout). 204 with a non-empty
   body is `FAILED`.

### Step E — Verify the change landed

Re-read the record to confirm the PATCH stuck:

- If the mutated field is a direct-queryable SOQL column on the
  sobject (rare — most `Metadata`-writable fields are not), a SELECT
  by Id is enough.
- Otherwise GET the record and inspect the corresponding key inside
  `.Metadata`.

If the read-back value doesn't match the requested value, record
`FAILED_VERIFY` — the PATCH returned 204 but the effect is not
visible (usually a naming or permission issue).

### Step F — Scheduled Apex (anonymous Apex route)

**Read `references/scheduled_apex_path.md`** — Steps A–E do not apply
(`CronTrigger` is read-only). The reference owns the F-1→F-4
anonymous-Apex recipe (pre-flight AMBIGUOUS gate, snippet build,
`sf apex run`, verify, dry-run) and the Step-F summary shape.

### Step G — Flow activation / deactivation (`Flows`)

**Read `references/flow_activation_path.md`** — Steps A + B still
apply (`FlowDefinition` is the pinned sobject; Step B confirms the
`Metadata` compound field). The reference owns the G-1→G-4
compound-`Metadata` PATCH recipe with fixed mutation key
`activeVersionNumber` (Step D-2 key derivation does NOT apply),
decision rules (`FlowApiName` validation, `ALREADY_ACTIVE` /
`ALREADY_INACTIVE` short-circuits, forbidden sibling keys), the
dry-run contract, and the Flows summary shape.

---

## IsActive semantics

- `IsActive: true`  → PATCH per Steps A–E (or Step G for `Flows`).
- `IsActive: false` → **do not PATCH**. Record `SKIPPED_INACTIVE`
  and add a Follow-ups bullet with the entry's `ConfigurationName`
  + `Label` so the customer sees it was left untouched.

Rationale: `IsActive: false` means "not active in this sandbox",
not "deactivate the existing record" — silently deactivating a
live integration is a much larger blast radius than leaving it.

---

## Canonical output shape (always emit this)

Single Markdown summary written to `./post-copy-<mode>-summary.md`
(mode is `dry-run` or `apply`) AND printed to the user. No JSON
side-files (`plan/phases.json`, `requests/*.request.json`, etc.) —
inline every planned/actual request in the Markdown.

**`Flows` and `ScheduledApex` use step-specific summary shapes** —
labeled narrative blocks that REPLACE the generic `Planned request:`
block below (phase table unchanged); see each reference's "Summary
shape" section. All other `ConfigurationName`s use the generic shape.

**Phase enumeration is script-owned.** Run `node scripts/plan-phases.mjs
<config.json>` and consume its `phases[]` verbatim — each entry carries
`ordinal` (1-indexed for headings) and `executionOrder` (raw, for
`(ExecutionOrder = <raw>)`); sparse values collapse; `IsActive:false`
entries are pre-marked `SKIP_INACTIVE`. See
`references/execution_phasing.md` for the worked example.

**Target-org resolution is script-owned.** Run `node
scripts/resolve-target-org.mjs`; substitute the returned `.alias` into
the header. Never emit `<env:SF_TARGET_ORG>` or `$SF_TARGET_ORG`
verbatim.

For dry-run entries the `HTTP` column is `—`. End the summary with:
`No PATCH requests were issued. To apply, re-run without the dry-run
flag.`

```markdown
# Post-Copy Configure Run — <N> entries <planned|applied> against `<alias>`

Config file: `<path>`
Target org: `<alias>`
Mode: <dry-run|apply>

## Phase <ExecutionOrder> — <count> entr(y|ies)

Planned request:
- Method: `PATCH`
- Path: `/services/data/v<apiVersion>/tooling/sobjects/<VerifiedSobject>/<Id>`
- Body: `<FULL merged Metadata: every key from the Step D-1 GET overlaid with the mutated keys. Verbose/org-specific values may render as "<preserved-from-GET>", but every key must be present. NEVER emit a minimal body.>`

| ConfigurationName | Label | Object | Sobject | Describe | Outcome | HTTP |
|-------------------|-------|--------|---------|----------|---------|------|
| <name>            | <lbl> | <obj>  | <VerifiedSobject> | <200 or 404> | <outcome> | <code> |

## Totals

| Outcome | Count |
|---------|-------|
| <state> | <n>   |

## Follow-ups

- <bullet per SKIPPED_INACTIVE / API_NOT_IDENTIFIED / AMBIGUOUS / FIELD_MAP_UNKNOWN / NOT_FOUND entry>
```

Column semantics: `Object` = entry's `Fields.Object` or `—`. `Sobject`
= Step A resolved sobject. `Describe` = Step B HTTP status (`200`
verified, `404` → `API_NOT_IDENTIFIED`) — mandatory so skipped Step Bs
are visible. Outcome vocabulary: `SUCCESS`, `NOT_FOUND`, `AMBIGUOUS`,
`API_NOT_IDENTIFIED`, `FIELD_MAP_UNKNOWN`, `FAILED`, `FAILED_VERIFY`,
`SKIPPED_INACTIVE`, `SKIPPED`, `DRY_RUN`, `DELETE_NOT_SUPPORTED`,
`ALREADY_ACTIVE` (Flows: requested version already active — no PATCH),
`ALREADY_INACTIVE` (Flows: Deactivate but already inactive — no PATCH),
`NOT_ATTEMPTED`.

**Scripts are internal** — never inline raw `node scripts/…` stdout or
"I ran node …" narration into the summary; consume the JSON, use the
returned values, render the exact shape above.

## Scope

- **In scope**: Apply a post-copy config JSON against a live org —
  phase-group by `ExecutionOrder`, derive+verify sobject, resolve Id
  via SOQL-over-REST, PATCH via compound `Metadata`, report outcomes.
- **Out of scope**: Generating the config JSON from an SOP (delegate
  to `automation-sandbox-post-copy-config-generate`); metadata-XML
  deploys; the ATF Java orchestrator; guessing an API path for an
  entry whose describe probe fails (`API_NOT_IDENTIFIED` → stop).

Live-org mutation tool: prefer `--dry-run` first; never silently
retry a failed entry against a different endpoint.

---

## Required Inputs

Gather or infer before applying:

- **Config file path**: JSON from
  `automation-sandbox-post-copy-config-generate` (default
  `./post-copy-config.json`). Missing → stop and ask.
- **Target org alias / username**: Never assume the default; if not
  supplied, list via `sf org list --json` and ask.
- **Dry-run flag** (default `false`): **reads ALLOWED, writes
  FORBIDDEN** — not "no network calls". Still run Step B describe
  GET, Step C SOQL, Step D-1 GET; the plan's would-be PATCH body is
  only accurate against the real Metadata block. Steps D-3 (PATCH)
  and E (verify) are skipped (Flows: see Step G — G-3 GET + PATCH
  both skip, G-1 + G-2 still run). On a read failure (401, 404,
  `NamedOrgNotFoundError`) surface and stop — never fall back to a
  from-memory plan. Prefer dry-run on the first pass.
- **Continue-on-error** (default `true`): true = failing entries
  don't abort the phase; false = abort mid-phase.

If the user supplies a clear config path and target alias, proceed
without further questions.

---

## Workflow

Every step executes real `sf` CLI commands via Bash. Never narrate the
plan without running the commands — this skill mutates the target org.

1. **Read + validate the config JSON** — load with the Read tool.
   Every entry needs the five top-level keys; malformed → hard stop.

2. **Resolve target org + API version** — `sf org display --json`.
   Parse to confirm alias resolves and capture `result.apiVersion`.
   Do not print the raw JSON — it contains the access token.

3. **Plan phases** — run `node scripts/plan-phases.mjs <config.json>`
   and iterate its `phases[]` output. See
   `references/execution_phasing.md` for the concurrency cap.

4. **Per-entry describe-verify** — for each distinct
   `ConfigurationName` ≠ `ScheduledApex`, run Step A + Step B once
   and cache the verified sobject. Step B failure → every entry with
   that name is `API_NOT_IDENTIFIED`. `ScheduledApex` skips
   describe-verify (Step F uses anonymous Apex, not compound
   Metadata). `Flows` DOES run describe-verify (PATCH transport is
   compound-Metadata on `FlowDefinition`); it skips only Step D's
   mutation-key derivation (Step G-3 uses a fixed key).

5. **Per-entry apply pass** — for each entry inside each phase:
   - `SKIP_INACTIVE` from plan-phases → `SKIPPED_INACTIVE` +
     Follow-ups bullet, continue.
   - `ScheduledApex` → Step F (F-1→F-4). Dry-run: F-1 + F-2 only;
     record `DRY_RUN`.
   - `Flows` → Step G (G-1→G-4). `ALREADY_ACTIVE` /
     `ALREADY_INACTIVE` pre-flight bypasses the PATCH. Dry-run:
     G-1 + G-2 only; record `DRY_RUN`.
   - All others → Step C (Id), Step D (GET+mutate+PATCH), Step E
     (verify). Dry-run: C + D-1/D-2 only; record `DRY_RUN`.

6. **Between phases** — wait for every entry in the current phase to
   complete before starting the next.

7. **Write the summary file** — Markdown at
   `./post-copy-<mode>-summary.md`, per the "Canonical output shape"
   section; also print to the user. Never write access tokens or raw
   `sf org display` output. Mask embedded URL credentials in the
   summary (`https://user:***@host/...`); the real PATCH body
   carries the verbatim URL.

---

## Rules and Gotchas

Load-bearing invariants (never insert; describe-gate every
`ConfigurationName`; compound `Metadata` PATCH preserves the full
existing block; `IsActive: false` → `SKIPPED_INACTIVE`; never print
raw access tokens; cap intra-phase concurrency at 5) and the
canonical response for each runtime failure (401 mid-run, 429,
credential-bearing URLs, `Fields.Action = "Delete"`, describe 404,
zero/many SOQL rows) live in `references/rules_gotchas.md`. Read
that file before deviating from the Step A–E procedure.

---

## Cross-Skill Integration

| Need | Delegate to |
|------|-------------|
| Turn a customer SOP into the JSON config this skill consumes | `automation-sandbox-post-copy-config-generate` |
| Deploy metadata XML outside the compound-Metadata Tooling pattern | Matching `generating-*` skill + a metadata deploy flow |
| Create new records that do not yet exist on the target org | `platform-metadata-deploy` |
| Assign permission sets required for the API calls | `dx-org-permission-set-assign` |

---

## Reference File Index

| File | When to read |
|------|-------------|
| `references/api_endpoints.md` | Steps A–E — full generic recipe + OBM/RSS worked examples |
| `references/scheduled_apex_path.md` | Step F — anonymous Apex route for `ScheduledApex` |
| `references/flow_activation_path.md` | Step G — flow activation / deactivation (`Flows`) |
| `references/execution_phasing.md` | Step 3 — phase-grouping model behind `plan-phases.mjs` |
| `references/authentication.md` | Step 2 — session check + 401 mid-run handling |
| `references/rules_gotchas.md` | Before deviating from Step A–E — invariants + failure responses |
| `scripts/plan-phases.mjs` | Step 3 — phase planner |
| `scripts/map-metadata-key.mjs` | Step D-2 — Metadata-key resolver |
| `scripts/classify-patch-result.mjs` | Step D-4 — HTTP-outcome classifier |
| `scripts/resolve-target-org.mjs` | Output shape — target-org alias resolver |
| `scripts/build-scheduled-apex.mjs` | Step F-2 — anonymous-Apex snippet builder |
| `scripts/soql-escape-job-name.mjs` | Step F-1/F-4 — SOQL-escape `JobName` |
| `assets/api_request_templates.json` | Steps A–E — describe/lookup/GET+PATCH template |
| `assets/scheduled_apex_template.apex` | Step F-2 — anonymous Apex template |
| `examples/sample_config_input.json` | Step 1 — config JSON shape |
| `examples/sample_scheduled_apex_config.json` | Step 1 — `ScheduledApex` entry shape |
| `examples/sample_execution_summary.md` | Step 7 — summary report shape |
