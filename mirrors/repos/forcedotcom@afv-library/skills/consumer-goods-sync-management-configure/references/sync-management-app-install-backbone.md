# Reference — The Sync Management App Sync-Config Install Backbone

Background for [Act 1](act1-setup-sync.md). The install *logic* here is the
backbone of the whole steel thread. The logic lives in `public` (namespace-private) Apex with no
`global`/REST entry point, so it isn't directly callable from a subscriber org. The package exposes
it headlessly through `SyncConfigInstallEndpoint` (`@RestResource /v1/syncconfig/install`, GET
discovery + POST install) — a thin `global` wrapper over `installBaseline` (see "The headless
install endpoint" below). Understanding the underlying logic precisely still matters because it's
the most important capability and everything in Act 1 either feeds this install or works around
what it does *not* do.

## The four sync objects (+ state)

Installed/populated by the backbone; all are **List custom settings** (each prefixed by the
runtime-resolved namespace — from the installed package or the org's own namespace, written `<ns>`
below):

| Object | Role |
|--------|------|
| `Sync_Config__c` | Root sync configuration (the installed baseline root — e.g. the Retail Execution baseline; there is no config literally named "Standard"). |
| `Sync_Tracked_Object_Config__c` | Which objects sync + per-object settings. |
| `Sync_Named_Fetch_Tree_Nodes__c` | Fetch-tree graph (parent/child fetch relationships). |
| `Sync_Named_Query__c` | Named queries the client runs to fetch data. |
| `Sync_Config_State__c` | Per-config **version** rows — how installed version is tracked. |

**List custom settings ⇒ no auto-defaults on DML, but also ⇒ reachable via generic `core`
sObject REST + SOQL.** Two consequences:
- A raw `POST /sobjects/<ns>Sync_Config__c` inserts a bare row; the schema `<defaultValue>`s do
  **not** fire. This is exactly why the baseline CSVs (not schema defaults) carry every value —
  installing the baseline yields a fully-populated config; a hand-rolled insert would not.
- Because they're custom settings, **generic `core` reads** (`GET /query?q=...`) reach them with
  no package code — this is what makes A3.1 count/version *verification* doable **today**. But
  **row-level *writes* are not all safe as raw `POST /sobjects/<ns>...`.** The
  `Sync_Client_App_Profile_Mapping__c` assignment row (A2.3) carries the **overloaded**
  `Business_Area_Name__c` field (an IOU Id under `Default_IOU`, a Business Area picklist value under
  `Custom_User_Field`); a raw insert that doesn't derive it from the config's strategy silently
  corrupts the row (and skips dedup + the unique-Name convention). That write must go through the
  **`/v1/syncconfig/assignment` endpoint** (`SyncConfigAssignmentEndpoint`, A2.3), which wraps the
  same service the VF page uses. What generic sObject REST also cannot do is run the baseline-ZIP
  install orchestration (unzip, `$$NS` macro, ordered multi-object insert, state-row bookkeeping) —
  that's the `public` logic that now has a `global` wrapper (`SyncConfigInstallEndpoint`, A1.3; see
  below).

### Field dictionary — the API names the skill's own reads/writes touch

Casing matters and several fields are **not** named the obvious way — guessing costs a describe
round-trip per miss. These are the exact API names (verified against the package object metadata)
for the fields this skill queries or writes. All take the `<ns>` prefix at runtime; the names below
are the unprefixed `__c` suffixes.

