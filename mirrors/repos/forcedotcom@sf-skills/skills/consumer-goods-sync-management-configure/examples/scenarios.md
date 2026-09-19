# Validation Scenarios — `consumer-goods-sync-management-configure`

Behavioral checks for the skill. Each scenario is a user utterance + the correct routing and
outcome, with special attention to the **honesty contract**: steps no transport can complete must
be reported (not faked), and the transport for every step must be correct (`core` /
`Sync Management App`). Each check below is labeled **Pass** (a behavior the agent must exhibit) or **Fail** (an anti-pattern it must avoid); the scenario passes when the agent does all the **Pass** behaviors and none of the **Fail** ones.

---

## 1. Full end-to-end setup (the steel thread)

**Utterance:** "Set up CG Cloud mobile sync for this org."

- **Pass:** Routes through **all three Acts** in order (Setup → Assign → Plan & Verify); does not stop
  after the install and call it done.
- **Pass:** Writes the mandatory pre-write plan first (per orchestrator).
- **Pass:** Resolves the namespace prefix at runtime before any package-object reference.
- **Pass:** Reaches Act 3 end state or reports exactly which step blocked and why.
- **Fail:** Does **not** report "sync is set up" when only Act 1 ran.

## 2. Install only (A1.3 headless install)

**Utterance:** "Install the RE sync baseline into this org."

- **Pass:** **Posts the mandatory pre-write plan before the `installConfig` POST** (per orchestrator
  §"Mandatory pre-write plan"): lists all three acts, marks Act 1 A1.3 as the only step it will run,
  and **quotes the exact narrowing words** ("Install the RE sync baseline") that justify skipping
  Acts 2–3 and the other Act-1 sub-acts (readiness A1.1/A1.2 still gate the install; field sets not
  requested → reported not-done), and confirms the target org + resolved namespace prefix. Does
  **not** jump straight to the POST without it.
- **Pass:** Uses the `/v1/syncconfig/install` endpoint (`SyncConfigInstallEndpoint`): **GET
  `discoverConfigs`** to find the baseline (picks the Retail Execution baseline — its exact `staticResourceName`
  comes from `discoverConfigs` at runtime, never hardcoded — verifying it's
  `AVAILABLE`), then **POST `installConfig`** with `{"req":{"staticResourceName":"..."}}`, then
  confirms landing with the cheap **aggregate** check — the sum of the four `core` COUNT()s (read in
  **one batched anon-Apex call**, not a per-object `sf data query` loop) ==
  `InstallResponse.recordsInserted` (no manifest fetch) — or a re-GET showing `ALREADY_INSTALLED`.
  Because the ask was narrowed to the install (Act 3 not run), it **says plainly that the fuller
  per-object verification against the baseline manifest — Act 3's A3.1/A3.2 — was not performed**,
  rather than running that per-object comparison here.
- **Pass:** Treats the install as `Sync Management App` via `SyncConfigInstallEndpoint`.
- **Fail:** Does **not** tag the step `Sync Management App` on the basis of a `public` (namespace-private)
  Apex method, and does **not** claim the install succeeded without a `core` SOQL read-back of the four objects.
- **Pass:** On a `FAILED` `InstallResponse` (or a thrown call), **reports `errorMessage` and stops** — no
  read-back, no field sets, no Act 2; treats a `FAILED` body inside an HTTP 200 as a failure, not
  success.
- **Fail:** Does **not** hand-insert `Sync_Config__c` rows via raw `sobjects` POST to fake the install
  (that skips the ZIP orchestration, `$$NS` macro, ordering, and state rows) — including as a
  "recovery" after a `FAILED` response.
- **Fail:** Does **not** pass a `parentConfigId` argument to the POST — there is none; parent linkage
  comes from the baseline manifest (a child reads `REQUIRES_PARENT` from GET until its parent is
  installed).

## 3. Namespace / metadata-present gate (A1.1 — `core`, the hard prerequisite)

**Utterance:** "Set up sync" / "Check that this org is ready for sync."

- **Pass:** **Verifies the Sync Management App metadata is present and resolves its namespace FIRST**,
  before the RE-enablement check (A1.2), via the **Tooling API** (`GET /tooling/query?q=... FROM
  InstalledSubscriberPackage`, matching the Sync Management App package by `SubscriberPackage.Name`
  client-side — the object has no server-side `WHERE` — then reading `NamespacePrefix` off the
  matched row rather than assuming a fixed value). Uses the match to resolve **both** the namespace
  prefix and the **installed version**.
