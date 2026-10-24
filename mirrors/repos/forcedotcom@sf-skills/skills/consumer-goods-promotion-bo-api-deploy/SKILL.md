---
name: consumer-goods-promotion-bo-api-deploy
description: "Use to enable the Consumer Goods Cloud TPM Promotion Business Object (BO) API framework in a Salesforce org, interview the user for the custom Workflow Step they want to add, generate and deploy that Apex class, wire it into the create/update/copy workflows, and prove it end-to-end via headless REST ingest. Ships a worked reference example (SetCommentValue) but the customization is user-supplied per org. Triggers on \"deploy the promotion BO API\", \"set up promotion BO API\", \"headless promotion create\", \"add a BO API workflow step\"."
metadata:
  version: "1.0"
  domains: ["Consumer Goods"]
  minApiVersion: "60.0"
  cliTools:
    - tool: ["jq"]
      semver: ">=1.6"
    - tool: ["node"]
      semver: ">=20.17.0"
    - tool: ["sf"]
      semver: ">=2.0.0"
  accessCheck: "License.CGCRetailAndTPMMgmtPsl"
---

# Deploy the Promotion BO API

## What this does

Turns on the Consumer Goods Cloud TPM Promotion Business Object (BO) API in a
Salesforce org, interviews the user for **one custom Workflow Step** to add to
the promotion pipeline, generates and deploys that Apex class, registers it
against a BO API entity, wires it into the customer's chosen subset of
`{create, update, copy}` workflows, then proves the whole path end-to-end via
three REST endpoints:

- `POST /services/apexrest/<prefix>/promotions/initialize`
- `POST /services/apexrest/<prefix>/promotions/ingest`
- `GET  /services/apexrest/<prefix>/promotions/status?importId=...`

It is meant for **headless delivery**: point it at an org, answer the interview, the skill installs and verifies the step. The Promotion BO API ships in the CGCloud **managed package** (`cgcloud` released, `cgcloud_dev` dev/beta). Every Apex identifier, object/field API name, and REST URL is derived from the detected package prefix at runtime.

`derive` is out of scope here (a follow-up skill covers it). Detailed runbooks
for the write and smoke phases live under `references/`:

- `references/preflight-and-seed-queries.md` — Phase 1/2/3 SOQL (TPM entitlement, permset gate, framework-state verification, static-resource retrieve recipe, batch-chain polling).
- `references/conventions-and-payload-rules.md` — sales-org partitioning, schema-first contract derivation, and the nine cross-workflow payload rules R1–R9.
- `references/generate-and-wire.md` — Phase 5a (generate + deploy the class) and Phase 5b (register + wire the step), with the full `register-step.apex`.
- `references/smoke-and-verify.md` — Phase 6 (contract derivation, payload materialization, create/update/copy legs + verification).
- `references/reference-example-set-comment-value.md` — the shipped `SetCommentValue` preset (assets at `assets/set-comment-value/`).

## Inputs to collect first

Ask before starting; do not guess.

1. **Org alias** — the `sf` alias of the target org. Required.
2. **Sales org** — required pre-parameter, default `0001`. Must be 4 chars, uppercase (mirrors `TPMSetupData.validateSalesOrg`). **Every** downstream lookup (promotion template, tactic template, anchor account, product filter criteria, SKUs) is scoped to this sales org — see `references/conventions-and-payload-rules.md` ("Sales-org partitioning").
3. **Yes to seeding?** — Phase 3a fetches the packaged BO API seed and asks for confirmation before inserting ~232 rows across 8 objects. Offer `--yes` for CI callers.
4. **Dry run?** — `--dry-run` runs Phases 1, 2, 3a-preview, the Phase 5 interview, and a validate-only deploy. Writes nothing.

What the customization *is* gets collected in Phase 5's interview, once the
framework state is known.

## Find the namespace first

The prefix depends on the installed build — detect it, do not guess. Released
package → `cgcloud`; dev/beta → `cgcloud_dev`; source-deployed → no prefix.

```bash
sf data query --target-org <alias> \
  --query "SELECT NamespacePrefix FROM ApexClass WHERE Name = 'TPMSetupData'" --json
```

Read `records[0].NamespacePrefix` and bind three variables used everywhere below:

- `PREFIX_DOT` — Apex references: `cgcloud.` / `cgcloud_dev.` / empty.
- `PREFIX_UNDER` — object/field API names: `cgcloud__` / `cgcloud_dev__` / empty.
- `URL_NS` — REST paths: `/cgcloud` / `/cgcloud_dev` / empty.

Every Apex call is `${PREFIX_DOT}ClassName.method(...)`; every SOQL object/field is
`${PREFIX_UNDER}Object__c`; every REST URL is
`/services/apexrest${URL_NS}/promotions/<endpoint>`. Substitute at run time.

