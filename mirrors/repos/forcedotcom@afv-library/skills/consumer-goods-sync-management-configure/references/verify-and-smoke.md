# Reference — Verify Steps & Smoke Tests

Background for [Act 3](act3-plan-verify.md) and for the `purpose: verify`
re-reads that every write step in Acts 1–2 should end with. These are the skill's verify
conventions — apply them consistently across every write step.

## End every write with an explicit verify step

- **Convention & template:** the standard verify-artifact format. A verify step
  is a distinct step with `id: verify`, a read `api`, and an `assert:` predicate:
  ```yaml
  - id: verify
    description: "Confirm the write took"
    api: "GET /query?q=SELECT COUNT() FROM <ns>Sync_Tracked_Object_Config__c"
    assert: "count == <expected for the installed baseline>"   # derived at runtime, never hardcoded
  ```
- **Pre-flight validate vs. post-write verify:** the skill also uses `purpose: validate`
  (pre-flight, e.g. "does this user exist" in A2.1) — that's the front of a step. `verify` is the
  back. Acts 1–2 writes should carry both: validate inputs before, assert results after.
- **The multi-object count verify is ONE batched call, not a loop.** The single-object `COUNT()`
  template above is fine for a lone row (the assignment write). But the **four-object A1.3 landing
  check and A3.1 count verify** must read every count in a **single anonymous-Apex call** that
  `System.debug`s a JSON blob — **never** a `sf data query` per object: each `sf` cold-start is
  ~15–20s, so a 4–5-object loop blows the 2-min timeout. And when parsing that call's output, **grep
  `USER_DEBUG` first** — `sf apex run` echoes the block as `Execute Anonymous:` source, so a bare
  marker grep matches the source too. Batched form + parse rule: transports cookbook form 6 in
  [transports-and-namespace.md](transports-and-namespace.md).
- **Read-back is the cheapest honesty mechanism.** For every `Sync Management App`/`core` write in this skill
  (config install, mapping row), the verify is a plain SOQL `COUNT()` or a targeted `SELECT` of
  the row just written. If the read-back doesn't match, report failure — never infer success from
  a 200/201 alone. (A2.2's IOU membership is a **read-only precondition**, not a write — its
  "verify" *is* the read itself: a matching `InternalOrgUnitUser` row proceeds; no row
  reports-and-stops under `Default_IOU`.)

## Write the run report to disk — the deliverable is a file, not the chat

Reporting in the conversation is **not** the deliverable. This is a long, multi-Act, org-mutating
run: a stream can truncate, a turn can end early, or the agent can simply conclude in chat — and if
nothing was written, the run leaves **no artifact at all**. So persist a `report.md` to the working
directory and **treat writing it as a first-class step, not an afterthought**:

- **Create it before the first org write.** The mandatory pre-write plan (SKILL.md) is the report's
  first section — write the file the moment the plan is formed, before enabling RE / installing /
  assigning. Use `write_file` (or an equivalent explicit file write); do not rely on shell echoes or
  on the chat transcript being captured.
- **Append as you go — one section per Act.** After each Act's end state, append what ran: the
  sub-steps executed, each step's **transport tag** (`core` / `Sync Management App`), the
  **read-back (`assert:`) result**, and any entries added to `blocked_steps` (step + boundary +
  who owns the missing piece). Incremental appends mean a partial or interrupted run still yields a
  faithful, scorable record of exactly how far it got.
- **Close with a single verdict.** End the file with the overall outcome: full setup reached
  (Act 3 end state) — or the exact step that blocked, why, and who provides the missing piece.
  A faithful report-and-stop is a complete deliverable; a silent chat-only summary is not.

The report mirrors the honesty spine already used throughout the skill — it just makes the record
durable. Keep it concise and factual; it is a run log, not a re-explanation of the skill.

## A1.4 field-set verify — compare on the bare name, case-insensitively

The A1.4 read-only describe (does each referenced field set exist per tracked object?) produces
false "missing" hits unless the comparison is both **case-insensitive** and **namespace-agnostic**:

- **`Schema.describeSObjects(...)[0].fieldSets.getMap()` keys are all-lowercase AND fully
  namespace-qualified** (`<ns>__name`). So `getMap().containsKey('RetailMobilityRelevant')` — the
  referenced name in its original case — returns **false even when the set exists** (the real key is
  e.g. `<ns>__retailmobilityrelevant`). Never `containsKey` the raw referenced name.
