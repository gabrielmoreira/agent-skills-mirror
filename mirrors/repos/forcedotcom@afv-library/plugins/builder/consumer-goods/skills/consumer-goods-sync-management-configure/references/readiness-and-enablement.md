# Reference — Namespace Gate & Retail-Execution Enablement (core precedents)

Background for [Act 1](act1-setup-sync.md) sub-acts A1.1, A1.2. Both are **core**
concerns — resolving the namespace and toggling Retail Execution both go through generic Salesforce
capabilities, not a package endpoint — so the pattern is a generic `core` transport; where no
automatable path exists, the skill reports what's needed and who provides it, then stops that step.

## A1.1 — Verify the Sync metadata is present and resolve its namespace (hard gate) — `core`

### A1.1.0 — Namespace-resolution gate (the hard prerequisite) — `core` Tooling API + `core` Organization query

The whole skill presupposes the Sync Management App sync objects exist and their namespace is
known — no sync object, `/v1/*` endpoint, or namespace reference works otherwise. The namespace
resolves from **one of two sources**: a **managed-package install** (`InstalledSubscriberPackage`,
below) or the **org's own registered namespace** (`Organization.NamespacePrefix`, for a
source-deployed DE/packaging org). **Verify presence and resolve the namespace as the very first
thing A1.1 does.** Start with the package check via the generic **Tooling API** (Option 2):

```text
GET /services/data/vXX.0/tooling/query?q=
    SELECT SubscriberPackage.Name, SubscriberPackage.NamespacePrefix,
           SubscriberPackageVersion.MajorVersion, SubscriberPackageVersion.MinorVersion,
           SubscriberPackageVersion.IsBeta
    FROM InstalledSubscriberPackage
```

- **Why Tooling, not the package's own endpoint.** The package *does* ship
  `ManagedPackageEndpoint` (`GET /v1/managedpackage?method=isManagedPackageInstalled&namespacePrefix=<ns>`,
  which internally does `UserInfo.isCurrentUserLicensed(ns)` and treats "didn't throw" as
  installed). But that route is *served by* the package — **if the package is absent the route
  404s**, so it cannot report absence (chicken-and-egg). The Tooling query is generic `core` and
  answers definitively either way, **and** returns the installed *version* — which the package
  endpoint does not. Use `/v1/managedpackage` only as an optional confirming call once Tooling has
  already said the package is present.
- **No server-side filter.** `InstalledSubscriberPackage` doesn't support a `WHERE` on the
  packaging fields — query all rows and match client-side by `SubscriberPackage.Name` (the Sync
  Management App package), then **read the matched row's `NamespacePrefix` off the result** — don't
  assume a fixed prefix; the org carries whatever the installed package was built with.
- **Two outputs from a match:** (a) the **namespace prefix** (read from the matched row) that every
  later package-object reference resolves to, and (b) the **installed version**, recorded for
  reference. (The
  `/v1/syncconfig/*` endpoints' package-release rollout is a separate workstream — no
  version-gating logic is needed here.)
- **Transport:** `sf data query --use-tooling-api --query "..."` when the CLI is present, else a
  plain REST `GET /services/data/vXX.0/tooling/query?q=<url-encoded SOQL>` (via `execute_api` or any
  session-token client — the CLI is only sugar over this).

#### The namespace has two sources — package OR org (don't stop at an empty package list)

A match on `InstalledSubscriberPackage` is the **managed-package install** case — a subscriber org.
But the sync metadata can also be **source-deployed under the org's *own* registered namespace** (a
Developer Edition / packaging / dev org), and then `InstalledSubscriberPackage` returns **no row at
all** even though the sync objects are present. An empty package list is therefore **not** an
automatic hard miss — fall back to the org namespace:

- **Org-namespace fallback (`core`, no Tooling needed):** `SELECT Id, NamespacePrefix FROM
  Organization`. A non-null `NamespacePrefix` is the org's own namespace; treat it (with the
  trailing `__`) as `ns_prefix`. **Confirm** the sync metadata actually lives under it by resolving
  one known object — `GET /sobjects/<orgNs>Sync_Config__c/describe` or `SELECT COUNT() FROM
  <orgNs>Sync_Config__c` — a success means the run proceeds under the org namespace. There is **no
  `SubscriberPackageVersion`** in this case; endpoint-version gating doesn't apply to a
  source-deployed org (the `/v1/syncconfig/*` classes are either deployed or not — probe the route).