| Object | Field(s) the skill uses | Purpose / gotcha |
|--------|-------------------------|------------------|
| `Sync_Config__c` | `ClientApp_ID__c`, `Business_Area_Resolution_Strategy__c`, `Business_Area_Mapping__c` | Config root. `ClientApp_ID__c` keys the config (the `clientAppId` the list/assignment endpoints return); `Business_Area_Resolution_Strategy__c` is `Default_IOU` vs `Custom_User_Field`. |
| `Sync_Tracked_Object_Config__c` | `Object_Api_Name__c`, `Fieldset_Name_List__c`, `List_Header_Fieldset__c`, `ClientApp_ID__c` | Per-tracked-object. **It's `Object_Api_Name__c`** — not `Tracked_Object_API_Name__c`. `Fieldset_Name_List__c` + `List_Header_Fieldset__c` hold the A1.4 field-set names (comma-split). |
| `Sync_Named_Fetch_Tree_Nodes__c` | `Object_Api_Name__c`, `Fetch_Tree_Name__c`, `Parent_Node_Id__c` | Fetch-tree graph; count-only for A3.x. |
| `Sync_Named_Query__c` | `Bindable_Name__c`, `SOQL_Statement__c`, `Type__c` | Named queries; count-only for A3.x. |
| `Sync_Config_State__c` | `Current_Version__c`, `Initial_Install_Version__c`, `Last_Upgrade_Date__c` | Installed version is **`Current_Version__c`** — there is **no** `Config_Id__c` on this object; rows are keyed by the custom-setting `Name`, not a config-id field. |
| `Sync_Client_App_Profile_Mapping__c` | `Client_App_ID__c`, `Client_App_Profile__c`, `Mapped_Record_Id__c`, `Business_Area_Name__c` | The A2.3 assignment row (write via the endpoint, never raw). `Business_Area_Name__c` is the overloaded IOU-Id/Business-Area field. |

**The client-app field is spelled two different ways across objects — do not conflate:**
`Sync_Config__c` and `Sync_Tracked_Object_Config__c` use **`ClientApp_ID__c`** (no underscore
between "Client" and "App"), while `Sync_Client_App_Profile_Mapping__c` uses
**`Client_App_ID__c`** (underscore between every word). Both end `_ID__c` (uppercase `ID`).

When in doubt, **describe the object before querying** rather than guessing a field name — but
these are the ones the flow actually needs.

## The logic: `SyncConfigInstall.installBaseline(String staticResourceName)`

- Reads a **`SyncConfigBaseline_*` static-resource ZIP** containing `manifest.json` + CSVs.
- The `manifest.json` declares per-object CSVs; a namespace macro (`$$NS`) is rewritten to the
  live prefix at install; per-config `Sync_Config_State__c` version rows are written so the
  installed version is recorded.
- `SyncConfigOrchestrator` drives the orchestration and exposes the state readers
  (`buildStateMap()` / `readCurrentVersion()`, backed by the `private` helper
  `installedVersionMap()`).

## Why the install needs a package endpoint (not a raw insert)

The underlying logic is `public` (namespace-private) — the reason A1.3 (the baseline install,
which *is* the sync-configuration creation) needs the endpoint rather than a raw insert:

- `SyncConfigInstall` is declared **`public virtual with sharing`**; `installBaseline` is
  **`public static`** — no `global`/`webservice`/`@RestResource`/`@InvocableMethod` of its own.
- The one caller that "ran" it, `MobileAppController.installManagedBaseline()`, is a
  **`public PageReference`** Visualforce action — also not `global`/REST/invocable.
- The state readers on `SyncConfigOrchestrator` — `buildStateMap()` / `readCurrentVersion()` — are
  **`public static`, unannotated** (their helper `installedVersionMap()` is **`private static`**).
- In a managed package, **`public` = namespace-private**: a subscriber org can invoke only
  `global` members via anonymous Apex or REST (a `private` member is even less reachable). So none
  of the above is reachable headlessly.

### The headless install endpoint — `SyncConfigInstallEndpoint`

The endpoint is a thin `global @RestResource(urlMapping='/v1/syncconfig/install/*')` wrapper over
the existing `public` logic — **no logic changes to the install path itself.**

- **POST `installConfig`** — body `{"req":{"staticResourceName":"..."}}` → `installBaseline`;
  returns an `InstallResponse` (`status` SUCCESS/FAILED, `configId`, `version`, `recordsInserted`,
  `errorMessage`). **On `status == FAILED` (or a thrown call), report `errorMessage` and stop —
  a `FAILED` body inside an HTTP 200 is a failure, not success, and there is no raw-sObject
  recovery** (see A1.3). **Single argument — `staticResourceName`. There is no `parentConfigId` param:**
  parent linkage is read from the baseline ZIP's `manifest.json` (`parentConfigId`), not passed by
  the caller. The install still guards a missing parent (a child whose parent isn't installed
  fails) — but that's derived from the manifest, not a method argument.