- **Whether the set is prefixed depends on the ORG, not the `$$NS` macro.** The
  `Fieldset_Name_List__c` / `List_Header_Fieldset__c` names use `$$NS`
  (`$$NSMobilityRelevant` → `<ns>__MobilityRelevant` at install). But `RetailMobilityRelevant`
  (no `$$NS`) is **not** always unprefixed: in a pure **subscriber** org RE provisions it as
  **standard** metadata (`NamespacePrefix` null), whereas in a **source-deployed / namespaced** org
  (the `Organization.NamespacePrefix` branch A1.1 handles) **every** set — including
  `RetailMobilityRelevant` — carries the **org namespace** (`FieldSet.getNamespace()` = `<ns>`).
- **Correct comparison: strip any `<prefix>__` from both sides and compare lowercased.** In Apex,
  build the present-set from `FieldSet.getName().toLowerCase()` (`getName()` is the bare local name;
  `getNamespace()` is the prefix, separately) — not from raw `getMap()` keys. In Tooling, compare
  `DeveloperName` case-insensitively and ignore `NamespacePrefix` (it varies by org).
- **Tooling `FROM FieldSet` requires an EntityDefinition filter** — `WHERE
  EntityDefinition.QualifiedApiName = '<obj>'`. An unfiltered `SELECT … FROM FieldSet` returns
  **zero rows**, which reads as "no field sets" and is a trap.

## A3.2 verification — record counts only (no device call, no new endpoint)