## Phase 1 — Preflight

Run these and stop on the first failure.

1. `sf --version`; `node --version` (only if running shipped scripts). Also `export SF_SKIP_NEW_VERSION_CHECK=true` once at session start so a stale CLI's update banner cannot leak onto stdout and break any `sf … --json | jq …` pipe downstream (see `references/smoke-and-verify.md` "parse caveat" for the alternate `sed` strip).
2. `sf org display --target-org <alias> --json` — confirm reachable; capture `instanceUrl` + org id (display/logging only). REST calls use `sf api request rest` on the CLI's stored session — the skill never extracts the access token.
3. Validate sales org locally: length 4, uppercase, non-blank (mirrors `TPMSetupData.validateSalesOrg`). Fail fast.
4. **TPM entitlement (Permission Set License)** — the `CGCRetailAndTPMMgmtPsl` PSL assignment on the running user. SOQL + warn/stop routing in `references/preflight-and-seed-queries.md` Step 4.
5. **Running-user permission set (TPM Admin persona)** — the running user must hold `TPM_Master_Data_Admin` (or a clone matching `%TPM%Master Data Admin%`); if missing, offer `sf org assign permset --name TPM_Master_Data_Admin --target-org <alias>` and wait. SOQL in `references/preflight-and-seed-queries.md` Step 5. Proceed only once admin access is confirmed.
6. Namespace discovery (above).
7. **Running user's `${PREFIX_UNDER}Sales_Org__c` equals `<salesOrg>`.** Blank throws `SOU0003`; mismatch surfaces as "not found" (create/update) or `TransformationError` (copy). SOQL in `references/preflight-and-seed-queries.md` Step 7. Blank or `!= '<salesOrg>'` → stop; fix on the user record only. See `references/conventions-and-payload-rules.md` R6; category access is preflighted in Phase 6 per R9.

## Phase 2 — Verify BO API framework state

Read-only; tells you whether Phase 3 needs to run. Run the three
sales-org-scoped SOQL queries in `references/preflight-and-seed-queries.md`
("Phase 2 — Verify BO API framework state"): workflow rows, step row count,
junction row count — all scoped to `<salesOrg>`.

- Zero workflow rows → fresh for this sales org, Phase 3 will seed.
- Full state (4 workflow rows `create/update/copy/derive`; >0 step + junction rows) → Phase 3 is a no-op for this sales org (still run for idempotency; 3a shows zero net-new).
- Partial state → **error**; stop, report which rows are missing. A human inspects first.

## Phase 3a — Preview the default BO API seed (fetch + confirm)

The workflows/steps/junctions/entities/input-structures ship as CSVs inside the
packaged `TPMSetupData` static resource; `TPMSetupData.setupBOApi` reads and
upserts them. Before running it, show the user what will land.

1. Locate + retrieve the `TPMSetupData` static resource into a dedicated `setup-data/` subproject (keeps the read-only managed resource out of the Phase-5a deploy tree at `./.promotion-bo-api-deploy/force-app`), then confirm each target sObject exists. SOQL + the full retrieve recipe + 8-CSV manifest + describe loop are in `references/preflight-and-seed-queries.md` ("Phase 3a — Retrieve the packaged seed"). Any step failing → stop with the printed delta/error.
2. Show row counts per object (total ~232 rows across 8 objects; "upsert on `Unique_Key__c` — idempotent") + first 3 rows of `0_BO_API_Workflow__c.csv` and `0_BO_API_Workflow_Step__c.csv` with `{{NS}}`/`{{SALES_ORG}}` substituted.
3. Wait for confirmation unless `--yes`. "no"/blank → abort clean, point at the retrieved BOApi/ directory.
4. On `--dry-run` → stop here; do not run 3b.

## Phase 3b — Apply the default seed

Only after 3a confirmation.

1. `PHASE3_START=$(date -u +%FT%TZ)`.
2. Run metadata-wizard setup via anon Apex: `${PREFIX_DOT}TPMSetupData.setupMetadataWizard('<salesOrg>');` → `sf apex run --target-org <alias> --file ./.promotion-bo-api-deploy/setup-metadata-wizard.apex`.
3. Wait for the batch chain. `GenericDemoSetupDataBatch` self-chains via `finish()`, so poll by class with the two-consecutive-zero break pattern + run the final `NumberOfErrors`/`ExtendedStatus` check. SOQL in `references/preflight-and-seed-queries.md` ("Phase 3b — Poll the batch chain"). Any `Failed`/`Aborted`/`NumberOfErrors > 0` → stop.
4. Repeat 2–3 for `${PREFIX_DOT}TPMSetupData.setupBOApi('<salesOrg>');`.