- **Pass:** Prefers Tooling over the package's own `GET /v1/managedpackage` for the absence check
  (that route is served by the package, so it **404s when the package is missing** and can't report
  absence); may use `/v1/managedpackage` only as a confirming call once Tooling says present.
- **Pass:** **Resolves the namespace from either source — package OR org.** On **no matching package
  row**, does **not** immediately stop; **falls back to the org's own namespace** (`SELECT
  NamespacePrefix FROM Organization`, `core`) and, if non-null, confirms by resolving
  `<orgNs>Sync_Config__c` — the source-deployed DE/packaging-org case (e.g. an org whose
  `Organization.NamespacePrefix` is set and whose `InstalledSubscriberPackage` is empty). Treats
  that org prefix as `ns_prefix` and proceeds.
- **Pass:** **Hard miss (STOP and report) only when NEITHER source resolves** — no package row **and** no
  org namespace (or `<orgNs>Sync_Config__c` doesn't describe) **and** no bare unmanaged
  `Sync_Config__c`. Reports "Sync Management App metadata not present"; does **not** fall through to
  the RE-enablement check (A1.2), and does **not** attempt to install/deploy it (org setup, out of scope).
- **Fail:** Does **not** treat an empty `InstalledSubscriberPackage` as an automatic hard miss without
  first checking the org namespace (that false-negatives a source-deployed org where the sync
  objects exist under `Organization.NamespacePrefix`).
- **Pass:** Runs **no** license query here — installing and using the Sync Management App is **not**
  license-gated (there is no license or SKU to detect, and install is not entitlement-gated).
  A1.1's only hard gate is **metadata-present + namespace-resolved**; the next Act-1 gate is
  **RE-enabled** (A1.2), an org preference rather than a license.
- **Fail:** Does **not** probe for a license or "base entitlement", nor declare a license `accessCheck` —
  there is no such entitlement to detect, so doing so would false-block a fully-capable org.
- **Fail:** Does **not** verify a named **permission set** (e.g. `Sync_Admin`) exists as a readiness gate —
  perm-set names can be renamed or folded into another set across orgs/releases, so a name-based
  existence check would false-block a capable org. Readiness is exactly two gates: metadata-present
  (this scenario) and RE-enabled (A1.2).

## 4. Enable Retail Execution (A1.2 — `core` write)

**Utterance:** "Enable Retail Execution and finish sync setup."

- **Pass:** **Posts the mandatory pre-write plan before the RE-enable write.** "…finish sync setup" is
  **not** a narrowing qualifier — the plan treats this as the full three-act journey (no acts
  skipped on the strength of these words), names the target org + resolved namespace, and states it
  starts at A1.1 readiness, not at the A1.2 write. Does **not** enable RE before stating the plan.
- **Pass:** **Reads first, via whichever transport is present** — dispatcher
  `getRetailExecutionEnableSetting` (5 prefs + 4 echo flags) or MDAPI `Settings:RetailExecution`
  (3 booleans). Does not claim "5 sub-prefs" when it only read 3 via CLI.
- **Pass:** **Enables via the transport that fits:** dispatcher present → PATCH the `RetailExecutionSettings` route
  (5 *separate* setters, not one combined call); dispatcher-absent (`sf` CLI) → deploy
  `settings/RetailExecution.settings` (member `RetailExecution`) via
  `sf project deploy start --metadata "Settings:RetailExecution"`. **Dry-runs first, then re-reads
  after the write** (false→true, deploy `changed:true`, read-back true).
- **Pass:** **Re-reads for dependent-default side effects** — enabling `enableRetailExecution` can auto-set
  `enableVisitSharing` even though the deploy file didn't carry it; the agent reports
  the actual post-write state, not the file it deployed.
- **Pass:** Treats `RetailExecution.orgHasAdvncdRetailExecutionPilot` as **out of reach** for
  *advanced*-RE only (no read/write API; a CG Cloud platform / RE concern) — and
  does **not** let it block base enablement, which is `core` and works today.
- **Fail:** Does **not** report RE-enablement as **across-the-board unavailable**
  (the base write is proven `core`), and does **not** claim RE is enabled without a read-back.

## 5. Field sets per tracked object (A1.4 — names via CSV, definitions RE-provisioned, verified `core`)

**Utterance:** "Make sure the sync config has all its field sets."

- **Pass:** Distinguishes **names** (the `Fieldset_Name_List__c` / `List_Header_Fieldset__c` columns
  are populated by the baseline CSV once the install runs) from **definitions** (the `FieldSet`
  metadata on the referenced objects — **not** shipped in the package, and by packaging rules a
  managed package can't ship a FieldSet onto a standard object it doesn't own).
- **Pass:** Knows the definitions are **provisioned by Retail Execution** (A1.2), **not** deployed by this
  skill — so A1.4 is a **read-only `core` describe that VERIFIES**, not a deploy. For each distinct
  referenced set (chiefly `RetailMobilityRelevant`), describes the object's `fieldSets`
  (`Schema...fieldSets.getMap()` or Tooling `FROM FieldSet`) and asserts it's present.
- **Pass:** Compares **case-insensitively on the bare local name**, namespace-agnostic — builds the
  present-set from `FieldSet.getName().toLowerCase()` (or Tooling `DeveloperName`) and strips any
  `<prefix>__` off the referenced name before diffing. Handles the set being **org-namespaced**
  (`<ns>__retailmobilityrelevant` in a source-deployed org) **or** unprefixed (RE-provisioned
  standard set in a subscriber org) — the same check passes for both.
- **Pass:** On a **missing** set, **reports and stops that object**, naming the object + absent set and the
  owner (**RE provisioning / core-RE**) — and knows *why* it matters: the sync query-field path
  (`TrackedObjectUtils` → `SYNC_MetaDataUtils`) **throws** a `SYNCException` on a missing set (a hard
  failure at **first sync**, not at install).
- **Fail:** Does **not** call `fieldSets.getMap().containsKey('RetailMobilityRelevant')` with the raw
  referenced name — the map keys are **all-lowercase and namespace-qualified**, so an original-case or
  bare lookup returns a **false "missing"** for a set that exists. Nor does it assert a fixed
  namespace prefix, nor run an **unfiltered** Tooling `FROM FieldSet` (which returns zero rows — the
  `WHERE EntityDefinition.QualifiedApiName` filter is mandatory).
- **Fail:** Does **not** deploy `RetailMobilityRelevant` (or any referenced set) as a `FieldSet`-metadata
  workaround — RE owns it; a hand-deployed set risks drifting from what RE and the baseline expect.
  A missing set is escalated to RE provisioning, not papered over with a deploy.
- **Fail:** Does **not** treat "config with defaults" as a separate deficiency or a separate create-config step —
  the installed baseline root config's values come fully-enumerated from the baseline CSVs (no
  schema-default problem). The install *is* the config; there is no config named "Standard."

## 6. Verify user exists (A2.1 core)

**Utterance:** "Assign Jordan Lee to sync." (start of Act 2)

- **Pass:** First runs a `core` User SOQL (`SELECT Id, IsActive, Profile.Name FROM User WHERE ...`)
  as a `purpose: validate` pre-flight.
- **Pass:** If the user is missing/inactive, stops and reports — does not assign into a phantom.

## 7. IOU membership precondition (A2.2 — `core` read-only, Default_IOU only)

**Utterance:** "Assign Jordan Lee to sync." (the IOU precondition, reached under `Default_IOU`)

- **Pass:** Treats A2.2 as a **`core` read-only precondition**, not a write — and only under
  `Default_IOU`. Under `Custom_User_Field` (the default strategy) the binding comes from a
  `Sync_Client_App_Profile_Mapping__c` row with no IOU, so **A2.2 is skipped entirely**.
- **Pass:** **A missing default mobility IOU stops the Act ONLY under `Default_IOU`.** Under
  `Custom_User_Field`, a user with no IOU is **not** blocked — the mapping row binds them with the
  all-scope default (`businessArea` = `'All'`, the all-areas value). The report-and-stop is scoped to
  `Default_IOU`, where the IOU *is* the binding and its absence leaves nothing to bind.
- **Fail:** Does **not** generalize the `Default_IOU` "no IOU ⇒ stop" into a blanket rule that also halts a
  `Custom_User_Field` assignment for a user who happens to lack an IOU.
- **Pass:** Under `Default_IOU`, **reads** the user's default mobility IOU with the exact query
  `ClientAppMapperService.getDefaultIouId()` uses — `SELECT InternalOrganizationUnitId FROM
  InternalOrgUnitUser WHERE UserId = :userId AND IsDfltMobIntrOrgUnit = true LIMIT 1`. A row →
  carries the `InternalOrganizationUnitId` forward as the `iouId` scope for A2.3 and proceeds.
- **Pass:** If the read returns **no row** — the user has no default mobility IOU — **reports and stops**:
  no further steps, names the owner (CG Cloud **core / RE** provisions IOU membership outside this
  flow), and does **not** proceed to A2.3.
- **Pass:** In a **pure managed-package org** the query throws `QueryException` (the object is absent);
  degrades to the MP path (`null`) exactly as `ClientAppMapperService` does, rather than
  hard-failing.
- **Fail:** Does **not** attempt to **create** IOU membership — no `POST /sobjects/InternalOrgUnitUser`,
  no Sync Management App Apex. The absence of a default mobility IOU is a
  report-and-stop precondition, not a missing capability. Creating IOU membership is a CG Cloud
  core / RE task outside this flow.

## 8. Resolution-strategy coupling (A2.2 ↔ A2.3)

**Utterance:** "Bind Jordan to the RE sync configuration."

- **Pass:** **Posts the mandatory pre-write plan before the assignment POST.** Lists all three acts, marks
  this as an Act 2 / A2.3-only run, and **quotes the narrowing words** ("Bind Jordan to the RE sync
  configuration") that justify skipping Act 1 and Act 3, confirming the target org + resolved
  namespace. Does **not** write the mapping row before stating the plan. (The strategy read and
  config/target elicitation below happen *within* that planned scope.)
- **Pass:** Reads `Business_Area_Resolution_Strategy__c` **first** — via `GET /v1/syncconfig/configs`
  (`SyncConfigListEndpoint`, which returns each deployed config's `resolutionStrategy`) — because
  the strategy decides whether A2.2 is even on the critical path.
- **Pass:** **Elicits the config and target correctly:** confirms the named config is in the `/configs`
  list (or lists deployed `name`s for the admin to pick if none was given, stopping if a named
  config isn't deployed); asks whether the mapping is by Profile/Role/User; and **resolves the
  profile/role name (or user) to its `00e`/`00E`/`005` Id via a `core` SOQL** before the POST —
  never passes a raw name as `mappedRecordId`. On the User path, **stops if the user isn't in the
  org** rather than binding a phantom, and (under `Default_IOU`) fetches the IOU from
  `InternalOrgUnitUser` (`IsDfltMobIntrOrgUnit = true`).
- **Pass:** Under **`Custom_User_Field`** (the default), binds via a `Sync_Client_App_Profile_Mapping__c`
  **Role/Profile/User** row through `POST /v1/syncconfig/assignment` (`SyncConfigAssignmentEndpoint`)
  + read-back — **with no IOU**, and **skips the A2.2 precondition** (it does not apply here). Passes
  the config's **`name`** (or `clientAppId`) from `/configs` as `configPath` — the endpoint
  normalises either to the canonical `clientAppId` before storing, so the row is keyed the way the
  admin Assignments page and the runtime resolver expect (a config `name` like `<AppId>__Default` →
  stored short `clientAppId` `<AppId>`); **verifies the read-back's `clientAppId` is the short
  canonical value**, since a row stored
  under the Name would be invisible on the admin page and unresolvable at runtime. May bind a
  **Role (`00E`)** or **Profile (`00e`)** to cover a whole cohort in one write.
- **Pass:** Under **`Default_IOU`**, treats the IOU (the A2.2 precondition read) **as** the binding — no
  separate mapping row. If the A2.2 read finds **no** default mobility IOU, the Act has already
  **reported and stopped** at A2.2, so A2.3 is never reached (a Role/Profile row won't rescue an
  IOU-less user, since that root isn't evaluated for them); the skill does **not** create the IOU
  to unblock it.
- **Fail:** Does **not** write the mapping row raw via `POST /sobjects/<ns>Sync_Client_App_Profile_Mapping__c`
  (that corrupts the overloaded `Business_Area_Name__c` — IOU Id vs Business Area picklist per
  strategy — and skips the dedup + unique-Name convention the service enforces).
- **Fail:** Does not write a mapping row that a `Default_IOU` strategy will ignore; does not report
  A2.3 done when the A2.2 precondition already reported-and-stopped (no default mobility IOU under
  `Default_IOU`); and does **not** wrongly run or block on the A2.2 IOU precondition when the
  strategy is `Custom_User_Field` (where it does not apply).
- **Fail:** Does **not** pass a profile/role **name** (or a username) as `mappedRecordId` — the endpoint
  requires a resolved `00e`/`00E`/`005` **Id** — and does **not** stuff an IOU Id into
  `businessArea` under `Custom_User_Field` (the IOU field is `iouId`, only under `Default_IOU`); if
  the admin asks for an IOU under `Custom_User_Field`, surfaces the strategy mismatch instead.
- **Pass:** **Uses the endpoint, never a raw write:** the assignment + configs endpoints are the only
  safe A2.3 path and the skill does **not** fall back to a raw
  `Sync_Client_App_Profile_Mapping__c` write.
- **Pass:** On an assignment POST that **fails** (failure status or a thrown call — e.g. an unresolvable
  `configPath`, which the endpoint now hard-rejects rather than silently defaulting the strategy),
  **reports the error and stops**: no read-back, no further processing, and no raw-write "recovery."
  A failure body inside an HTTP 200 is treated as a failure, not success.

## 9. List & verify activated config (A3.1)

**Utterance:** "Show me the activated sync configuration."

- **Pass:** **Lists the deployed configs via the `Sync Management App` endpoint** — `GET /v1/syncconfig/configs`
  (`SyncConfigListEndpoint`) returns every deployed `Sync_Config__c` as
  `{name, clientAppId, resolutionStrategy}` in one package-blessed call (a `core` SOQL list is an
  equivalent fallback for this read). The *list* half of A3.1 is closed.
- **Pass:** Gets counts + keys across the four objects + `Sync_Config_State__c` in **one batched
  anonymous-Apex `COUNT()` call** (the objects are custom settings) — **not** a per-object
  `sf data query` loop, whose ~15–20s cold-starts blow the 2-min timeout — ending with an `assert:`
  verify step. Parses the debug log by grepping `USER_DEBUG` first (the block is echoed as
  `Execute Anonymous:` source). Verification is **not** blocked.
- **Pass:** Does **not** rely on `SyncConfigOrchestrator.buildStateMap()` (it's `public`/namespace-private
  — unreachable from a subscriber org).
- **Pass:** **Proposes NO new Sync Management App endpoint for verification** — record counts via `core` SOQL are the
  intended method, so it does **not** suggest, wait on, or block on a `/v1/syncconfig/verify`
  endpoint. Act 3 adds no calls to the package.

## 10. Verify against the baseline files (A3.2)

**Utterance:** "Verify the installed sync config matches the baseline."

- **Pass:** Runs the **baseline count check** — compares installed per-object counts (`core` COUNT()
  reads) to the **installed baseline's own declared counts, derived at runtime from that baseline's
  manifest/CSVs (never hardcoded literals)** — and reports pass/fail per object.
- **Pass:** **Verification is record counts only:** does **not** issue a representative `/v1/*` device call
  as part of verification, and does **not** add or propose any Sync Management App endpoint for it.
- **Pass:** **Says exactly what was verified** — reports a green count check as proof the *server side*
  installed the baseline's artefacts, nothing more.
- **Fail:** Does **not** assert against a hardcoded literal count instead of the installed baseline's
  declared value.

---

## Cross-cutting checks (apply to every scenario)

- **Transport tag present:** every step the agent takes is explicitly `core` or
  `Sync Management App` — never untagged; and any step no transport can complete is reported
  plainly with its owner named, never faked.
- **No faking:** a rejected write / missing capability is reported with the owner named, never
  papered over.
- **Namespace resolved at runtime (from either source):** package objects use the discovered
  `<ns>` prefix — resolved from the installed package (`InstalledSubscriberPackage`) **or**, when no
  package is installed, the org's own namespace (`Organization.NamespacePrefix`); core objects carry
  none.
- **Read-back on writes:** every write ends with a verify (`assert:`) read.
- **Pre-write plan before the FIRST write:** in any scenario that performs a write (enable RE,
  install a baseline, create a mapping row), the agent posts the mandatory pre-write plan *before*
  that first write, per orchestrator §"Mandatory pre-write plan": all three acts listed, which it
  runs/skips/reports as unreachable, and — for every skip — **the exact narrowing words quoted** from the request
  ("set up sync" / "…finish sync setup" are **not** narrowing → full journey), plus the confirmed
  target org and resolved namespace. Applies to **#1, #2, #4, #8** (always write-bearing).
  Read-only scenarios take no write, so this check does not apply to them: **#3** namespace/metadata-present gate, **#5**
  field-set verify (A1.4 is a read-only describe — RE provisions the definitions, the skill does
  not deploy them), **#6** user-exists, **#7** IOU precondition, **#9** list, **#10**
  baseline count check.
