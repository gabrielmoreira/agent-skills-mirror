# Reference — Transports & Namespace

Load-bearing background for [`consumer-goods-sync-management-configure`](../SKILL.md). Read this before
authoring any step: it defines the two transports every step must be tagged with, and the
namespace discipline that every Sync Management App sObject/REST reference depends on.

## The two transports (the honesty spine)

Every step in every Act is exactly one of these. Tag it explicitly; never let a step be
untagged.

| Tag | Meaning | Where the action comes from |
|-----|---------|------------------------------|
| **`core`** | A generic Salesforce / Headless-360 capability. | `execute_api` (`/query`, `/tooling/query`, `/sobjects/`, `/connect/`, `/headless/*`). |
| **`Sync Management App`** | An in-package action the agent can trigger **today**. | A **`global @RestResource /v1/*`** endpoint (the ONLY headless package surface — see below). |

Where neither transport can complete a required step, report what's missing and who provides it
(the CG Cloud platform / Retail Execution, or the org admin), then stop that step — never fake it.

> **Transport reality check (do not skip).** The only real headless `Sync Management App` surface
> is the set of **`global @RestResource /v1/*`** endpoints. This matters because the install/verify
> logic exists as **`public`** Apex — and in a managed package `public` is **namespace-private**:
> unreachable from a subscriber org's anonymous Apex *or* REST. Only `global` members are
> reachable. So "the class has a method that does it" is **not** sufficient to call a step
> `Sync Management App`; there must be a `global`/`webservice` entry point (a `/v1/*` route) that reaches it.

Every automatable step resolves to a generic core capability or an invokable Sync Management App
action. Where neither exists for a required step, the skill reports what's needed and who
provides it, then stops that step rather than faking it.

### How to decide the tag