## Phase 4 — Verify the BO API framework is on

Re-run the Phase 2 queries. Expect 4 `BO_API_Workflow__c` rows
(`create`/`update`/`copy`/`derive`, uniqueness on `Unique_Key__c`), ≥46
`BO_API_Workflow_Step__c` rows, ≥54 `BO_API_Workflow_Workflow_Step__c` junction
rows. Anything short → stop, print what's missing. Never claim success while a
component failed.

## Phase 5 — Interview: what does the user want to customize?

The framework is now on. The customization is **user-supplied** — do not skip
the interview or invent an answer. Print:

```text
The Promotion BO API framework is installed. To add a custom step, tell me:
  - Which BO API entity does it target? (e.g. Promotion/Tactic — I'll list registered entities)
  - Which workflows should it fire in? (create, update, copy)
  - What does it read from the ingest input?
  - What does it write on the SObject or elsewhere?
  - Any preconditions or side effects?
Say "use the SetCommentValue reference" for a worked example.
```

### 5.1 — Answers to collect

| Field | Required | Notes |
|---|---|---|
| `stepName` | yes | PascalCase Apex class name + BO API Workflow Step `Name`. Unique across `ApexClass`. |
| `entity` | yes | BO API entity `Name` — MUST match a row queried live from `${PREFIX_UNDER}BO_API_Entity__c` (shared, not sales-org-partitioned). Typical rows include `Promotion`, `Tactic`, `ProductFilter`, `ManualInputs`, `CustomState`. Query the org — don't assume a fixed list. |
| `workflows` | yes | Non-empty subset of `{create, update, copy}`. `derive` is out of scope. |
| `actionName` | yes | Symbolic action string the class receives in `call(String action, ...)`. Convention: lowerCamelCase of `stepName`. |
| `inputPaths` | yes (≥1) | JSON paths to read from `currentInput`, e.g. `["Comment"]`. |
| `inputPathType` | yes | JSON type of the input paths — `String`, `Array`, `Boolean`, `Number`, `Object`. Drives the `RecordType` on each SIS row; a wrong value causes `TransformationError: Expected <Type>` at ingest. Different types → run Phase 5b once per type group. |
| `inputPathRequired` | optional | Whether `inputPaths` must appear on the ingest payload. Defaults to `false`. Drives `BO_API_Step_Input_Structure__c.Required__c` (platform default is `true` — skill always writes explicitly). See `references/generate-and-wire.md`. |
| `outputWrites` | yes (≥1) | `{field, source}` pairs; `field` is the target API name **without** the namespace prefix (skill adds `${PREFIX_UNDER}`), `source` references an `inputPaths` value / literal / computed expression. |
| `description` | yes | One-sentence step description → `${PREFIX_UNDER}Description__c` + class docstring. |
| `preconditions` | optional | Free-text guards before writing. |
| `sortAfter` | optional | Named packaged step to sort after; default `max(Sort__c) + 10`. |

### 5.2 — Interview flow

1. **Preset shortcut.** `--preset set-comment-value` (or "use the SetCommentValue reference") loads answers from `references/reference-example-set-comment-value.md` (`assets/set-comment-value/interview-answers.json`) and skips the interactive interview. `--interview-file <path>` loads a JSON mirroring the 5.1 table (wins over `--preset`).
2. **Ask the questions** one at a time (or as a block); do not proceed until every required field has a value.
3. **Show the entity's writeable fields** after the user names the entity:
   ```bash
   sf sobject describe --target-org <alias> --sobject '${PREFIX_UNDER}<Entity>__c' --json \
     | jq -r '.fields[] | select(.updateable == true and .createable == true) | .name'
   ```
   Any `outputWrites` field must appear here; otherwise stop and ask for a different one (FLS is caller-scoped).
4. **Confirm the plan** (recap Class/Entity/Workflows/Reads/Writes/Sort/Description → "Deploy + wire? [y/N]"). If `workflows` includes `copy`, flag TWO copy-only preconditions up front so neither surfaces as a runtime surprise: (a) per-child input values come from the source promotion — `outputWrites` still fires but `<inputPaths>` values are ignored (only top-level fields like `Slogan` propagate); (b) the running `User.Sales_Org__c` MUST equal the source template's `Sales_Org__c` (preflighted in Phase 1 step 7 + re-checked before every Phase 6 ingest; a mid-flow drift fails `copy` with `TransformationError: The User and the Promotion Template must have the same Sales org` — fix on the user record, do not mutate mid-flow; see `references/conventions-and-payload-rules.md` R6). `n`/blank → save answers to `./.promotion-bo-api-deploy/interview.json` and exit. `y` → Phase 5a.

## Phases 5a / 5b — Generate + deploy, register + wire

