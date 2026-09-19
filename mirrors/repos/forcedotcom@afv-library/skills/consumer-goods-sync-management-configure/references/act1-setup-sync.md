# Act 1 of 3 — Setup Sync

Part of the [`consumer-goods-sync-management-configure`](../SKILL.md) skill — the **first of three acts**.
Runs first; nothing in Acts 2–3 should be attempted until this Act's end state is reached.
After it, continue to [Act 2](act2-assign-users.md) → [Act 3](act3-plan-verify.md).

**This Act both gates and writes.** It *validates* things external to the package (the sync
metadata is present and its namespace resolves — from a package install **or** the org's own
namespace — and Retail Execution enablement — you can only check these, and a hard miss on either
halts the run),
and it *performs writes* (install the admin-confirmed baseline; field-set definitions are
provisioned by RE, so A1.4 only verifies them — no field-set deploy).
Having only *validated readiness* does **not**
mean Act 1 is done — you must complete the install + configuration writes and reach the end
state below.

**Read the transport contract first.** Every step here is `core` or `Sync Management App` (see the
parent `SKILL.md` and `transports-and-namespace.md`). Where neither transport
can complete a step, report what's needed and who provides it, then stop that step — never fake
it. The exceptions that **halt** the run are the hard readiness misses in steps 1–2: the sync
metadata absent (A1.1's gate — **neither** a managed-package install **nor** an org-namespaced/
unmanaged deploy resolves), or RE cannot be enabled and isn't already on (A1.2).

## What this Act does

### 1. A1.1 — Verify the Sync metadata is present and resolve its namespace (hard gate) — `core`

