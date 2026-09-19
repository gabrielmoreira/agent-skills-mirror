---
name: consumer-goods-sync-management-configure
description: "Use this skill to set up Salesforce Consumer Goods (CG) Cloud Mobile Sync end-to-end for the Sync Management App managed package — it runs all three acts in order (Act 1 Setup Sync, Act 2 Assign Users, Act 3 Plan & Verify), not just installing the baseline, so a sales rep can see the day's planned visits offline. Use it when asked to \"set up CG Cloud mobile sync\", \"configure Consumer Goods mobile sync\", \"set up sync for Retail Execution\", \"install the sync baseline\", \"assign a user to the sync configuration\", \"verify the sync setup\", or \"why can't my rep see their planned visits offline\" when sync setup or the baseline install is suspected. DO NOT TRIGGER for general CG Cloud mobile-app troubleshooting unrelated to sync setup, for authoring new or custom sync baselines (this installs only shipped baselines discovered at runtime), or for building or customizing the mobile app UI itself — those are out of scope."
metadata:
  version: "1.0"
  cliTools:
    - tool: ["sf"]
      semver: ">=2.0.0"
---

**Setting up CG Cloud Mobile Sync means running all three acts in order — Act 1 (Setup Sync), Act 2 (Assign Users), Act 3 (Plan & Verify) — NOT just installing the sync artefacts.** Installing the baseline is one step of Act 1; finishing it is not finishing the setup.

Guide an admin/implementer through setting up **Consumer Goods (CG) Cloud Mobile Sync** for a customer org so a sales rep can install the CG Cloud Mobile App and see the day's planned visits **offline**. The moving parts live in the managed package **`Sync Management App`** (its namespace is resolved at runtime — see `ns_prefix` in Session state) plus CG Cloud **core / Retail Execution** settings.

This skill automates as much as a **real** transport can trigger — a Headless-360 / generic-core call (SOQL, sObject REST, Connect, Tooling), an `sf` deploy, or a **`global @RestResource /v1/*`** endpoint in the package. A `public` package method is **not** enough: in a managed package `public` is namespace-private (unreachable from a subscriber org), so only `global`/`webservice`/`@RestResource` members are triggerable. Where neither a generic core capability nor an invokable package action can complete a step, the skill **reports what's needed — and who provides it — and stops that step**; it never fakes a capability.

## Scope & definition of done — READ THIS FIRST

**"Set up CG Cloud mobile sync" / "set up sync for Retail Execution" / "configure Consumer Goods mobile sync" with no narrowing qualifier means run ALL THREE ACTS, in order: Act 1 → Act 2 → Act 3.** It does **not** mean "install the artefacts." If you are about to run only the install for an unqualified request, that is the bug this section prevents — start at Act 1, step 1 (readiness).

**You are NOT done after installing artefacts.** Setup is complete only when **Act 3's end state** is reached (the activated config listed, verified across the four objects, and checked against the baseline files). A run that ends after the install is a *partial* run — say so plainly.

**Act 1 is not "install-only."** It has hard **readiness gates before** the install — the **namespace gate** (A1.1) and **Retail Execution enablement** (A1.2) — and a **verify after** it (A1.4). Installing the baseline into a non-RE-enabled org produces a config that can never sync, so readiness is checked first; a hard miss is **reported-and-stopped**, not written around. The baseline install *is* the sync configuration (the root `Sync_Config__c` and its values come from the baseline CSVs) — there is no separate "create config" step.

**A step the skill can't complete is a stop-*that-step* signal, not stop-the-whole-run.** Report the boundary and **who provides the missing piece** (the CG Cloud platform / Retail Execution, or the org admin), then **continue with every unblocked step.** Only a *hard readiness miss* halts the sequence: the sync metadata absent (neither a package install nor an org namespace resolves), RE cannot be enabled and isn't already on, or — under `Default_IOU` — the target user's missing default mobility IOU.

