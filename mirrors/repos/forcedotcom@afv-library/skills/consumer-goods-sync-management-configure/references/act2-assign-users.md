# Act 2 of 3 — Assign Users to the Sync Configuration

Part of the [`consumer-goods-sync-management-configure`](../SKILL.md) skill — the **second of three acts**.
Runs after [Act 1](act1-setup-sync.md) (it binds a user to the config Act 1
installed — the admin-confirmed baseline root, e.g. the Retail Execution baseline); followed by
[Act 3](act3-plan-verify.md).

**This Act verifies, checks a precondition, then writes.** It verifies the user (read), confirms
the user's IOU membership (read — a **precondition**, not a write; the package doesn't own IOU
membership and this skill does **not** create it), then writes the config assignment. **The IOU
precondition (A2.2) only matters under the `Default_IOU` strategy** — see below.

**Detect the resolution strategy first, because it decides whether the IOU precondition even
applies.** Read the target config root's `Business_Area_Resolution_Strategy__c` (via
`GET /v1/syncconfig/configs`). The runtime resolver (`ClientAppMapperService.mapClientApp`) picks
the root *by strategy, gated on IOU presence*, then resolves the binding **User → Role → Profile**
from the mapping rows:
- **`Custom_User_Field` (the default strategy) — no IOU needed.** This root is selected for
  users **without** a default mobility IOU, and the binding is resolved entirely from the
  `Sync_Client_App_Profile_Mapping__c` rows. So a **Role (00E)** or **Profile (00e)** mapping —
  written by A2.3's endpoint — binds every user with that role/profile in one shot, with **no IOU
  membership involved at all**. A2.2 does not apply here — skip it.