- **FIRST — verify the Sync Management App metadata is present in the org and resolve its
  namespace. This is the hard prerequisite for the entire skill** — without the sync objects no
  endpoint or namespace exists, so every downstream step is meaningless. The namespace has **two
  possible sources** (see below): a **managed-package install** (`InstalledSubscriberPackage`) or
  the **org's own registered namespace** (`Organization.NamespacePrefix`, for source-deployed
  DE/packaging orgs). Start with the package check via the **Tooling API** (generic `core`, no
  package code — so it answers even when the package is *absent*, which the package's own
  `GET /v1/managedpackage` cannot, since that route 404s when the package isn't installed):
  ```text
  GET /services/data/vXX.0/tooling/query?q=
      SELECT SubscriberPackage.Name, SubscriberPackage.NamespacePrefix,
             SubscriberPackageVersion.MajorVersion, SubscriberPackageVersion.MinorVersion,
             SubscriberPackageVersion.IsBeta
      FROM InstalledSubscriberPackage
  ```
  `InstalledSubscriberPackage` does not support server-side `WHERE` filtering, so **query all rows
  and match client-side** by `SubscriberPackage.Name` (the Sync Management App package), then
  **read the matched row's `NamespacePrefix` off the result** rather than assuming a fixed value —
  the org's installed package carries whichever prefix it was built with; that value (with a
  trailing `__` appended) becomes `ns_prefix`. Transport: `sf data query --use-tooling-api`
  when the CLI is present, else a plain REST `GET /services/data/vXX.0/tooling/query?q=<url-encoded SOQL>`
  via `execute_api` / any session-token client — the CLI is only sugar over this.
  - **A matched row confirms the package is installed** — and its `SubscriberPackageVersion`
    resolves **two** things at once: (a) the namespace prefix to use for every later
    package-object reference, and (b) the **installed version**, which you compare against the
    release that carries the `/v1/syncconfig/*` endpoints (A1.3 install, A2.3 assignment,
    A3.1-list) — an org on an older version won't have those routes even though the package is present.
  - **The namespace can come from two sources — package OR org.** A match above is the
    **package-install** case (a subscriber org). But the sync metadata can also be **source-deployed
    into the org under the org's *own* registered namespace** (a DE / packaging / dev org), where
    `InstalledSubscriberPackage` returns **no row at all** even though the objects are present. So an
    empty `InstalledSubscriberPackage` is **not** an automatic hard miss.
  - **No matched row → do NOT stop; fall back to the org namespace.** Read the org's own prefix
    with a generic `core` query — `SELECT NamespacePrefix FROM Organization` — and if it is
    non-null, treat that value (with the trailing `__`) as `ns_prefix`. **Confirm** by resolving one
    known object under it (`GET /sobjects/<orgNs>Sync_Config__c/describe`, or `SELECT COUNT() FROM
    <orgNs>Sync_Config__c`): a 200/successful describe means the sync objects live under the org
    namespace and the run proceeds. (There is no `SubscriberPackageVersion` in this case — version
    gating for the `/v1/syncconfig/*` endpoints doesn't apply to a source-deployed org; those
    classes are either deployed or not, verified by probing the route.)
  - **Hard miss = STOP only when NEITHER resolves.** If no `InstalledSubscriberPackage` row matches
    **and** the org has no namespace (or `<orgNs>Sync_Config__c` doesn't describe) **and** the
    object isn't present unmanaged (bare `Sync_Config__c`), then report "the Sync Management App
    metadata is not present in this org (no managed package, no org-namespaced deploy)" and halt the
    whole run — installing/deploying it is an org-setup prerequisite **outside this skill's scope**.
    Do not fall through to the RE-enablement check (A1.2); it presupposes the sync objects exist.
  - **Describe fallback (no Tooling access):** attempt `GET /sobjects/<ns>Sync_Config__c/describe`
    across the candidate prefixes — the package's known namespace(s) **and** the org namespace from
    `SELECT NamespacePrefix FROM Organization` (a `core` query, no Tooling), plus the bare
    (unmanaged) name — a 200 confirms that prefix is the live one (but yields no version); a
    `NOT_FOUND` = that prefix absent. `NOT_FOUND` on all probed = the metadata is absent. Prefer the
    Tooling query when available — only it returns the installed *version* for the package case.
- **No license read — installing and using the Sync Management App is not license-gated.**
  There is no license or SKU to detect, and package install is not entitlement-gated. So A1.1 does
  **not** run any license query and declares no license `accessCheck`: the Act-1 readiness gates are
  **metadata-present** (the namespace gate above) and **RE-enabled** (A1.2 below). Retail Execution
  is an org *preference*, not a license — enable it in A1.2 rather than probing for an entitlement
  here.
- **Do NOT verify the existence of any named permission set as a readiness gate.** Permission-set
  names are unstable — they can be renamed or folded into another set with a different name across
  releases and orgs — so a name-based existence check false-blocks a perfectly capable org. The
  **only** two Act-1 prechecks are (1) the **Sync Management objects are present** (A1.1 above) and
  (2) **Retail Execution is enabled** (A1.2 below). Access to the install/assignment endpoints is
  granted by *some* permission set in the target org (its name is the admin's concern, not a fixed
  value the skill asserts); if a call is denied for lack of access, report the access boundary and
  who grants it — never gate readiness on a specific permission-set name.

### 2. A1.2 — Enable Retail Execution — `core` read + `core` write

- **Read** the current setting one of two ways — **the transport determines what you see:**
  - **Headless-360 dispatcher present:** GET the CG Cloud core
    `RetailExecutionSettings` node (`getRetailExecutionEnableSetting`) — returns **5 prefs**
    (`isRetailExecutionEnablePrefEnable`, `isProductHierarchyPrefEnabled`,
    `isVisitSharingPrefEnabled`, `isCGAgentsPrefEnabled`, `isCGGenAIPrefEnabled`) + 4 read-only
    echo flags.
  - **Dispatcher-absent (e.g. `sf` CLI):** retrieve `Settings:RetailExecution` via MDAPI
    (`sf project retrieve start --metadata "Settings:RetailExecution"`). The Settings surface
    exposes **3** booleans — `enableRetailExecution`, `enableProductHierarchy`,
    `enableVisitSharing` — **not** the dispatcher's 5. Same underlying org pref
    (`ORG_PREFERENCE_RETAIL_EXECUTION_ENABLED` via `PermAndPrefUtil.setOrgPref`, controller
    `RetailExecutionEnableController`), different projection. If already enabled, record and move on.
  - **CLI absent → plain REST via the Tooling API (no dispatcher needed):**
    `RetailExecutionSettings` is a queryable Tooling *singleton* sObject. **Prefer the SOQL
    projection — one call, returns the values directly:**
    `GET /services/data/vXX.0/tooling/query?q=SELECT+IsRetailExecutionEnabled,IsProductHierarchyEnabled,IsVisitSharingEnabled+FROM+RetailExecutionSettings`.
    It returns the fields under **Tooling names** — `IsRetailExecutionEnabled`,
    `IsProductHierarchyEnabled`, `IsVisitSharingEnabled` (note: `Is…Enabled`, distinct again from
    both the dispatcher's `is…PrefEnable(d)` and MDAPI's `enable…`). **Avoid the two-call
    singleton GET** (`SELECT Id …` → `GET /tooling/sobjects/RetailExecutionSettings/<id>`) as the
    primary read — the per-id `sobjects` fetch can return `UNKNOWN_EXCEPTION`; keep it only as a
    fallback. This is the read to use when neither the `sf` CLI nor the Headless-360 dispatcher is
    present.
- **Enabling it is `core` and works today** on both transports below:
  - **Dispatcher present:** PATCH the `RetailExecutionSettings` route
    `.../retail-execution-settings/set-retail-execution-enable-setting` with `{enable:true}`.
    There are **5 separate PATCH setters, not one combined call** — `set-retail-execution-enable-setting`,
    `set-product-hierarchy-pref`, `set-visit-sharing-pref`, `set-cgagent-pref`, `set-cgcgen-aipref`,
    each body `{enable:boolean}`. Guards: all need View Setup & Configuration;
    `set-visit-sharing-pref` needs the Visit Share Pilot perm on `enable=true`; the two
    CG-agent/GenAI setters are gated by `RetailExecution.userCanUseCGGenAI`.
  - **Dispatcher-absent (`sf` CLI):** deploy a
    `settings/RetailExecution.settings-meta.xml` (source) / `settings/RetailExecution.settings`
    (MDAPI) whose member is named **`RetailExecution`** (the bare setting-type name — *not*
    `RetailExecutionSettings.*`) carrying
    `<enableRetailExecution>true</enableRetailExecution>`, then
    `sf project deploy start --metadata "Settings:RetailExecution"`. This is a generic **`core`**
    Metadata-API Settings deploy. Always dry-run first (`--dry-run`), then
    re-read after the real write to confirm the value took.
  - **CLI absent → plain REST via the Metadata deploy resource** (this is exactly what
    `sf project deploy start` wraps): `POST /services/data/vXX.0/metadata/deployRequest` with a
    base64-encoded zip (`package.xml` selecting `Settings:RetailExecution` +
    `settings/RetailExecution.settings`) and `{"deployOptions":{"checkOnly":true}}` to dry-run,
    then poll `GET /services/data/vXX.0/metadata/deployRequest/<id>` to completion; repeat with
    `checkOnly:false` for the real write.
    **Do NOT try a direct Tooling field PATCH** —
    `PATCH /tooling/sobjects/RetailExecutionSettings/<id>` with `{"IsRetailExecutionEnabled":true}`
    is **rejected** (`METADATA_FIELD_UPDATE_ERROR: Could not find a name resolver for Metadata`).
    Settings sObjects are read-only to a direct Tooling PATCH; the write must go
    through the Metadata deploy resource (or the dispatcher's PATCH setter). So: read is a clean
    Tooling GET, but write is *always* the metadata-deploy path.
- **Dependent-default side effect:** enabling `enableRetailExecution` also enables
  `enableVisitSharing` as a dependent default (if it was absent/off before) — the platform applies
  dependent sub-pref defaults on enable, even though the deploy file carried only the one field.
  **Re-read after the write; don't assume the sub-prefs match exactly what you deployed.**
- **A narrow exception: the advanced-pilot GA gate.**
  `RetailExecution.orgHasAdvncdRetailExecutionPilot` has **no read/write API surface**
  — it is a Core-source admission-gate expression on the setup tree, not an OrgPreference/PSL row.
  But **base RE enablement does *not* require it** — RE enables cleanly without touching it; it
  gates only *advanced* RE. When an advanced-RE feature needs it, report that it has no
  automatable read/write path and that it's owned by the CG Cloud platform / Core setup tree, then
  stop that step — do **not** let it block the base toggle, which is `core` and works today.
- **On a hard miss** (RE cannot be enabled and isn't already on): halt — like A1.1, an install
  into a non-RE org produces a config that can't sync.

### 3. A1.3 — Install sync artefacts into the four objects — `Sync Management App`

- **A headless install endpoint exists for this step.**
  `SyncConfigInstallEndpoint` is a `global @RestResource(urlMapping='/v1/syncconfig/install/*')`
  wrapper over the existing `SyncConfigInstall.installBaseline(...)` logic. It exposes:
  - **POST `installConfig`** — install a baseline. Body `{"req":{"staticResourceName":"..."}}` →
    `InstallResponse` (`status` SUCCESS/FAILED, `configId`, `version`, `recordsInserted`,
    `errorMessage`). **The only argument is `staticResourceName`** — see the discovery step for how
    to obtain a valid one.
  - **GET `discoverConfigs`** — list installable baselines *before* POSTing, so you don't guess the
    resource name. Returns `ConfigOption`s: `configId`, `displayName`, `parentConfigId`,
    `staticResourceName` (the value to POST), `availability` (`AVAILABLE` / `ALREADY_INSTALLED` /
    `REQUIRES_PARENT`), and `requiresLabel` (the blocking parent's configId when
    `REQUIRES_PARENT`). Read-only.
  - **On failure, report and STOP.** If the POST returns `status == FAILED` (or the call throws),
    surface `errorMessage` to the admin and **halt this step — no verify, no field sets, no Act 2.**
    A `FAILED` body inside an HTTP 200 is still a failure; never read it as success and never fall
    back to a raw sObject insert to "recover." Only a `SUCCESS` response proceeds to the verify below.
  - **Flow:** GET to discover → present the `AVAILABLE` baselines and **get the admin's explicit
    confirmation of which one to install** (see the confirmation gate below) → POST the confirmed
    baseline's `staticResourceName` to install → on `FAILED`, report `errorMessage` and stop → on
    `SUCCESS`, **confirm the install landed — the cheap *aggregate* landing check only.** This is a
    lightweight post-write gate, **not** Act 3's verification; do **not** run the per-object /
    baseline-manifest comparison here (that is A3.1/A3.2's job — running it in Act 1 just re-does Act
    3 a step early). Two reads, not one: a re-GET showing `ALREADY_INSTALLED` is a quick confirmation
    that the state row was written, but it does **not** prove the artefacts landed. The landing check
    is a single **aggregate** read-back: sum the four `core` COUNT()s (`Sync_Config__c`,
    `Sync_Tracked_Object_Config__c`, `Sync_Named_Fetch_Tree_Nodes__c`, `Sync_Named_Query__c`) and
    compare that sum to **`InstallResponse.recordsInserted`** — which equals the manifest's total row
    count, so this needs **no** static-resource fetch and **no** manifest at all. **Read the four
    counts with ONE batched anonymous-Apex call — do NOT loop `sf data query` per object** (each `sf`
    cold-start is ~15–20s, so a per-object loop blows the 2-min timeout; and when you parse the
    `sf apex run` output, **grep `USER_DEBUG` first** — the block is echoed as `Execute Anonymous:`
    source, so a bare marker grep matches twice; see the batched form in
    [transports-and-namespace.md](transports-and-namespace.md)). Capture
    `recordsInserted` + `version` from the `InstallResponse` into session state for Act 3 to reuse.
    **Run this aggregate landing check even for a narrow install-only ask** (where Act 3 may not
    otherwise run), so an install is never reported successful on a bare `SUCCESS`/state-row flip
    without confirming the rows inserted — and if the caller needs the per-object split for an
    install-only ask, say plainly that the fuller Act-3 verification (per-object counts vs the
    baseline manifest) was not run.
  - **Confirmation gate (mandatory, skill-side).** The install is a write, so **never POST without
    the admin's explicit OK.** Before installing, present what will be written: the chosen baseline
    (there is **no** config named "Standard" — the installable baselines are **discovered at runtime
    via `discoverConfigs`, never hardcoded**; Act 1 targets the **Retail Execution** baseline, whose
    exact `staticResourceName` comes from `discoverConfigs`), its per-object counts (read from the
    selected baseline's own manifest/CSVs at runtime — **never hardcoded**), and any additional
    sub-configs the admin also wants. Install only the confirmed set. **Sub-configs are just more
    baselines** installed through the same POST, each behind its own confirmation; parent-before-child
    ordering is enforced by the manifest's `parentConfigId` (a child shows `REQUIRES_PARENT` until its
    parent is installed) — not by a caller-supplied param.
- **Verify by re-GET after install** (GET → POST install of the discovered Retail Execution baseline → SUCCESS;
  re-GET shows `ALREADY_INSTALLED`). The endpoint's package-release rollout is a separate
  workstream from this skill.
- **What the logic does:** reads the discovered baseline's static-resource ZIP
  (`manifest.json` + CSVs) and inserts rows into all four objects: `Sync_Config__c`,
  `Sync_Tracked_Object_Config__c`, `Sync_Named_Fetch_Tree_Nodes__c`, `Sync_Named_Query__c`
  (namespace-agnostic via `SYNC_NamespaceHandler`; `$$NS` macro rewritten at install; per-config
  `Sync_Config_State__c` version rows written). Guards: blocks a duplicate `configId`, blocks a
  missing parent — **the parent linkage (`parentConfigId`) is read from the ZIP's `manifest.json`,
  not passed as a param**; a re-run is a no-op.
- **Do not hand-roll the install.** Do **not** substitute generic `core` sObject REST for the
  endpoint: the baseline install is an *orchestration* (unzip → macro → ordered multi-object
  insert → state bookkeeping) that hand-inserting rows via `POST /sobjects/<ns>...` would not
  reproduce faithfully (it skips the state rows and ordering guarantees). Use the endpoint, or have
  an admin run it via the VF page in a non-headless context.
- **The installed root config carries its values from the CSVs — there is no separate "defaults" concern.**
  The four sync objects are List custom settings, whose schema `<defaultValue>`s do **not** fire on
  DML — but the baseline CSVs enumerate every value, so installing the baseline yields a
  fully-populated root `Sync_Config__c` (plus any child/sub-configs). Creating the config is
  therefore not a separate "create-with-defaults" step and needs no confirmation beyond the install
  gate above; a bare hand-rolled insert, by contrast, would land an empty row.
- Several baseline **editions** ship (e.g. a Consumer Goods edition, a Direct-Store-Delivery
  edition, and a Retail Execution edition), each as its own static resource whose exact name is
  returned by `discoverConfigs`; **enumerate them from the endpoint at runtime, never hardcode the
  names** (the set expands across releases). Act 1 targets the **Retail Execution** edition — its
  exact static-resource name comes from `discoverConfigs` at runtime. A custom baseline beyond the
  shipped editions requires authoring the ZIP by hand — out of scope.

### 4. A1.4 — Verify the referenced field-set definitions exist — `core` (read-only describe)

- **Names — done by A1.3.** The `Fieldset_Name_List__c` and `List_Header_Fieldset__c` columns
  on `Sync_Tracked_Object_Config__c` are populated by the same install CSV. No separate step.
- **Definitions — provisioned by Retail Execution, not deployed by this skill.** The `FieldSet`
  metadata those names reference (chiefly `RetailMobilityRelevant`, wired to ~60 baseline rows on
  standard objects — Account, Contact, Event, Task, Product2, `InternalOrganizationUnit`, …) is
  **not shipped by the package** (a managed package can't own a FieldSet on a standard object) and
  is **not** a manual deploy in this flow either: **enabling Retail Execution (A1.2) provisions
  it.** So A1.4 is **not** an install/deploy step — there is no field-set "upload." But because the
  package only *consumes* field sets via Schema describe and the **sync query-field path throws**
  when a named set is missing (`SYNC_MetaDataUtils.getFieldsForFieldSetByFieldSetMapOrThrowException`
  → `SYNCException("We couldn't find the <name> field set …")`, exercised by
  `TrackedObjectUtilsTest.getFieldsForTOOrThrowException_unknownfieldSet_exception`), a missing set
  is a **hard failure at first sync, not at install** — so **verify, don't assume.**
- **The verify (this is the read-back A1.4 was missing).** After the install, for each distinct
  field-set name the installed baseline's `Sync_Tracked_Object_Config__c` rows reference
  (`Fieldset_Name_List__c` + `List_Header_Fieldset__c`, split on `,`), confirm the set exists on the
  object's schema — a **read-only `core` describe**, mirroring A1.2's post-write re-read:
  - Per object, read the field-set map — `Schema.describeSObjects(new String[]{objName})[0]`
    `.fieldSets.getMap()` via anonymous Apex (all describe variants — default options,
    `SObjectDescribeOptions.FULL`, `Schema.getGlobalDescribe()`, and the static
    `Schema.SObjectType.<obj>` reference — return the **same** field sets, verified on-org; the
    default `describeSObjects` is fine), or a Tooling `GET /tooling/query?q=SELECT DeveloperName,
    NamespacePrefix FROM FieldSet WHERE EntityDefinition.QualifiedApiName = '<obj>'`. The Tooling
    **`WHERE EntityDefinition.QualifiedApiName` filter is mandatory** — an unfiltered `FROM FieldSet`
    returns **zero rows** (reads as "no field sets" — a trap).
  - **Compare on the BARE name, case-insensitively — do NOT `containsKey` the raw referenced name.**
    `fieldSets.getMap()` keys are **all-lowercase and fully namespace-qualified** (`<ns>__name`), so
    `getMap().containsKey('RetailMobilityRelevant')` returns **false even when the set exists** (the
    real key is e.g. `<ns>__retailmobilityrelevant`) — the classic false-missing this step must
    avoid. Build the present-set from `FieldSet.getName().toLowerCase()` (`getName()` is the bare
    local name; `getNamespace()` is the prefix, separately), strip any `<prefix>__` off the referenced
    name (`substringAfterLast('__')`), and compare lowercased. In Tooling, compare `DeveloperName`
    case-insensitively.
  - **Whether a set is prefixed depends on the ORG, not the `$$NS` macro.** The CSV names use `$$NS`
    (`$$NSMobilityRelevant` → `<ns>__MobilityRelevant` at install). But `RetailMobilityRelevant`
    (no `$$NS`) is **not** always unprefixed: in a pure **subscriber** org RE provisions it as
    **standard** metadata (`NamespacePrefix` null), whereas in a **source-deployed / namespaced** org
    (the `Organization.NamespacePrefix` branch A1.1 handles) **every** set — including
    `RetailMobilityRelevant` — carries the **org namespace** (`getNamespace()` = `<ns>`, confirmed
    on-org). Comparing on the bare, lowercased local name (above) is correct for **both** org types;
    assuming a fixed prefix is not.
  - **All present → report verified** (RE provisioned them; nothing to deploy). This is the
    per-object `assert:` step A1.4 must end on, same convention as every other write's read-back.
  - **Any missing → report and stop that object.** Name the object + the absent field set, and
    state the owner: **Retail Execution provisioning (A1.2 / core-RE)**, not this skill and not the
    package. Do **not** attempt to deploy the FieldSet as a workaround — RE owns it; a hand-deployed
    set risks drifting from what RE and the baseline expect. If RE is enabled and the set is still
    absent, that's an RE-provisioning issue to escalate to the CG Cloud platform / Retail Execution
    owners, not a `FieldSet` this skill ships.

## Act 1 end state

- **Sync Management App metadata confirmed present and its namespace resolved** — either a
  managed-package install (Tooling API `InstalledSubscriberPackage` match, **namespace prefix +
  installed version captured** from the matched row) **or** the org's own namespace (`SELECT
  NamespacePrefix FROM Organization`, confirmed by resolving `<orgNs>Sync_Config__c` — no version in
  this case). On **neither** resolving, the run halted with "Sync Management App metadata not
  present" (install/deploy is out of scope). This is A1.1's opening gate, ahead of RE enablement (A1.2).
- A1.1/A1.2 readiness reported as an explicit Pass/Fail checklist; a hard miss halted the run.
- Admin-confirmed baseline (the Retail Execution root config, plus any sub-configs the admin also confirmed)
  **installed** across the four objects via the `/v1/syncconfig/install` endpoint (GET discover →
  confirmation gate → POST install), with `installed_config_id` / `installed_version` captured from
  the `InstallResponse` (never faked via raw sObject inserts). The install is the config: the root
  `Sync_Config__c` and its values come fully-enumerated from the baseline CSVs — no separate
  create-config step. Landing confirmed by the cheap **aggregate** check (sum of the four `core`
  COUNT() reads == `InstallResponse.recordsInserted`) — **not** the per-object/baseline-manifest
  comparison, which is Act 3's (A3.1/A3.2) and is deliberately not repeated here.
- Field-set names present (from the baseline CSV); the referenced field-set **definitions
  verified present** on each tracked object by a read-only `core` describe (RE provisions them via
  A1.2) — or any missing set reported-and-stopped with the owner named (RE provisioning), not
  deployed around.

## Gotchas

- **List-custom-setting defaults never auto-apply on DML.** This is why the baseline install (A1.3),
  not a raw insert, is the only correct way to create the config — a package-wide constraint: don't
  assume an inserted `Sync_Config__c` row has its declared defaults. The baseline CSVs carry every
  value; a bare insert would not.
- **A dispatcher-404 for RE enablement is not "capability missing" — it's a transport switch.**
  On a dispatcher-absent org, fall back to MDAPI: read via `Settings:RetailExecution` retrieve
  and **write via `sf project deploy start --metadata "Settings:RetailExecution"`**. Prefer the
  MDAPI fallback over stopping the step — fall back, don't stop. Only *advanced*-RE (the
  `orgHasAdvncdRetailExecutionPilot` gate) is truly un-writable.
- **RE enable applies dependent-pref defaults.** Enabling `enableRetailExecution` can flip
  sub-prefs you didn't set (for example, `enableVisitSharing` going true as a dependent default).
  Always re-read after the write; report the post-write state, not the file you deployed.
- **Namespace first.** Resolve the live prefix (A1.1's namespace gate — package or org namespace) before any package-object path;
  `SyncConfigInstall` handles it internally, but any sObject-REST path you emit must use the
  resolved prefix — never a hardcoded one.
- **The install is idempotent by guard, not by luck** — a re-run against an installed
  `configId` is a designed no-op; don't treat the guard message as an error.