**The only legitimate subset run** is when the admin's own ask is narrow (e.g. "sync's already installed, just assign Chantelle", "just verify what's activated") — see the routing table. When the ask is unqualified or you are unsure, run the full 1→3.

## The transport contract — every automatable step is `core` or `Sync Management App`

This is the honesty spine. Before running a step, know its transport, and **never fake success for a step no transport can complete:**

- **`core`** — a generic Salesforce / Headless-360 capability: direct SOQL via `execute_api` → `GET /query?q=...`; the CG Cloud core `RetailExecutionSettings` get→set org-preference triad; sObject-REST writes (`POST /services/data/vXX.0/sobjects/<Entity>`); Schema/Tooling **describe** reads.
- **`Sync Management App`** — an action triggered inside the package. The real headless surface is a **`global @RestResource /v1/*`** endpoint, chiefly the three **`/v1/syncconfig/*`** routes: **`/install`** (GET discover + POST install — A1.3), **`/configs`** (GET deployed configs + strategy — A3.1 list), **`/assignment`** (GET/POST/DELETE user→config binding — A2.3). **Not** `Sync Management App`: `public` Apex methods (namespace-private) and Visualforce actions.

**When neither transport can complete a step**, report what's missing, name **who provides it**, and stop that step — do not guess an API name or write around it. The genuine non-automatable points are few: the *advanced*-RE pilot GA gate (A1.2, platform-owned, no API) and IOU-membership **creation** (A2.2, a CG Cloud core / RE task the skill only reads). Deep transport rules: `references/transports-and-namespace.md`.

## Mandatory pre-write plan — state this before your FIRST write

Before you execute a single write (enable RE, install a baseline, create a mapping row), post a short plan that makes your scope decision **explicit and reviewable**:

1. **The full journey is three acts** — Act 1 (Setup Sync), Act 2 (Assign Users), Act 3 (Plan & Verify).
2. **Which acts/sub-acts you will run, and which you will skip** — for every skip, **quote the exact words in the admin's request that narrow the scope** ("the request said 'set up sync'" is NOT a narrowing qualifier); for any step you can't complete, name who provides the missing piece.
3. **The target org**, confirmed explicitly (never silently inherited), and **the resolved `ns_prefix`** you will use for package objects.
4. **Where you will start.** For an unqualified request this is Act 1, step 1 (readiness: namespace + RE) — never the install.
5. **Persist this plan to `report.md`** in the working directory — writing that file is the very first action you take, before any org write. Append each Act's outcome (steps run, transport tag, read-back result, blocked steps) as you complete it, and write a final verdict at the end. This file — not the chat transcript — is the run's deliverable; it must exist even if the run stops early. Contract: "Write the run report to disk" in `references/verify-and-smoke.md`.

## Entry point — route on the admin's actual ask

**Default rule:** unless the ask *explicitly narrows the scope*, treat it as the full setup and **run Acts 1→2→3 in order.** When in doubt, run the full journey.

| Signal | Where to start |
|---|---|
| **"Set up CG Cloud mobile sync" / "set up sync for Retail Execution" / no narrowing qualifier / no prior state** | **Run the FULL journey: confirm org + resolve namespace, then Act 1 step 1 (readiness: namespace + RE), then Acts 1→2→3. NOT "just install." Not done until Act 3's end state.** |
| "Sync's already installed, I just need to assign a user" | Narrow → Act 2. First read back the installed config (Act 3 list step) to confirm a config is deployed before binding a user. |
| "Just install the Retail Execution baseline" | Narrow → Act 1 A1.3 only, **after** confirming A1.1/A1.2 readiness **and** explicit confirmation of which baseline. GET `/v1/syncconfig/install` to discover, then POST to install. Never hand-roll via raw sObject inserts. Report the skipped steps (A1.4, Acts 2–3) as not-done. |
| "Just verify / list what's activated" | Act 3. Read-only; no writes. |
| "Enable Retail Execution" | A1.2 only. CG Cloud **core**, a working `core` write; only *advanced*-RE hits the platform-owned pilot gate (no API). |