- **`Default_IOU` — IOU membership is the binding, and it's a precondition.** This root is selected
  **only** for users who *have* a default mobility IOU, so that membership is what routes them.
  **This skill reads it, it does not create it:** if the user already has a default mobility IOU,
  proceed; **if the user has no IOU membership, report and stop** — there are no further steps, and
  the skill does **not** write IOU membership (that's a CG Cloud core / RE concern). A Role/Profile
  mapping alone won't rescue an IOU-less user, because this root isn't even evaluated for them.

**A missing default mobility IOU is a stop *only* under `Default_IOU` — never under
`Custom_User_Field`.** Under `Custom_User_Field` the strategy doesn't route by IOU at all, so a user
without one is **not** blocked: they bind through the mapping row with the **all-scope default**
(`businessArea` = `'All'`, i.e. all business areas — the `Custom_User_Field` analog of "all IOUs").
Only under `Default_IOU`, where the IOU *is* the binding, does an absent IOU leave nothing to bind —
so report-and-stop applies **there and only there**. Do not generalize the `Default_IOU` stop into a
blanket "no IOU ⇒ stop" rule; that would wrongly halt every `Custom_User_Field` assignment.

Choosing the wrong path produces a user who "looks assigned" but whose app resolves no config.

## What this Act does

### 1. A2.1 — Verify the target user exists — `core`

- Generic SOQL via `execute_api`:
  `GET /query?q=SELECT Id, Name, IsActive, Profile.Name FROM User
  WHERE Name = '<name>'` (or by username/email — prefer a unique key). **Versionless** — the
  `execute_api` transport supplies the `/services/data/<api_version>/` base itself (see the
  orchestrator's session state); don't pin a version into a `core` call. This is a
  first-class `purpose: validate` pre-flight query, **not** a bespoke API. `User` is a core object —
  namespace is irrelevant.
- No package code needed. Report the resolved `User.Id` (and `IsActive`) into session state;
  if the user doesn't exist or is inactive, stop and report — don't assign into a phantom.

### 2. A2.2 — Confirm the user's Mobility IOU membership — `core` (read-only precondition)

- **Package boundary:** `Sync Management App` only **reads** `InternalOrgUnitUser` /
  `InternalOrganizationUnit` — `ClientAppMapperService` queries the user's default mobility IOU
  (`IsDfltMobIntrOrgUnit = true`) to route them to a `core`-mode `Sync_Config` root, and is
  written (dynamic SOQL + `QueryException` catch) to even *compile* in pure managed-package
  orgs where `InternalOrgUnitUser` doesn't exist. It **never writes** IOU membership, and
  **neither does this skill** — IOU membership is a CG Cloud **core Retail Execution** concern,
  provisioned outside this flow.
- **Under `Custom_User_Field` (the default) — skip this step entirely.** The binding is resolved
  from the `Sync_Client_App_Profile_Mapping__c` row with no IOU involved, so there is nothing to
  check here; go straight to A2.3. A user with **no** default mobility IOU is **not** a blocker under
  this strategy — the mapping row binds them with the all-scope default (`businessArea` = `'All'`).
  The "report and stop on a missing IOU" rule below is **`Default_IOU`-only**.
- **Under `Default_IOU` — check the membership as a precondition (read-only):** run the same query
  `ClientAppMapperService.getDefaultIouId()` uses —
  `SELECT InternalOrganizationUnitId FROM InternalOrgUnitUser WHERE UserId = :userId AND
  IsDfltMobIntrOrgUnit = true LIMIT 1` (`core`; `InternalOrgUnitUser` is a core RE object, no
  namespace prefix).
  - **If it returns a row:** the user has a default mobility IOU — carry that
    `InternalOrganizationUnitId` forward (it's the `iouId` scope A2.3 needs) and proceed.
  - **If it returns no row:** the user has **no** Mobility IOU membership — **report and stop.**
    Under `Default_IOU` the config root isn't even evaluated for an IOU-less user, so there is
    nothing further to do: do **not** attempt to create IOU membership, and do **not** proceed to
    A2.3. Say plainly that the user must be given a default mobility IOU (a core / RE task) before
    sync assignment can continue.
  - **In a pure managed-package org** the query throws `QueryException` (the object is absent); the
    package treats that as the MP path (`null`) — degrade the same way rather than hard-failing.

### 3. A2.3 — Assign the user to the sync configuration installed in Act 1 — `Sync Management App` (mapping row) / `core` (IOU-implicit)

**An assignment binds a User, a Role, OR a Profile to the config** — `mappedRecordId`'s key-prefix
picks which (`005` = User, `00E` = Role, `00e` = Profile), and the runtime resolver matches in
priority **User → Role → Profile**. A **Role or Profile** mapping is the high-leverage choice: one
row binds everyone with that role/profile, no per-user write. Two paths, chosen by the
`resolution_strategy` you detected up front:

#### A2.3 elicitation flow (admin-facing) — what to gather, in order

When an admin says "assign the Sync config to a profile / role / user," walk this flow. The
endpoint (`POST /v1/syncconfig/assignment`) takes a resolved **Id** in `mappedRecordId`
(`005`=User, `00E`=Role, `00e`=Profile) — never a name — so every "name" the admin gives is
**resolved to an Id via a `core` SOQL** before the call. Do not skip a confirmation to save a
round-trip: a wrong config name or an unresolved profile silently produces a no-op binding.

1. **Establish the Config to assign to.**
   - If the admin **didn't name a config**, list the deployed ones — `GET /v1/syncconfig/configs`
     (`SyncConfigListEndpoint`) returns `{name, clientAppId, resolutionStrategy}` — and present the
     **`name`** values for the admin to pick. Do not guess.
   - If the admin **named a config**, confirm it's actually deployed: match the name against
     `/configs`. If it's not there, say so and stop (nothing to bind to) — offer the deployed list.
   - Carry forward the chosen config's **`name`** (→ `configPath`) **and** its
     `resolutionStrategy` — the strategy decides whether the second field is an **IOU** (`iouId`,
     `Default_IOU`) or a **Business Area** (`businessArea`, `Custom_User_Field`). `name` ≠
     `clientAppId`; pass the `name`.
2. **Identify the mapping option: Profile, Role, or User.** Ask the admin if it's not stated.
3. **Resolve the target name → Id and gather the scope, per option:**
   - **Profile:** get the profile name; if the admin didn't give one, list available profiles
     (`SELECT Id, Name FROM Profile ORDER BY Name`) and ask. Resolve the name → **`00e` Id**
     (`SELECT Id FROM Profile WHERE Name = '<name>'`). Gather the scope (IOU/Business Area — see
     below). Invoke the endpoint with the `00e` Id as `mappedRecordId`.
   - **Role:** get the role name; if not given, list available roles
     (`SELECT Id, Name FROM UserRole ORDER BY Name`) and ask. Resolve the name → **`00E` Id**.
     Gather the scope. Invoke with the `00E` Id as `mappedRecordId`.
   - *Grounding & core-vs-Sync Management App:* these mirror the package's own list fetchers —
     `ClientProfileEditExtension.getProfileIds()` (`SELECT Id, Name FROM Profile`) and
     `getRoleIds()` (`SELECT Id, Name FROM UserRole`) — but `Profile`/`UserRole` are standard
     platform objects (no namespace prefix) and those accessors are VF-controller/`protected`
     (namespace-private, not headless-reachable), so the agent runs the SOQL **directly as `core`**,
     exactly like the IOU reads. Both require the caller to have **view access** on the object.
   - *Role name nuance:* pass the resolved **Id** forward, not the picked name. The service derives
     the persisted mapping-row name itself — and for **roles it uses `DeveloperName`** (the API
     name), not the display `Name` you listed (`SyncConfigAssignmentService.buildRecordName`);
     profiles use `Name` for both. Passing the Id avoids the display-vs-API-name mismatch.
   - **User:** identify the user and get the **`005` Id** from the org
     (`SELECT Id, IsActive FROM User WHERE Username/Email/Name = '<value>'` — reuse A2.1). **If the
     user isn't in the org, inform the admin and stop** — do not bind a phantom. Under `Default_IOU`,
     the user's default mobility IOU was already confirmed in **A2.2** (the precondition check): pass
     that confirmed `InternalOrganizationUnitId` as the scope (`iouId`). Invoke with the `005` Id as
     `mappedRecordId`. (A2.2's read used the exact query `ClientAppMapperService.getDefaultIouId()`
     runs: `SELECT InternalOrganizationUnitId FROM InternalOrgUnitUser WHERE UserId = :userId AND
     IsDfltMobIntrOrgUnit = true LIMIT 1`.)
     - *`IsDfltMobIntrOrgUnit = true` is load-bearing:* it matches **only** the user's *default
       mobility* IOU. A secondary/non-default IOU the user belongs to is deliberately **not**
       matched (the resolver routes such users via the MP path), so do **not** substitute another
       IOU row.
     - *No default mobility IOU → already stopped in A2.2:* if the user had no such membership, the
       A2.2 precondition already reported-and-stopped under `Default_IOU`, so you never reach this
       write. This skill does not create IOU membership to unblock it.
4. **The "scope" field is strategy-dependent — this is the key reconciliation:**
   - Under **`Default_IOU`**, the admin's "IOU" is passed as **`iouId`** (the InternalOrganizationUnit
     Id). For the **User** path this is exactly the IOU fetched from `InternalOrgUnitUser` in step 3.
     For **Profile/Role**, there is no single user to derive it from, so **list the org's IOUs and
     ask** — `SELECT Id, OrganizationCode, OrganizationName FROM InternalOrganizationUnit ORDER BY
     OrganizationCode` (present **`OrganizationName` alongside `OrganizationCode`** so the admin can
     identify the right record — a bare code like `IOU-001` is hard to recognize; the admin's pick →
     `iouId`; blank = all IOUs). The package's own `ClientProfileEditExtension.getIouOptions()`
     selects only `OrganizationCode` for its VF label; add `OrganizationName` here for the
     admin-facing pick. **Both IOU
     reads are `core`, not `Sync Management App`** — `InternalOrgUnitUser` and `InternalOrganizationUnit` are CG
     Cloud core RE objects (no namespace prefix), and the package's IOU accessors are
     VF-controller/`protected` (namespace-private, not headless-reachable), so the agent runs the
     SOQL directly. In a **pure managed-package org** these objects don't exist — the query throws
     `QueryException` (the package catches it and degrades to "All"); the agent should treat a
     missing-object error the same way, not as a hard failure.
     - *Object confusion to avoid:* `InternalOrganizationUnit` = the IOU **record** (carries
       `OrganizationCode`, what you *list from*); `InternalOrgUnitUser` = the user↔IOU **junction**
       (carries `IsDfltMobIntrOrgUnit`, what you query for *one user's default*).
   - Under **`Custom_User_Field`** (the default), there is **no IOU** — the second field is a
     **Business Area picklist value** passed as **`businessArea`** (blank / `'All'` = all areas).
     So "assign to profile X with IOU Y" under this strategy means: bind profile X, and Y is a
     Business Area value, not an IOU. If the admin insists on an IOU under `Custom_User_Field`, that
     signals the config's strategy doesn't match the request — surface the mismatch rather than
     stuffing an IOU Id into `businessArea`.
5. **Invoke and verify.** `POST /v1/syncconfig/assignment` with the body in step (a).2 below, then
   read back with `GET /v1/syncconfig/assignment?configId=<config name>`.
   - **On failure, report and STOP.** If the POST returns a failure status (or throws), surface the
     error message to the admin and **halt — no read-back, no further processing.** A failure body
     inside an HTTP 200 is still a failure; never treat it as success and never fall back to a raw
     `Sync_Client_App_Profile_Mapping__c` write to "recover." In particular an **unknown/unresolvable
     `configPath` is a hard rejection** (the endpoint throws — it no longer round-trips the value or
     silently defaults the strategy to `Custom_User_Field`), so a bad config name fails loudly here
     rather than writing a mis-keyed row: confirm the config is in the `/configs` list before POSTing.
     Only a success response proceeds to the read-back.

The mechanics of each transport path:

- **(a) `Custom_User_Field` (the default) — a mapping-row write via the `Sync Management App` endpoint, NO IOU
  needed.** The binding is resolved entirely from the `Sync_Client_App_Profile_Mapping__c` row, so
  write a **User/Role/Profile** row through `SyncConfigAssignmentEndpoint` and you're done — **A2.2
  is not on the critical path here.** Steps:
  1. **Pick the config.** `GET /v1/syncconfig/configs` (`SyncConfigListEndpoint`) lists the
     deployed configs as `{name, clientAppId, resolutionStrategy}`. Pass the config's **`name`** (or
     its `clientAppId`) as `configPath` — the endpoint accepts **either** and normalises to the
     canonical `clientAppId` before storing (see the `configPath` note below). The **stored** row is
     always keyed by `clientAppId`, which is what the admin **Assignments page** displays.
  2. **Assign.** `POST /v1/syncconfig/assignment` with
     `{"req":{"configPath":"<config name or clientAppId>","mappedRecordId":"<005|00E|00e id>","businessArea":"<value or 'All'>"}}`.
     Pass a **Role (`00E`)** or **Profile (`00e`)** id to bind by role/profile; a **User (`005`)** id
     to bind one user. `mappedRecordId`'s key-prefix picks the type automatically.
  3. **Verify by read-back.** `GET /v1/syncconfig/assignment?configId=<name or clientAppId>` returns
     the row with the resolved target name and the stored `businessAreaStored`/`resolutionStrategy`.
     The returned `clientAppId`/`clientAppProfile` are the **canonical** short `clientAppId` (not
     the config's longer custom-setting `name`); confirm they match, since that canonical value is
     what makes the row appear on the admin Assignments page (which filters by `clientAppId`). For
     example, passing a config `name` like `<AppId>__Default` as `configPath` stores the short
     `clientAppId` `<AppId>`, and the row is visible on that app's Assignments page.
- **(b) `Default_IOU` — IOU-implicit; gated on the A2.2 precondition.** This root is selected
  **only** for users with a default mobility IOU, so the user is bound via that IOU, not a
  standalone mapping row. **A2.2 must have already confirmed the membership** — if the user had no
  default mobility IOU, A2.2 already reported-and-stopped and you never reach here. Given the
  confirmed membership, verify by re-reading it and confirming `ClientAppMapperService`'s route
  resolves to the installed config root. (A Role/Profile row alone won't bind an IOU-less user here, because
  this root isn't evaluated for them.) When you do write a row under this strategy, pass
  `"iouId":"<id>"` (the IOU confirmed in A2.2) instead of `businessArea` so the endpoint stores the
  IOU id correctly.
- **Why NOT a raw `POST /sobjects/<ns>Sync_Client_App_Profile_Mapping__c`:** the mapping's
  `Business_Area_Name__c` field is **overloaded** — it holds an InternalOrganizationUnit **Id**
  under the `Default_IOU` strategy but a Business Area **picklist value** under
  `Custom_User_Field`. A raw sObject write that doesn't derive this from the config's
  `Business_Area_Resolution_Strategy__c` **silently corrupts the field**, and also skips the
  cross-config duplicate check and the unique-Name convention. The endpoint centralizes all three
  (it's the same `SyncConfigAssignmentService` the VF `ClientProfileEditExtension.Save()` uses), so
  the headless agent and the admin UI produce identical rows. This is why A2.3's explicit path is
  **`Sync Management App`, not `core`** — the raw-sObject shortcut is unsafe.
- **Use the endpoint, never a raw write.** The assignment + configs endpoints are the supported
  path here — never fall back to a raw `Sync_Client_App_Profile_Mapping__c` write (it corrupts the
  overloaded `Business_Area_Name__c` and skips dedup + the unique-Name convention).

#### A2.3 re-assignment, update & removal — upsert semantics (do this, don't guess)

The POST is an **upsert**, and re-binding an already-mapped user/role/profile is a first-class
case — not the same call twice. Get it wrong and you either hit a duplicate error or write a second
conflicting row. The rules the endpoint enforces server-side (`SyncConfigAssignmentService`):

- **Create vs. update is decided by the `recordId` param, not by the config.** The POST body
  carries an optional **`recordId`** (an *existing* `Sync_Client_App_Profile_Mapping__c` Id):
  - **Omit `recordId` → create a new row.**
  - **Pass `recordId` → update that existing row in place** (the endpoint SELECTs it and throws
    `No assignment found for recordId ...` if the Id doesn't exist — so read it back first).

  Body shape (add `recordId` to the step-(a).2 body when updating):
  `{"req":{"configPath":"<name|clientAppId>","mappedRecordId":"<005|00E|00e>","businessArea":"<value|'All'>","recordId":"<existing mapping Id>"}}`
  (under `Default_IOU`, `"iouId":"<id>"` replaces `businessArea`, as above).

- **The create path is NOT idempotent — re-POSTing the same binding is rejected, not a no-op.**
  Within one config the dedup key is the **triple** `(configPath, businessArea, mappedRecordId)`
  (i.e. `Client_App_ID__c` + `Business_Area_Name__c` + `Mapped_Record_Id__c`). A create (`recordId`
  omitted) whose triple already exists **throws a duplicate error**
  (`ASSIGNMENT_EDIT_DUPLICATE_MAPPING`). So **before re-assigning, `GET
  ?configId=<name>` first**: if the exact row already exists, the user/role/profile is *already*
  bound as requested — report done, don't re-POST. Only the row being updated is excluded from this
  check, and only when you pass its Id as `recordId` — that's what lets you change an existing
  binding's scope (e.g. move a profile from `businessArea='All'` to a specific area) without it
  colliding with itself: fetch the row's Id via GET, then re-POST with `recordId` = that Id.

- **Moving a binding between configs = DELETE-then-POST, not a re-POST.** A *second* guard,
  `assertNoDuplicateAcrossStrategyRoots`, blocks the same `(mappedRecordId, businessArea)` from
  being bound to a **different config that shares the same resolution strategy** (a blank strategy
  normalises to `Custom_User_Field`, so it's in that bucket) — and this guard has **no exclude
  param**, so you **cannot** simply POST the binding to the new config while the old row still
  exists; it throws `This mapping is already used in the configuration "..."`. To move a binding
  across same-strategy configs: **DELETE the old mapping first, then POST to the new config.** (Two
  configs with *different* strategies don't collide, so this only bites same-strategy roots — but
  DELETE-then-POST is the safe default regardless.)

- **Remove a binding via DELETE.** `DELETE /v1/syncconfig/assignment?id=<name-or-id>` removes one
  mapping. The `id` param accepts **either the row's `Name` or its `Id`** (the service resolves Name
  first, then Id) — use the value the `GET ?configId=<name>` read-back returns; it throws
  `No assignment found for "..."` if neither matches. **Verify with a follow-up GET** showing the row
  gone, exactly like any other write. (Deleting only removes the explicit mapping row; under
  `Default_IOU`, where the IOU *is* the binding, there is no mapping row to delete — revoking that
  user is an IOU-membership change, a core / RE task outside this flow.)

- **Every update/delete ends with a read-back too.** The upsert and the DELETE are writes — verify
  each with `GET /v1/syncconfig/assignment?configId=<name>` (row present with the new scope after an
  update; row absent after a delete). Never infer success from the 200 alone.

## Act 2 end state

- Target user confirmed to exist and active (`User.Id` captured).
- Under `Default_IOU`: the user's default mobility IOU membership **confirmed** by read
  (`IsDfltMobIntrOrgUnit = true`) — **or**, if the user has no such membership, **reported and the
  Act stopped** (the skill does not create IOU membership; that's a core / RE task). Under
  `Custom_User_Field`: no IOU check applies.
- The user bound to the config installed in Act 1: implicitly (via the confirmed IOU, strategy
  `Default_IOU`) or explicitly (a verified `Sync_Client_App_Profile_Mapping__c` row written via the
  `/v1/syncconfig/assignment` endpoint under `Custom_User_Field`) — or, if the `Default_IOU`
  precondition failed, reported as stopped-at-A2.2 with no binding.

## Gotchas

- **`Default_IOU` gates A2.3 on the A2.2 IOU precondition — but `Custom_User_Field` does NOT.**
  Under `Default_IOU` there is no separate "assign to config" write — the IOU *is* the assignment,
  so an IOU-less user cannot be bound: A2.2 reads the membership and, if it's absent, **reports and
  stops** (the skill never creates IOU membership). Under `Custom_User_Field` (the default strategy)
  the binding is a `Sync_Client_App_Profile_Mapping__c` row keyed by **User/Role/Profile** with **no
  IOU involved** — a Role or Profile row binds a whole cohort in one write, and the IOU check does
  **not** apply. Detect the strategy before deciding whether the IOU precondition is even on the
  critical path; don't invent a mapping row a `Default_IOU` root ignores, and don't run the IOU
  check under `Custom_User_Field`.
- **Assignment granularity: User / Role / Profile.** `mappedRecordId` chooses by key-prefix
  (`005`/`00E`/`00e`) and the resolver matches **User → Role → Profile** in priority order. Prefer a
  **Role or Profile** mapping when the intent is "everyone in this role/profile" — it's one row, not
  one-per-user, and it's the same lever the admin VF page pulls.
- **The package's read-only IOU stance is deliberate — and so is this skill's.** `ClientAppMapperService`
  is built to survive orgs where `InternalOrgUnitUser` doesn't exist — that's the signal the package
  doesn't own IOU writes. This skill mirrors that: it **reads** IOU membership as a precondition and,
  if it's missing under `Default_IOU`, reports and stops. It does **not** write IOU membership or
  treat the absence as a Sync Management App task — provisioning a user's default mobility IOU is a core / RE
  responsibility, done outside this flow.
- **Don't write the mapping row raw — the `Business_Area_Name__c` field is overloaded.** It was
  tempting to treat A2.3's explicit path as a plain custom-setting sObject POST (no VF page needed),
  but that skips the strategy-driven derivation of `Business_Area_Name__c` (IOU Id vs Business Area
  picklist value), the cross-config duplicate check, and the unique-Name convention — silently
  corrupting the row. Use `POST /v1/syncconfig/assignment` (`SyncConfigAssignmentEndpoint`), which
  wraps the same `SyncConfigAssignmentService` the VF page uses. This is why A2.3's explicit path is
  `Sync Management App`, not `core`.
- **`configPath` accepts either the `name` or the `clientAppId`; the row is stored under the
  `clientAppId`.** `GET /v1/syncconfig/configs` returns both (e.g. `{name:"<AppId>__Default",
  clientAppId:"<AppId>"}`), and they differ when a config's custom-setting Name isn't its short
  `clientAppId`. The endpoint **normalises** `configPath` to the canonical `clientAppId` before
  writing `Client_App_ID__c`/`Client_App_Profile__c`, so passing either works. This matters because
  the package keys everything off `clientAppId`: the admin **Assignments page**
  (`ClientProfilesController`) only shows rows whose `Client_App_Id__c` equals the config's
  `clientAppId`, and the runtime resolver (`ClientAppMapperService`) returns `Client_App_Profile__c`
  verbatim as the resolved client-app id. **Storing the Name (e.g. `<AppId>__Default`) instead of the
  short `clientAppId` (`<AppId>`) makes the assignment invisible on the admin page and unresolvable at
  runtime** — `SyncConfigAssignmentService` normalises Name↔clientAppId, storing the canonical
  `clientAppId` so this doesn't happen. Always confirm the read-back's `clientAppId` is the short
  canonical value.