- **GET `discoverConfigs`** — lists installable baselines as `ConfigOption`s
  (`configId`, `displayName`, `parentConfigId`, `staticResourceName`, `availability`,
  `requiresLabel`), each classified `AVAILABLE` / `ALREADY_INSTALLED` / `REQUIRES_PARENT`. This is
  the discovery step: call GET to find the `staticResourceName` to POST. Wraps
  `SyncConfigOrchestrator.discoverBaselines()` (the same read the admin VF install dropdown uses) —
  read-only, no side effects.
- **Access** is by Apex class access — granted through *a* permission set in the target org (named
  e.g. `Sync_Admin`, but that name can be renamed or folded into another set across orgs/releases,
  so never depend on it) — **not** a runtime CRUD gate: the four objects are List custom settings,
  for which `SYNCSecurityUtil.isObjectPermissible()` always returns true, so a CRUD gate would be a
  no-op. The skill does not verify a permission set by name; a denied call is reported as an access
  boundary (with who grants it).
- Never substitute a raw sObject insert for the endpoint — that skips the ZIP orchestration, `$$NS`
  macro, ordering, and state rows.

A3.1 verification is record counts via generic `core` SOQL — the intended method, which works
today — so **no `/v1/syncconfig/verify` surface is proposed**; the state readers being
`public`/namespace-private is moot. Two sibling `/v1/syncconfig/*` endpoints ship alongside
install: **`/configs`** (`SyncConfigListEndpoint`, GET — lists every deployed `Sync_Config__c` as
`{name, clientAppId, resolutionStrategy}`; closes A3.1's *list* half) and **`/assignment`**
(`SyncConfigAssignmentEndpoint`, GET/POST/DELETE — the safe A2.3 user→config binding surface). See
[transports-and-namespace.md](transports-and-namespace.md) for the endpoint table.

## The shipped baselines

Several baseline **editions** ship — covering Consumer Goods, Direct-Store-Delivery, and Retail
Execution — each as its own static resource. **Enumerate them from the discovery endpoint
(`discoverConfigs`) at runtime; never hardcode the names or assume a fixed set** — editions are
added across releases.

**Pick the baseline that matches the org's edition.** The steel thread is the **Retail Execution**
path (its exact static-resource name comes from the discovery endpoint at runtime — never hardcode
it). **Act 3 verification derives the expected counts at runtime from whichever baseline was
actually installed** (that baseline's own manifest/CSVs) and compares them to the installed record
counts — it must **not** assert against hardcoded literals, since a different baseline (or release)
declares different counts.

## What the backbone does NOT do (and who owns those pieces)

- It does **not** resolve the **namespace** or **enable Retail Execution** (A1.1/A1.2 — core). (There is no license read to do — installing/using the app is not license-gated.)
- It does **not** ship **field-set definitions** (A1.4 — the CSV assigns field-set *names*; the
  `FieldSet` metadata they reference, chiefly `RetailMobilityRelevant` on standard objects, is
  **provisioned by Retail Execution**, not by this install and not by a separate deploy in this
  flow — a managed package can't own a FieldSet on a standard object). A1.4 therefore **verifies**
  the referenced sets exist (read-only describe), rather than deploying them; a missing set is an
  RE-provisioning issue, and because the sync query-field path throws on it, the verify matters.
- It does **not** write **IOU membership** (A2.2 — core/RE; the skill only *reads* it as a
  `Default_IOU` precondition and never writes it). User→config *assignment* (A2.3) and
  *listing* deployed configs (A3.1) are now handled by the sibling `/v1/syncconfig/assignment` and
  `/v1/syncconfig/configs` endpoints, not by the install backbone. A3.1 verification is record
  counts via `core` SOQL — no additional invokable action is needed.

Treat `installBaseline` as the trunk; every other Act-1 sub-act is a branch that either prepares
its input (right baseline, RE-enabled, namespace resolved) or fills something it leaves undone.