## Session state (track across the conversation)

- `target_org_alias` — the org being configured; confirmed explicitly before any write.
- `ns_prefix` — namespace prefix (with trailing `__`), **discovered at runtime** by A1.1 (never hardcoded), resolved once and used for every package-object path. Two sources: the installed managed package (`InstalledSubscriberPackage.NamespacePrefix`) or the org's own registered namespace (`Organization.NamespacePrefix`, source-deployed DE/packaging org).
- `api_version` — the Salesforce REST API version for raw-HTTP URLs. **Never hardcode.** Resolve once via `GET /services/data`, take the highest `version`. `execute_api` calls are versionless.
- `org_ready` — bool; true when A1.1's namespace gate passes AND A1.2 (RE enabled) passes. A hard miss on either halts the run.
- `installed_config_id` / `installed_version` — from the baseline install (A1.3). The install *is* the config — no separate "config created" flag.
- `act1_complete`, `act2_complete`, `act3_complete` — bool per Act; run strictly 1→2→3. For an unqualified request, all three must be `true` (minus reported non-automatable steps) before reporting complete.
- `resolution_strategy` — the config root's `Business_Area_Resolution_Strategy__c` (`Default_IOU` vs `Custom_User_Field`); decides whether A2.3 is IOU-implicit (via A2.2) or an explicit mapping write.
- `blocked_steps` — running list of steps the skill could not complete, each with the boundary and who provides the missing piece.
- `report_path` — the run's **deliverable on disk**: a `report.md` in the working directory. Created **before the first org write** (starting with the pre-write plan) and appended at each Act boundary, so a partial or interrupted run still leaves a faithful record. Reporting only in chat does **not** satisfy this — the record must exist as a file.

## Per-sub-act transport map (compact)

Single source of truth for which transport each step uses. **Full detail (API names, fallbacks, owners): `references/transports-and-namespace.md`, `references/readiness-and-enablement.md`, `references/sync-management-app-install-backbone.md`, `references/verify-and-smoke.md`.**