- *Worked example:* a DE org with a non-null `Organization.NamespacePrefix` (say `<orgNs>`) and
  zero `InstalledSubscriberPackage` rows resolves `ns_prefix = <orgNs>__`, and
  `<orgNs>Sync_Config__c` describes successfully — the run proceeds; the empty package list was a
  red herring.

- **Describe fallback (no Tooling access):** `GET /sobjects/<ns>Sync_Config__c/describe` across the
  candidate prefixes — the package's known namespace(s), **the org namespace** from `SELECT
  NamespacePrefix FROM Organization` (a plain `core` query, no Tooling), and the bare (unmanaged)
  name — 200 = that prefix is the live one (no version); `NOT_FOUND` = that prefix absent.
  `NOT_FOUND` on all probed = absent. Prefer the Tooling query when available — only it returns the
  installed *version* for the package case.
- **Hard miss = STOP the whole run — only when NEITHER source resolves.** If no
  `InstalledSubscriberPackage` row matches **and** the org has no namespace (or `<orgNs>Sync_Config__c`
  doesn't describe) **and** the object isn't present unmanaged (bare `Sync_Config__c`), report "the
  Sync Management App metadata is not present in this org (no managed package, no org-namespaced
  deploy)" and halt — **installing/deploying it is org setup outside this skill's scope**, not a
  step the skill performs. This is the outermost admission gate, ahead of RE enablement (A1.2),
  which presupposes the sync objects exist.

### A1.1.1 — No license read, no permission-set gate (readiness is exactly two checks)

Installing and using the Sync Management App is **not** license-gated: there is no license or SKU
to detect, and package install is not entitlement-gated. So A1.1 runs **no** license query and the
skill declares no license `accessCheck`.

**Equally, do NOT verify the existence of any named permission set as a readiness gate.**
Permission-set names are unstable — renamed or folded into another set with a different name across
releases and orgs — so a name-based existence check would false-block a perfectly capable org.

The Act-1 readiness gates are therefore **exactly two**: **(1) the Sync Management objects are
present** (the namespace gate, A1.1.0 above) and **(2) Retail Execution is enabled** (A1.2 below) —
RE is an org *preference*, not a license, so it is enabled in A1.2 rather than probed for as an
entitlement here. Access to the install/assignment endpoints is granted by *some* permission set in
the target org whose name is the admin's concern, not a value the skill asserts; a denied call is
reported as an access boundary (with who grants it), never gated on a specific permission-set name.

## A1.2 — Enable Retail Execution — `core` read + `core` write

- Enabling base RE is a **working `core` write**: an MDAPI `Settings:RetailExecution` deploy flips
  `enableRetailExecution` **false → true**. Dry-run first, then re-read to confirm.
- **What the read shows depends on the transport:**
  - **Dispatcher (Headless-360)** `getRetailExecutionEnableSetting` returns **5 prefs**
    (`isRetailExecutionEnablePrefEnable`, `isProductHierarchyPrefEnabled`,
    `isVisitSharingPrefEnabled`, `isCGAgentsPrefEnabled`, `isCGGenAIPrefEnabled`) + 4 read-only
    echo flags.
  - **MDAPI `Settings:RetailExecution`** exposes **3** booleans (`enableRetailExecution`,
    `enableProductHierarchy`, `enableVisitSharing`). Same org pref
    (`ORG_PREFERENCE_RETAIL_EXECUTION_ENABLED` via `PermAndPrefUtil.setOrgPref`, controller
    `RetailExecutionEnableController`), narrower projection. Don't claim "5 sub-prefs" when reading
    via CLI — you'll only see 3.
- **Two write transports:**
  - **Dispatcher present:** `RetailExecutionSettings` has **5 separate PATCH setters, not one
    combined call** — `set-retail-execution-enable-setting`, `set-product-hierarchy-pref`,
    `set-visit-sharing-pref`, `set-cgagent-pref`, `set-cgcgen-aipref` (each body
    `{enable:boolean}`). Guards: all need View Setup & Configuration; `set-visit-sharing-pref`
    needs Visit Share Pilot perm on enable=true; the CG-agent/GenAI setters are gated by
    `RetailExecution.userCanUseCGGenAI`. Route base:
    `PATCH /headless/invoke/platform/retail-execution-settings/...`. The batch endpoint harness only
    probes no-param GETs, so these PATCH-with-body routes are structurally un-probed.
  - **Dispatcher-absent (`sf` CLI):** deploy `settings/RetailExecution.settings` (the member takes
    the bare type name `RetailExecution`, no `Settings` suffix) via
    `sf project deploy start --metadata "Settings:RetailExecution"`. Generic `core` MDAPI Settings
    deploy — read pref → write settings file → deploy → re-verify. `sourceApiVersion` must be ≥ the
    field's minApiVersion.
- **Dependent-default side effect:** enabling `enableRetailExecution` also auto-set
  `enableVisitSharing` true (was absent before), even though the deploy file carried only the one
  field. Always re-read after the write; the org may set dependent sub-prefs for you.
- **The advanced-pilot GA gate is a pure dependency, not a blocker:**
  `RetailExecution.orgHasAdvncdRetailExecutionPilot` appears **only** as a Core-source setup-tree
  admission-gate expression — no step in this skill (or its spec) reads or writes it, and it's not an OrgPreference/PSL row,
  so it has no read/write API anywhere. **Base RE enablement does not require it** — it gates only
  *advanced* RE. Report it as a CG Cloud platform / Retail Execution concern only when an
  advanced-RE feature needs it — never as a blocker on the base toggle.

### REST endpoints — the CLI-free path

The `sf` CLI is only sugar over these REST resources. **When the `sf` CLI plugin is not available,
use the REST APIs directly** (any HTTP client with a valid session token — `execute_api` in a
dispatcher context, or a bearer-token `curl`). Same operations, same results.

| Step | REST call | CLI equivalent | Notes |
|---|---|---|---|
| **A1.2** read (Tooling) | **Primary: `GET /tooling/query?q=SELECT+IsRetailExecutionEnabled,IsProductHierarchyEnabled,IsVisitSharingEnabled+FROM+RetailExecutionSettings`** (SOQL projection — returns the values directly). Fallback: the two-call singleton `SELECT Id …` → `GET /tooling/sobjects/RetailExecutionSettings/<id>` | `sf project retrieve start --metadata "Settings:RetailExecution"` | Tooling field names: `Is{RetailExecution,ProductHierarchy,VisitSharing}Enabled`. Prefer the SOQL projection — the singleton `GET /sobjects/RetailExecutionSettings/<id>` can return `UNKNOWN_EXCEPTION` |
| **A1.2** read (dispatcher) | `POST /headless/invoke` (op in body) | — | Dispatcher route only where Headless-360 is provisioned; 404 otherwise |
| **A1.2** write | `POST /metadata/deployRequest` (base64 zip; `checkOnly:true` to dry-run) → poll `GET /metadata/deployRequest/<id>`; repeat `checkOnly:false` for real | `sf project deploy start --metadata "Settings:RetailExecution"` | This is what `sf project deploy` wraps |
| **A1.2** write (unsupported) | `PATCH /tooling/sobjects/RetailExecutionSettings/<id>` `{"IsRetailExecutionEnabled":true}` | — | Settings sObjects reject a direct Tooling PATCH (`METADATA_FIELD_UPDATE_ERROR`) — use the metadata-deploy path instead |

**Field-name drift by transport (same underlying pref, three spellings) — don't cross them:**
dispatcher `is…PrefEnable(d)` · MDAPI Settings `enable…` · Tooling sObject `Is…Enabled`.

**Net:** A1.2 **read** has a clean CLI-free REST path (Tooling GET, works with no dispatcher);
A1.2 **write** is REST too but *only* via `/metadata/deployRequest` (or the dispatcher PATCH where
present) — never a direct Tooling field PATCH.

## Ordering consequence

Namespace gate (A1.1 — package **or** org namespace resolves) → RE enablement (A1.2, the effective
base-provisioning gate) → then anything RE-gated: the RE-flavored install baseline. There is **no
license read** in this ordering — A1.1 is the namespace gate alone, since installing/using the app
is not license-gated. If the sync metadata is absent (neither package nor org namespace resolves) or
RE can't be enabled, the RE-gated steps are reported blocked rather than attempted-and-faked, with
the owner of the missing piece named.