- **The method is a record-count check, full stop.** After install, compare the installed
  per-object row counts (from A3.1's `core` `COUNT()` reads) to the **installed baseline's own
  declared counts**. One pass / fail verdict per object. Act 3 issues **no** representative
  device-facing `/v1/*` call as part of verification, and proposes **no** new Sync Management App endpoint
  (`/v1/syncconfig/verify`) — the count comparison is the complete server-side check.
- **Derive the expected counts at runtime — never hardcode them.** The expected numbers vary by
  which baseline was installed. Identify the installed baseline from the activated config (the
  `staticResourceName`/version captured at install time in A1.3, carried in session state, or
  the installed `configId`/`version` read back in A3.1), then compare against the baseline's own
  declared counts — never a fixed set of numbers.

### How to get the expected counts — A3.2 is the per-object split; the aggregate was Act 1's landing check

- **The aggregate was already checked at install — Act 3 does not just repeat it.** At A1.3 the
  install ran the cheap **aggregate** landing check: sum of the four `core` COUNT() reads ==
  `InstallResponse.recordsInserted` (which equals the manifest's total row count), needing **no**
  static-resource fetch. `recordsInserted` + `version` were captured into session state there; reuse
  them, but do **not** treat re-running the aggregate as A3.2's verification — that would duplicate
  Act 1. A3.2's job, and its value over the landing check, is the **per-object split** below (it
  catches a right-total / wrong-distribution install the aggregate cannot).
- **Per-object split (A3.2's verification — the one thing that needs the manifest):** to verify each object's count
  individually (e.g. `Sync_Config__c` = 1, `Sync_Tracked_Object_Config__c` = 39,
  `Sync_Named_Fetch_Tree_Nodes__c` = 63, `Sync_Named_Query__c` = 77 — illustrative; read the real
  split from the installed baseline), you need the baseline's per-object row counts. **Retrieve the
  static resource in *source* format into an *in-project* scratch dir, then read `manifest.json`
  directly — do NOT `unzip`, and do NOT stream the Body over REST.** Two field-verified constraints
  drive the exact shape of this command:
  - **`--output-dir` must resolve to a path INSIDE the sfdx project root.** `sf project retrieve
    start --output-dir` rejects any dir outside the project with `OutputDirOutsideProjectError`, so
    `mktemp -d` (which returns `/var/folders/…`, outside the project) **always errors**. Walk up
    from the cwd to the dir containing `sfdx-project.json`, make the scratch dir *under* it, and
    `rm -rf` it when done.
  - **Source-format retrieve produces a folder, not a ZIP.** A retrieved static resource expands to
    `staticresources/<name>/{manifest.json, *.csv}` — there is **no `<name>.resource` ZIP**, so any
    `unzip` step can never run. `manifest.json` already carries the **per-object row count**, so read
    it straight — you don't even need to count CSV rows.
  ```bash
  # 1) find the sfdx project root — `retrieve --output-dir` MUST resolve to a path inside it
  ROOT="$PWD"; while [ "$ROOT" != "/" ] && [ ! -f "$ROOT/sfdx-project.json" ]; do ROOT="$(dirname "$ROOT")"; done
  WORK="$ROOT/.sync-verify-tmp"           # in-project scratch dir — NOT mktemp -d (that path is outside the project → error)
  trap 'rm -rf "$WORK"' EXIT              # ALWAYS clean up, even on early return / failure
  # 2) SOURCE-format retrieve (~45s here; the MDAPI --target-metadata-dir path hung >2min)
  sf project retrieve start --metadata "StaticResource:<baselineName>" \
    --target-org <org> --output-dir "$WORK"
  # 3) expands to staticresources/<baselineName>/manifest.json (+ *.csv) — no ZIP, no unzip.
  #    manifest.json carries the per-object row counts; read them straight from it.
  MANIFEST="$(find "$WORK" -path '*/staticresources/<baselineName>/manifest.json' | head -1)"
  # parse each object's declared count from "$MANIFEST" and compare to the A3.1 COUNT() reads
  ```
  **Don't fetch the ZIP over REST, and don't reach for the MDAPI path first:**
  - `sf api request rest .../StaticResource/<id>/Body` **UTF-8-corrupts the binary** (a 7,391-byte
    zip came back as ~12,918 bytes of mojibake) — never stream the Body.
  - The MDAPI/SOAP retrieve (`sf project retrieve start --target-metadata-dir <dir>`) *does* sidestep
    the in-project `--output-dir` constraint, but it **hung past 2 min** in the field, whereas the
    source-format `--output-dir` retrieve above finished in **~45s**. Prefer source format.
- **Clean up the download — always.** The retrieved `staticresources/<name>/` folder (`manifest.json`
  + CSVs) is a **throwaway verification artefact**, not project source. Because it must live *inside*
  the project root, delete it as soon as the counts are read — the `trap 'rm -rf "$WORK"' EXIT` above,
  or `rm -rf` before every early return. Never leave it behind in the workspace, never commit it, and
  add the scratch path to `.forceignore` so a stray run isn't picked up as source.
- **The hard boundary:** a green count check proves the **server side** installed the baseline's
  artefacts. Say exactly what was verified — report it as a server-side count check.

## When there is no programmatic path

- **When there's no programmatic path, it's a platform ask.** If a feature is UI-only with no
  API anywhere, name the team that owns it and move on — don't build around it.
- **Report genuine non-automatable capabilities to the admin, with the owner named.** For
  example, A1.2's advanced-RE pilot GA gate (`orgHasAdvncdRetailExecutionPilot`) has no API
  anywhere — a CG Cloud core / RE concern — so it's reported, not worked around. This is
  different from A2.2: the absence of a default mobility IOU is a report-and-stop
  **precondition**, not a missing capability (see below).

## Assignment write (A2.3) and the IOU precondition (A2.2)

- **A2.3's assignment write goes through the package endpoint, not a raw junction POST.** The
  user→config binding is written via `POST /v1/syncconfig/assignment`
  (`SyncConfigAssignmentEndpoint`), which derives the overloaded `Business_Area_Name__c`
  (IOU Id vs Business Area value) from the config's strategy and enforces dedup + the unique-Name
  convention — a raw `POST /sobjects/<ns>Sync_Client_App_Profile_Mapping__c` would silently corrupt
  the row. So the generic junction-write / sObject-REST playbooks are **not** the
  path for A2.3 — the endpoint is. Verify the write with a `GET /v1/syncconfig/assignment`
  read-back, as with any other write.
- **A2.2 is NOT a junction write — it is a `core` read-only precondition (Default_IOU only).**
  `InternalOrgUnitUser` is never written by this skill — it only **reads** the user's default
  mobility IOU (`SELECT InternalOrganizationUnitId FROM InternalOrgUnitUser WHERE UserId = :userId
  AND IsDfltMobIntrOrgUnit = true LIMIT 1`, mirroring `ClientAppMapperService.getDefaultIouId()`).
  A row → carry the `iouId` to A2.3; no row → **report and stop** (the user needs a default
  mobility IOU, a CG Cloud core / RE task done outside this flow); pure-MP org → `QueryException`
  → degrade to the MP path. Under `Custom_User_Field` the precondition does not apply — skip it.
  Creating IOU membership is out of scope; do **not** probe a raw `POST /sobjects/InternalOrgUnitUser`
  or report its absence as a missing capability — it is the report-and-stop precondition above.