1. **Is there a `global @RestResource /v1/*` endpoint that does it?** → `Sync Management App`.
   (A `public` Apex method does **not** count — it's namespace-private, unreachable from a subscriber org.)
2. **Else, is it a generic Salesforce operation via `execute_api`
   (SOQL, sObject REST, Connect, Tooling)?** → `core`. *Note: the
   four sync objects are **custom settings**, so generic sObject REST + SOQL reach them as
   `core` — this covers most **reads** without any package change.*

If neither applies, the step is not automatable here — state what's missing, who provides it
(Sync Management App package code, or CG Cloud core / Retail Execution / the platform), and stop
that step. Do not invent a Sync Management App action to paper over a core limitation, and do not
fake success.

### What isn't automatable here

A3.1 verification is record counts via `core` SOQL — the intended method, so there is no
`/v1/syncconfig/verify` endpoint. And A2.2 IOU-membership *creation* is a CG Cloud core / Retail Execution task done
outside this flow — the skill only **reads** IOU membership as a `Default_IOU` precondition and
reports-and-stops if absent; it never writes it.

## The real `Sync Management App` headless surface: `global @RestResource /v1/*`

The **only** package actions an agent can trigger from a subscriber org today. `global`
endpoints in `force-app/main/default/classes/*Endpoint.cls`:

| Route | Purpose |
|-------|---------|
| `/v1/managedpackage` | Check whether the package is installed (`isManagedPackageInstalled`) — **check only, does not install**. |
| `/v1/devicemetadata` | Device metadata (feature settings) — **read-only**. |
| `/v1/namedquery`, `/v1/namedfetchtree` | Read named queries / fetch trees for a client app. |
| `/v1/download`, `/v1/upload` | Device sync data transfer. |
| `/v1/batchsoql`, `/v1/batchdml` | Generic SOQL/DML, but **gated by `isClientAppIdAvailable()`** (needs a pre-existing `Sync_Config__c`). |
| `/v1/assignment`, `/v1/clientappmapper`, `/v1/clientregistration`, `/v1/bulksobjectdescribe`, `/v1/metadata` | Device-facing sync support. **`/v1/assignment` (`AssignmentEndpoint`) is NOT the A2.3 user→config binding surface** — despite the name, it's a device call that *deletes* `Sync_ID_Mapping__c` local-id rows (`@HttpPost cleanRequest(recordIdList, deviceId)`) — note `Sync_ID_Mapping__c` is a **regular custom object** (the device-owned local-to-server id map), **not** one of the config List custom settings. For A2.3 use **`/v1/syncconfig/assignment`** (row below). |
| `/v1/syncconfig/install` | `SyncConfigInstallEndpoint`. **POST** installs a baseline (`installConfig`, body `{"req":{"staticResourceName":"..."}}`) → `InstallResponse` (status/configId/version/recordsInserted). **GET** (`discoverConfigs`) lists installable baselines with availability (`AVAILABLE` / `ALREADY_INSTALLED` / `REQUIRES_PARENT`) so a caller can discover the `staticResourceName` before POSTing. Provides the A1.3 baseline install path. |
| `/v1/syncconfig/configs` | `SyncConfigListEndpoint`. **GET** (`listConfigs`) lists every **deployed** `Sync_Config__c` as `{name, clientAppId, resolutionStrategy}` — distinct from install's `discoverConfigs` (installable *baselines*), this is what's actually *deployed*. Lets an assignment caller pick a config by name; the `name` it returns is the value `/v1/syncconfig/assignment` expects as `configPath`, and `resolutionStrategy` tells the caller whether the assignment takes an IOU id (`Default_IOU`) or a Business Area value (`Custom_User_Field`). Provides the *list* half of A3.1's read/verify path. |
| `/v1/syncconfig/assignment` | `SyncConfigAssignmentEndpoint`. Binds a Sync Config to a User(`005`)/Role(`00E`)/Profile(`00e`) — the headless "Config Assignment page". **Do not confuse with the device-facing `/v1/assignment` (`AssignmentEndpoint`) above** — that one cleans `Sync_ID_Mapping__c` device rows and is *not* the user→config surface; A2.3 is **this** `/v1/syncconfig/assignment` route (`Sync_Client_App_Profile_Mapping__c`). **GET** `?configId=<name>` lists assignments (resolves target names); **POST** body `{"req":{configPath, mappedRecordId, businessArea, iouId, recordId}}` upserts; **DELETE** `?id=<name-or-id>` removes. **This is the safe A2.3 explicit-mapping surface — a raw sObject POST to `Sync_Client_App_Profile_Mapping__c` is UNSAFE** because `Business_Area_Name__c` is overloaded (IOU Id under `Default_IOU`, Business Area picklist value under `Custom_User_Field`); the endpoint derives it from the config's strategy server-side and also enforces cross-config dedup + the unique-Name convention. Provides the A2.3 explicit-mapping capability. |

> The three `/v1/syncconfig/*` routes cover install/discovery, listing deployed configs with
> strategy, and binding a Sync Config to a User/Role/Profile with server-side derivation of the
> overloaded `Business_Area_Name__c` field from the config's resolution strategy. Their
> package-release rollout is a separate workstream. What the skill must never do is *fake* these
> calls: for the install, do **not** hand-roll raw sObject inserts (skips the ZIP orchestration,
> `$$NS` macro, ordering, and state rows); for A2.3, do **not** substitute a raw
> `Sync_Client_App_Profile_Mapping__c` write (it corrupts the overloaded
> `Business_Area_Name__c`). A `core` SOQL list is an equivalent fallback for the A3.1 *read/verify*
> path.

### Building the callable URL — the namespace goes in the ROUTE, not just the object names

The table above lists each endpoint's `urlMapping` (`/v1/syncconfig/*`). That is **not** the
callable path. Apex REST routes are served under `/services/apexrest`, and **when the metadata
carries a namespace the namespace is injected as a path segment** — exactly as it is for object
API names. This bites the org-namespace source-deploy case the skill treats as first-class: a
first call to `/services/apexrest/v1/syncconfig/configs` returns **`NOT_FOUND`**; the reachable
URL is `/services/apexrest/<ns>/v1/syncconfig/configs`.

- **Rule:** `POST/GET/DELETE /services/apexrest/<ns>/<urlMapping>`, where `<ns>` is the resolved
  namespace **as a bare segment** — and this applies to **both** namespace sources:
  a managed-package install **and** an org-namespaced source deploy. Only a bare *unmanaged* deploy
  (no namespace at all) omits the segment.
- **`<ns>` here is the bare namespace, NOT `ns_prefix`.** `ns_prefix` carries the trailing `__`
  (`<ns>__`) and is what prefixes **object/field API names** (`<ns>__Sync_Config__c`).
  The **URL segment is the namespace *without* the underscores** (`<ns>`). Strip the trailing
  `__` from `ns_prefix` to build the route segment.

| Namespace source | Object API name | Callable route |
|---|---|---|
| Namespaced — **either** a managed-package install **or** an org-namespaced source deploy | `<ns>__Sync_Config__c` | `/services/apexrest/<ns>/v1/syncconfig/configs` |
| Bare unmanaged (no namespace) | `Sync_Config__c` | `/services/apexrest/v1/syncconfig/configs` |

Resolve `<ns>` once from A1.1's namespace gate (same value the object paths use, minus the `__`)
and build every `/v1/syncconfig/*` route with it. A `NOT_FOUND` on a `/v1/*` route in a namespaced
org almost always means the segment was omitted — not that the endpoint's release is missing (probe
that only after confirming the namespaced URL also 404s).

