# Act 3 of 3 — Plan & Verify

Part of the [`consumer-goods-sync-management-configure`](../SKILL.md) skill — the **third and final act**.
Runs after [Act 1](act1-setup-sync.md) (install) and [Act 2](act2-assign-users.md)
(assignment). For an unqualified "set up sync" request you must reach this Act's end state —
finishing the install is not finishing the setup.

**This Act is read + assert (no writes).** It lists the activated config, verifies it across
the four objects, and checks it against the baseline files. **This is the authoritative
verification** — Act 1's post-install step ran only the cheap **aggregate** landing check (sum of
the four counts == `InstallResponse.recordsInserted`, no manifest fetch); the **per-object** count
comparison against the baseline manifest (A3.2) happens **here, once** — Act 1 deliberately does
not run it, so the two acts do not duplicate each other.

## What this Act does

### 1. A3.1 — List + verify the activated config across the four objects — **`Sync Management App` (list) + `core` (counts)**

- **List the deployed configs via the `Sync Management App` endpoint.** `GET /v1/syncconfig/configs`
  (`SyncConfigListEndpoint`) returns every deployed `Sync_Config__c` as
  `{name, clientAppId, resolutionStrategy}` in one package-blessed call — the source of truth for
  *which* configs are activated and each one's Business Area Resolution Strategy. This is also the
  discovery step Act 2's explicit assignment (A2.3) consumes: the `name` it returns is the
  `configPath` the assignment endpoint expects. This is the supported list surface (a `core` SOQL
  list — see below — is an equivalent fallback for reading deployed configs).
- **Get per-object counts + installed version via generic `core` reads — works today, no package
  change.** The four sync objects + `Sync_Config_State__c` are **List custom settings**, so they're
  queryable via generic SOQL. **Batch all five `COUNT()`s into ONE anonymous-Apex call that
  `System.debug`s a JSON blob — do NOT loop `sf data query` per object.** Each `sf` cold-start is
  ~15–20s, so a 4–5-object loop blows the 2-min timeout; one `sf apex run` returns every count in a
  single invocation (see the batched form + the **grep `USER_DEBUG` first** parse rule in
  [transports-and-namespace.md](transports-and-namespace.md) — `sf apex run` echoes the block as
  `Execute Anonymous:` source, so a bare marker grep matches twice). A single
  `GET /query?q=SELECT COUNT() FROM <ns>Sync_Config__c` via `execute_api` is fine only for a one-off
  read. Return row counts + keys + installed `configId`/`version` in one summary. **This covers the
  count/verify half** — it is **not** blocked.
- **What does *not* work (and why):** the package's own state readers
  `SyncConfigOrchestrator.buildStateMap()` / `readCurrentVersion()` are **`public static`,
  unannotated** (and their internal helper `installedVersionMap()` is **`private static`**) —
  either way namespace-private, so **not** callable via anonymous Apex or REST from a subscriber org
  (a `private` member is even less reachable than a `public` one). `BatchSoqlEndpoint` (`/v1/batchsoql`) is gated by
  `isClientAppIdAvailable()` (needs a pre-existing `Sync_Config__c`). So the package's
  *purpose-built* count/version reader isn't reachable — but generic core SOQL covers the need.
- **No additional Sync Management App call is needed for A3.1 — record counts ARE the verification.** The
  per-object `core` COUNT() reads above are the complete, intended verification method (the objects
  are custom settings, directly queryable). Do **not** propose, wait on, or build a
  `/v1/syncconfig/verify` endpoint — Act 3 adds **no** Sync Management App calls; verification is done through
  record counts, full stop, not a workaround for a missing surface. The package's `public static`
  state readers being namespace-private is therefore moot — their output (counts + version) is
  already covered by generic `core` SOQL.
- **Adopt the verify-step convention** when documenting the result — end the workflow with
  an explicit assert step (a distinct step with `id: verify`, a read `api`, and an `assert:` predicate).
  **Assert against the installed baseline's own
  expected count — never a hardcoded literal** (`<expected>` is resolved at runtime per the bullet
  below; it varies by which baseline was installed):
  ```yaml
  - id: verify
    description: "Confirm activated sync config"
    api: "GET /query?q=SELECT COUNT() FROM <ns>Sync_Tracked_Object_Config__c"
    assert: "count == <expected tracked-object count for the installed baseline>"
  ```

### 2. A3.2 — Verify against the baseline static-resource files — `core`

- **Baseline count check (record counts only — the intended verification):**
  1. **Derive the expected per-object counts from the installed baseline — do NOT hardcode them.**
     The expected numbers depend on *which* baseline was installed (a different baseline, or a newer
     release of the same one, has different counts), so resolve them at runtime, not from literals in
     this doc:
     - Identify the installed baseline from the activated config (the `staticResourceName`/version
       captured at **install time** in Act 1's A1.3 — carry it forward in session state — or the
       installed `configId`/`version` read back in A3.1).
     - Read that baseline's own manifest/CSVs (the installed baseline's static-resource name came
       from the discovery endpoint / the install captured in A1.3) and count the
       rows it declares per object — that row count **is** the expected value. The per-object numbers
       differ by edition and release, so **derive them from the installed baseline's manifest at
       runtime — never assert against a constant in this doc.**
  2. Get the installed counts from A3.1's `core` COUNT() reads.
  3. Report a single pass / fail verdict per object: installed count == the installed baseline's
     declared count.
  - **Verification is through record counts.** The count comparison against the installed baseline
    is the complete server-side check — a count match confirms the config's artefacts installed as
    that baseline specifies.
  - **These reads hit Core directly, bypassing the package dispatcher** — the same generic `core`
    SOQL A3.1 runs (the **batched anon-Apex `COUNT()` call**); A3.2 **reuses those counts** rather
    than re-querying per object.
  - **No Sync Management App work here.** There is no `/v1/syncconfig/verify` (or `mode=smoke`) proposal — Act 3
    adds no calls to the package; counts cover the need.
- **A green count check proves the server side installed the baseline's artefacts — say exactly
  what was verified.** Matching counts confirm the cloud-side install; report the verification as a
  server-side count check so no one reads a green count as more than that.

## Act 3 end state

- Activated config **listed** via the `/v1/syncconfig/configs` `Sync Management App` endpoint (deployed configs +
  strategy) and **verified** across the four objects + `Sync_Config_State__c` **through per-object
  record counts** via generic `core` SOQL (the objects are custom settings). Act 3 requires **no new
  Sync Management App call** — counts are the verification.
- **Baseline count check** run: installed per-object counts match the **installed baseline's own
  declared counts** (derived at runtime from that baseline's manifest/CSVs — not hardcoded) — or the
  discrepancy reported.

## Gotchas

- **The package's config *count/version* readers are namespace-private, but you don't need them.**
  They're `public static` (unreachable headlessly) — but the four objects are **custom settings**,
  so generic `core` SOQL reads them today. Listing the deployed
  configs + strategy has a blessed surface (`/v1/syncconfig/configs`). No further Sync Management
  App endpoint is needed for Act 3 — verification is record counts via `core` SOQL, and that is the
  intended method, not a workaround.
- **A green count check proves the server side installed the baseline's artefacts.** Matching
  record counts confirm the cloud-side install. Say exactly what was verified — report it as a
  server-side count check, nothing more.