| Sub-act | Requirement | Transport | Note |
|---|---|---|---|
| A1.1 | Verify sync metadata present + resolve namespace (hard prereq) | `core` | **The namespace gate is the only hard stop here** (Tooling `InstalledSubscriberPackage` → else `Organization.NamespacePrefix`). No license read (install isn't license-gated) and **no permission-set-existence check** (perm-set names can be renamed/folded). |
| A1.2 | Enable Retail Execution | `core` | Read+write via `RetailExecutionSettings` (dispatcher, 5 prefs) or MDAPI `Settings:RetailExecution` (3 booleans). Only *advanced*-RE hits the pilot GA gate (no API); base toggle is unaffected. |
| A1.3 | Install the sync config (baseline root + sub-configs), with confirmation | `Sync Management App` | `SyncConfigInstallEndpoint` `/v1/syncconfig/install`: GET `discoverConfigs`, POST `installConfig`. Baselines discovered at runtime — never hardcoded. **The install *is* the config.** Never hand-roll via raw inserts. |
| A1.4 | Verify referenced field-set definitions exist per tracked object | `core` (read-only describe) | Names installed by the CSV; definitions (e.g. `RetailMobilityRelevant`) provisioned by RE, not the package. Missing set → report-and-stop, owner = RE provisioning. |
| A2.1 | Verify target user exists | `core` | `User` SOQL via `execute_api`. |
| A2.2 | Confirm user's Mobility IOU membership | `core` read-only precondition (`Default_IOU` only) | Reads `InternalOrgUnitUser` (`IsDfltMobIntrOrgUnit = true`); never writes IOU membership. No row under `Default_IOU` → report-and-stop. Skipped under `Custom_User_Field`. |
| A2.3 | Assign user to the installed config | `Sync Management App` / IOU-implicit → A2.2 | `SyncConfigAssignmentEndpoint` `/v1/syncconfig/assignment` (GET/POST/DELETE). **Not** `core`: a raw write corrupts the overloaded `Business_Area_Name__c`. |
| A3.1 | List + verify activated config across the 4 objects | `Sync Management App` (list) + `core` (counts) | `SyncConfigListEndpoint` `/v1/syncconfig/configs`; all four `COUNT()`s in **one batched anon-Apex call** (not a per-object `sf data query` loop). **No `/v1/syncconfig/verify` — record counts ARE the verification.** |
| A3.2 | Verify against baseline static-resource files | `core` | Compare installed per-object counts to the installed baseline's own declared counts, derived at runtime — never hardcoded. |

## Act 1 of 3 — Setup Sync

> Readiness gates **before** the install, a cheap **landing check after** it — the full per-object verification is Act 3's, not repeated here. Installing the baseline is the middle sub-step, not the whole act.

1. **A1.1 — Verify sync metadata present, resolve namespace.** `core`. Confirm the sync objects exist and resolve `ns_prefix` (package via Tooling `InstalledSubscriberPackage`, else `Organization.NamespacePrefix`). **Hard miss (stop) only when NEITHER resolves.** Installing the package is not license-gated, so there is no license read here — and **do not verify any permission set by name** (perm-set names can be renamed/folded). The real Act-1 readiness gates are exactly two: metadata-present (this step) and RE-enabled (A1.2).
2. **A1.2 — Enable Retail Execution.** `core` read + `core` write. Read via `RetailExecutionSettings` (dispatcher) or MDAPI `Settings:RetailExecution`; enable via the dispatcher's PATCH setters or `sf project deploy start --metadata "Settings:RetailExecution"` (false→true, re-read to confirm). RE-enabling implies base provisioning. The advanced-pilot toggle (`orgHasAdvncdRetailExecutionPilot`) has no API and gates only *advanced* RE.
3. **A1.3 — Install the sync configuration into the four objects.** `Sync Management App`. GET `discoverConfigs` (runtime discovery — no config named "Standard"), then **POST only on the admin's explicit OK** after presenting the chosen baseline and its manifest-derived per-object counts. Sub-configs = child baselines; `parentConfigId` comes from the manifest, enforcing parent-before-child. Never hand-roll via raw sObject inserts. On `SUCCESS`, confirm landing with the cheap **aggregate** check only — one **batched anon-Apex call** for all four `core` COUNT()s (never a per-object `sf data query` loop; cold-starts blow the timeout), sum == `InstallResponse.recordsInserted`, no manifest fetch — **not** Act 3's per-object comparison.
4. **A1.4 — Verify the referenced field-set definitions exist.** `core` read-only describe — **not a deploy.** The sync query-field path throws on a missing set (hard fail at first sync), so verify per tracked object; any missing → report-and-stop, owner = RE provisioning.

**Act 1 end state:** package present (gate passed) and RE-enabled (or the miss reported and run halted); the admin-confirmed baseline installed across the four objects after explicit confirmation (`installed_config_id`/`installed_version` captured), landing confirmed by the aggregate `COUNT()==recordsInserted` check (the per-object baseline verification is Act 3's); referenced field-set definitions verified present. Full detail: `references/act1-setup-sync.md`.

## Act 2 of 3 — Assign Users to the Sync Configuration

> Runs after Act 1 (binds a user to the config Act 1 installed). Detect the config root's resolution strategy before choosing the A2.3 transport.

1. **A2.1 — Verify the target user exists.** `core`. `User` SOQL via `execute_api`.
2. **A2.2 — Confirm the user's Mobility IOU membership.** `core` read-only precondition, **`Default_IOU` only.** Read the default mobility IOU (`IsDfltMobIntrOrgUnit = true`); carry `iouId` into A2.3, or **report-and-stop if none** (the skill does not create IOU membership). **Skip entirely under `Custom_User_Field`** — do not generalize into a blanket "no IOU ⇒ stop."
3. **A2.3 — Assign the user to the config.** `Sync Management App` (mapping row) / `core` (IOU-implicit). An assignment binds a User (`005`), Role (`00E`), OR Profile (`00e`); a Role/Profile row binds a whole cohort. Pick the config via `GET /v1/syncconfig/configs`, resolve name→Id, and scope by strategy (`Default_IOU` → `iouId`; `Custom_User_Field` → `businessArea` picklist). POST to `/v1/syncconfig/assignment`, then GET read-back — confirm the returned short canonical `clientAppId`. Re-assignment is an **upsert**: GET first; a duplicate `(configPath, businessArea, mappedRecordId)` triple is rejected; move a binding = DELETE the old row then POST. **Never write `Sync_Client_App_Profile_Mapping__c` raw** — the endpoint must derive the overloaded `Business_Area_Name__c`.

**Act 2 end state:** target user confirmed; under `Default_IOU`, default mobility IOU confirmed (or reported-and-stopped); the user bound to the installed config, verified by read-back. Full detail: `references/act2-assign-users.md`.

## Act 3 of 3 — Plan & Verify

> The final act — the **authoritative** verification (Act 1 ran only a cheap aggregate landing check; the per-object comparison happens here, once). For an unqualified setup you must reach this act's end state — do not stop after the install.

1. **A3.1 — List + verify the activated config across the four objects.** `Sync Management App` (list) + `core` (counts). List deployed configs + strategy via `GET /v1/syncconfig/configs` (a `core` SOQL list is an equivalent fallback). Get all counts via **one batched anon-Apex `COUNT()` call** across the four sync objects + `Sync_Config_State__c` (custom settings) — not a per-object `sf data query` loop (cold-starts blow the timeout). **No `/v1/syncconfig/verify` — record counts ARE the verification.**
2. **A3.2 — Verify against the baseline static-resource files.** `core`. Compare installed **per-object** counts to the installed baseline's own declared counts, derived at runtime (identify the baseline from the activated config / version captured in A1.3) — this per-object split is A3.2's job (the aggregate total was Act 1's landing check); it catches a right-total / wrong-distribution install. **Do not hardcode counts** — they vary by baseline.

**Act 3 end state:** the activated config listed via `/v1/syncconfig/configs` and verified across the four objects (+ state) through `core` SOQL record counts, each matched against the baseline's own declared count. Full detail: `references/act3-plan-verify.md`.

## Definition of done (the whole skill)

An unqualified CG Cloud mobile sync setup is **complete only when all three Acts reach their end states**, with any step the skill couldn't complete explicitly reported and attributed to who provides the missing piece: Act 1 (org ready; admin-confirmed baseline installed; field-set definitions verified — or missing set reported-and-stopped) → Act 2 (user exists; under `Default_IOU` the default mobility IOU confirmed — or reported-and-stopped; config bound) → Act 3 (activated config listed + verified against baseline files via `core` SOQL counts). **Reporting "done" after only the install (A1.3) is a defect.** Close with an explicit list of what remains and who provides each missing piece.

## Out of scope / deferred

Reported to set expectations, not reasons to halt the Act sequence:

- Removal / GA-gating of the `orgHasAdvncdRetailExecutionPilot` admission toggle — CG Cloud core (Retail Execution); no API anywhere (A1.2).
- Authoring **new/custom** baselines beyond those shipped (discovered at runtime) — manual ZIP (manifest + CSV) authoring outside this skill.
- **Creating** Mobility IOU membership (A2.2) — a CG Cloud core / RE task; the skill only reads it.

## Companion references

- `references/act1-setup-sync.md`, `references/act2-assign-users.md`, `references/act3-plan-verify.md` — standalone per-Act breakdowns.
- `references/transports-and-namespace.md` — the transport & namespace rules and the `sf` CLI cookbook.
- `references/readiness-and-enablement.md` — the namespace gate & RE-enablement detail.
- `references/sync-management-app-install-backbone.md` — the Sync Management App install backbone.
- `references/verify-and-smoke.md` — the verify & smoke-test patterns.
- `examples/scenarios.md` — worked validation scenarios (correct vs. anti-pattern runs).