Runbook in `references/generate-and-wire.md`. In short: guard the class name
for idempotency; confirm target-field writeability; clean any stale
`.cls`/`.cls-meta.xml` from
`./.promotion-bo-api-deploy/force-app/main/default/classes/` (leftovers cause a
silent MDAPI full-batch rollback); generate a namespace-agnostic `Callable`
from the interview — class **and** `call` method must be `global` (packaged
`CallableManager` resolves via `Type.forName` across the namespace boundary;
`public` fails at runtime on managed installs — see runbook); show + confirm;
`sf project deploy start`. Then, in one anon-Apex transaction, upsert one
`BO_API_Workflow_Step__c` (bare class name in `Classname__c`), one
`BO_API_Workflow_Workflow_Step__c` junction per chosen workflow (`derive`
dropped), and the `BO_API_Step_Input_Structure__c` rows (RecordType per
`inputPathType`, `Required__c` set explicitly from `inputPathRequired`). Both
upserts key on `Unique_Key__c` (idempotent).

## Phase 6 — Smoke test through the REST endpoints

Runbook in `references/smoke-and-verify.md`. Derive the payload contract per
invoked workflow from `BO_API_Step_Input_Structure__c` (schema-first), apply
rules R1–R9 from `references/conventions-and-payload-rules.md`, resolve every
reference in-sales-org, materialize `./out/smoke/{create,update,copy}.json`, then
run `initialize → ingest → poll status` for each chosen workflow. Verify via a
direct `BO_API_Transaction_Log__c` query (any row `!= 'Calculated'` → fail) plus
an `outputWrites` field assertion against `./out/smoke/expected.json`. Update and
copy legs run only if the interview included them.

## Phase 7 — Report

Short status: org, sales org, dry-run flag; namespace prefix; seed rows
before/after (Phases 2 & 4); interview summary; deploy result + workflow-step
id + junction ids; smoke import ids per invoked workflow — all `Calculated`
with matching assertions, or exactly which failed (SOQL, expected, actual);
manual follow-ups (`none` if clean).

## Rules

- Never claim success while any `BO_API_Transaction_Log__c` row for the smoke import ids has `Status__c != 'Calculated'`. `Calculated` is the terminal success state (R2); `Processed` does NOT exist in the picklist.
- Never claim success while any `outputWrites` assertion fails, or while any `GenericDemoSetupDataBatch` `AsyncApexJob` since the phase start is still running or failed.
- Stop on the first failed preflight or verify check; report the exact failure.
- Never hard-code the namespace prefix — compose every Apex/SOQL/REST reference from the Phase-1 detection.
- Never invent Apex method signatures — use what the packaged `TPMSetupData` / `BO_API_*` objects and the shipping REST endpoints declare.
- The seeded BO API metadata is packaged content — preview it and get user confirmation before invoking `TPMSetupData.setupBOApi`.
- Never invent an interview answer. Absent a user and `--preset`/`--interview-file`, stop and print the questions.
- Never wire a workflow the interview did not include. `create`/`update`/`copy` are opt-in; `derive` is always excluded.
- Never compose a smoke payload from a hard-coded template — derive accepted paths per workflow from `BO_API_Step_Input_Structure__c` and validate user input against that contract first.
- Never resolve a reference value without the sales-org filter. A record under a different sales org is not valid for this invocation.
- Never generate a `Callable` step class with `public` visibility — declare the class and the `call` method `global`. `public` works only on same-namespace dev orgs and fails on managed installs with `Type "<stepName>" does not exist`; the transaction log shows a generic `Error`. See `references/generate-and-wire.md`.
- Never re-use `./.promotion-bo-api-deploy/force-app/main/default/classes/` across step deploys — remove the prior step's `.cls`/`.cls-meta.xml` first. A stale file triggers a silent MDAPI full-batch rollback while the CLI still reports `"created": true`.
- Never insert a `BO_API_Step_Input_Structure__c` row without setting `Required__c` explicitly. The platform defaults it to `true`; the skill defaults `false` and only opts in when `inputPathRequired` is set. Omitting the field silently makes every optional path mandatory.
- Never proceed past Phase 1 without confirming the running user's `${PREFIX_UNDER}Sales_Org__c` equals `<salesOrg>` — blank throws `SOU0003`; mismatch surfaces as "not found" (create/update) or `TransformationError` (copy). Fix on the user record only. See `references/conventions-and-payload-rules.md` R6.
- Never ingest a payload whose `ProductFilter.Criteria.<level>` references categories the running user lacks `Product_Category_Share__c` `Access_Level__c='ReadWrite'` on — Phase 6 preflight per `references/conventions-and-payload-rules.md` R9. Do not silently insert share rows.