**A3.1's *list* half is now covered by `/v1/syncconfig/configs`, and its *verify* half is record
counts via generic `core` SOQL — the intended method, which works today.** No `/v1/syncconfig/verify`
endpoint is proposed: Act 3 verification adds no Sync Management App call, so `SyncConfigOrchestrator`'s
state readers (`buildStateMap()` / `readCurrentVersion()` are `public static`, their helper
`installedVersionMap()` `private static`) being namespace-private is moot.

## Namespace discipline

- **The namespace has two possible sources — a package install OR the org's own namespace.** When
  the metadata is installed as a **managed package**, the prefix is the package's, which **varies by
  how it was built** (a production install and a non-production/CI build can carry different
  prefixes). When the metadata is **source-deployed into a DE/packaging/dev org**, it takes the
  **org's own registered namespace** (`Organization.NamespacePrefix`) and there is **no**
  `InstalledSubscriberPackage` row at all. Never assume a specific value, and never assume a
  package install — an empty package list can still be a fully-namespaced org.
- **Resolve the prefix at runtime — never hardcode.** The package itself resolves via
  `SYNC_NamespaceHandler` / `SYNCConstants.NAMESPACEPREFIX`. For agent-issued `core` SOQL /
  sObject REST against package objects, **discover the live prefix** in this order: (1) match the
  Sync Management App package in `InstalledSubscriberPackage` and read its `NamespacePrefix`
  (Tooling); (2) if there's no such row, read the **org namespace** with `SELECT NamespacePrefix
  FROM Organization` (plain `core`, no Tooling) and confirm by resolving `<orgNs>Sync_Config__c`;
  (3) failing both, probe candidate prefixes (package's known namespace(s), the org namespace, bare
  unmanaged) via one known object's describe. Then substitute the resolved value as `<ns>` in every
  package-object reference. See [readiness-and-enablement.md](readiness-and-enablement.md) A1.1.0 for the
  full gate.
- **Core objects carry no namespace.** `User`, `InternalOrgUnitUser`,
  `InternalOrganizationUnit`, `Profile`, `UserRole`, etc. are core — do **not** prefix
  them. Only the four sync objects + `Sync_Config_State__c` + `Sync_Client_App_Profile_Mapping__c`
  and other package custom settings take `<ns>`.
- **Why it bites:** the four sync objects are **List custom settings**. Their schema
  `<defaultValue>`s do **not** auto-apply on Apex/`sobjects` DML insert — the install path
  populates them from baseline CSVs, not from schema defaults. See
  [sync-management-app-install-backbone.md](sync-management-app-install-backbone.md).

## Dispatcher vs. direct REST (which `execute_api` path)

- **`@AuraEnabled` / Apex-controller actions** go through the H360 **dispatcher**
  (`/headless/invoke/...` envelope).
- **Generic reads/writes bypass the dispatcher and hit Core directly** — `/query`,
  `/tooling/query`, `/sobjects/`, `/connect/`. Nearly every
  `core` step in this skill is a direct-REST read/write, not a dispatcher call.

## `sf` CLI cookbook — parse-safe invocations (the CLI-fallback path)

When `execute_api` is unavailable or unauthenticated, every `core` and `Sync Management App`
op runs through the `sf` CLI. The CLI is only sugar over the REST resources above, but two concrete
mechanics bite hard and cost retries — bake these in:

- **stdout hygiene — the linked-plugin banner pollutes output.** In this workspace the linked
  ESM plugin prints `Warning: @ind-rcg/modeler-sfdx-cli-plugin is a linked ESM module …` on the
  first line, so `sf … --json` piped to a JSON parser (`python3`, `jq`) fails intermittently with `KeyError: 'result'` /
  a JSON parse error. **Always `2>/dev/null` before parsing**, and if a stray line still slips into
  stdout, slice from the first `{`/`[` (e.g. `sed -n '/^[[{]/,$p'`) before piping to a parser.
- **`--body @file.json` needs the `@`.** `sf api request rest … --body @install.json` reads the
  request body **from the file**; without the `@` the CLI sends the literal string `install.json`
  as the body → `JSON_PARSER_ERROR` on the POST. Write the body to a temp file, pass it with `@`.
- **Batch the four-object COUNT() verify into ONE anonymous-Apex call — never loop `sf data
  query` per object.** Each `sf` invocation cold-starts the CLI (~15–20s); a 4–5-object COUNT()
  loop blows the 2-min tool timeout. Run **one** `sf apex run` whose anonymous block queries all
  four sync objects (+ `Sync_Config_State__c`) and `System.debug`s a single JSON blob — one
  cold-start, every count. **This is the default for the A1.3 landing check and the A3.1 count
  verify** (form 6 below); a single `sf data query COUNT()` (form 1) is fine only for a genuine
  one-off read.
- **Parsing `sf apex run` output — grep `USER_DEBUG` FIRST.** `sf apex run` echoes the anonymous
  block back as `Execute Anonymous:` source lines, so a bare grep for your marker string matches the
  **echoed source** as well as the real `USER_DEBUG|…` line → two hits, parse failure. Always filter
  to `USER_DEBUG` before extracting the marker (the direct analogue of the linked-plugin banner
  hazard above): `… | grep USER_DEBUG | grep -o 'SYNCCOUNTS=.*'`.

Copy-pasteable forms (substitute `<org>` alias and the resolved `<ns>`/`<ns_prefix>`):

```bash
# 1. core SOQL query (objects take ns_prefix with trailing __)
sf data query --target-org <org> --json 2>/dev/null \
  --query "SELECT COUNT() FROM <ns_prefix>Sync_Config__c"

# 2. core Tooling query (InstalledSubscriberPackage, FieldSet, RetailExecutionSettings, …)
sf data query --use-tooling-api --target-org <org> --json 2>/dev/null \
  --query "SELECT SubscriberPackage.Name, SubscriberPackage.NamespacePrefix FROM InstalledSubscriberPackage"

# 3. Apex-REST GET — namespace is a ROUTE SEGMENT (bare ns, no __); see "Building the callable URL"
sf api request rest "/services/apexrest/<ns>/v1/syncconfig/configs" \
  --target-org <org> 2>/dev/null

# 4. Apex-REST POST with a body FILE — note the @ prefix
printf '%s' '{"req":{"staticResourceName":"<name>"}}' > "$TMPDIR/install.json"
sf api request rest "/services/apexrest/<ns>/v1/syncconfig/install" \
  --method POST --body @"$TMPDIR/install.json" \
  --target-org <org> 2>/dev/null

# 5. Apex-REST DELETE (assignment removal)
sf api request rest "/services/apexrest/<ns>/v1/syncconfig/assignment?id=<name-or-id>" \
  --method DELETE --target-org <org> 2>/dev/null

# 6. Batched four-object COUNT() verify — ONE cold-start, all counts as a JSON blob
#    (DEFAULT for the A1.3 landing check and the A3.1 count verify; SOQL takes ns_prefix + trailing __)
cat > "$TMPDIR/counts.apex" <<'APEX'
Map<String,Integer> c = new Map<String,Integer>{
  'Sync_Config__c'                 => [SELECT COUNT() FROM <ns_prefix>Sync_Config__c],
  'Sync_Tracked_Object_Config__c'  => [SELECT COUNT() FROM <ns_prefix>Sync_Tracked_Object_Config__c],
  'Sync_Named_Fetch_Tree_Nodes__c' => [SELECT COUNT() FROM <ns_prefix>Sync_Named_Fetch_Tree_Nodes__c],
  'Sync_Named_Query__c'            => [SELECT COUNT() FROM <ns_prefix>Sync_Named_Query__c],
  'Sync_Config_State__c'           => [SELECT COUNT() FROM <ns_prefix>Sync_Config_State__c]};
System.debug('SYNCCOUNTS=' + JSON.serialize(c));
APEX
sf apex run --target-org <org> --file "$TMPDIR/counts.apex" 2>/dev/null \
  | grep USER_DEBUG | grep -o 'SYNCCOUNTS=.*'   # grep USER_DEBUG FIRST — the block is echoed too
```

`sf data query` returns `{"result":{"records":[…],"totalSize":N}}`; a bare `SELECT COUNT()` puts the
count in `result.totalSize`. `sf api request rest` returns the endpoint's raw JSON body (no
`result` envelope). `sf apex run` returns the debug log — the counts ride a `USER_DEBUG` line, and
the block is echoed as `Execute Anonymous:` source, so **grep `USER_DEBUG` before extracting**. All
three still need the `2>/dev/null` banner strip before parsing.
