---
name: service-itsm-agentic-setup-incident-sla-configure
description: "End-to-end Incident SLA setup for Service Cloud ITSM — creating a MilestoneType, an Incident-scoped SLA Policy (SlaProcess), attaching a Milestone with criteria, and wiring an Entitlement so Incidents derive an EntityMilestone with a computed TargetDate. Use when the user asks to configure SLA milestones on Incidents, create an SLA policy for Incident records, set up entitlement processes for ITSM, wire milestones so they appear on the Incident page, or enable SLA tracking for incident management. DO NOT TRIGGER when: the user asks about Case entitlements or Case SLA (not Incident), querying existing SLA policies without setup intent, general Entitlement sObject CRUD unrelated to Incident, or Milestone queries for reporting purposes only."
metadata:
  version: "3.8"
  domains: ["Service"]
  minApiVersion: "67.0"
  accessCheck:
    - type: "userPerm"
      value: "CustomizeApplication"
    - type: "orgPerm"
      value: "IncidentMgmt.orgHasITSMOrgPermission"
  relatedSkills:
    - "service-itsm-incident-mgmt-configure"
    - "service-itsm-incident-priority-configure"
  mcpTools:
    headless-360:
      tools: ["describe", "discover", "dispatch", "dispatch_readonly"]
      semver: ">=1.0.0"
allowed-tools: |
  Read AskUserQuestion
  mcp__headless-360__discover
  mcp__headless-360__describe
  mcp__headless-360__dispatch
  mcp__headless-360__dispatch_readonly
---

# Configuring Incident SLA (End-to-End)

Configures a complete **Incident SLA pipeline** for Service Cloud ITSM — the chain deriving an
EntityMilestone (with a computed TargetDate) on every Incident with an Entitlement, all via the
Salesforce-hosted **`headless-360`** MCP server (org from the OAuth JWT). Requires the org-level
**SLA Management for IT Service** setup item (the Phase 0.5 gate).
Four parts: **MilestoneType** (what you measure) → **SLA Policy** (SlaProcess, Incident-scoped,
entry/exit criteria) → **Milestone** (time trigger + criteria) → **Entitlement** (Account-wired, so
Incidents engage the SLA).

## Scope

- **In scope**: the four artifacts above + verifying SLA engagement on Incident records; gating
  **SLA Management for IT Service** (Phase 0.5); offering the OOB *Standard Support for Incidents*
  policy vs a custom one (Phase 0.6, Incident only) — all via `headless-360` MCP.
- **Out of scope**: Case SLA/entitlements; Assignment Rules; Escalation Rules; Notification
  Rules; general Entitlement CRUD not related to Incident SLA; SLA reporting.

---

## Output contract — applies to EVERY message

**Never print a raw Salesforce record Id** (15/18-char: `55…`, `550…`, `0ny…`, `00…`) — full **or
masked** (`557VW…R3XVYA0` still leaks) — in **any** user-facing text: interim narration *and* the
final report. Holds for artifacts you **created** *and* ones you **detected/reused** — name each (the
name you supplied on create, or matched on reuse), keep its Id internal (chaining only). Verifying or
matching via SOQL? Report the **verified attributes/name**, never the Id you queried by. One
exception: on a **halt** you may relay the raw error body verbatim even if it embeds an Id —
don't hand-edit it.

- **Wrong:** `SLA policy created (552VW…)` · `Incident created (0ny…)` · `First Response → 557VW…R3XVYA0` (reuse)
- **Right:** `Created SLA policy "Standard Support for Incidents"` · `reusing the existing First Response
  milestone type` · the test Incident is "the test Incident" until Phase 3, then its `IncidentNumber`;
  milestones by `MilestoneType` name.

---

## Routes at a glance

Reads → `mcp__headless-360__dispatch_readonly`, writes → `mcp__headless-360__dispatch`. Both take raw
HTTP `{"url","method","body"?,"query_params"?}` — **not** `{operation_id, arguments}`; read `body`
from `{status_code, body}`. Full route table with request/response shapes: `references/mcp-invocation.md`.

---

## Clarifying Questions

Ask only what you cannot infer from context (pre-populate; note "(from conversation)"). **Resolve the
Phase 0.5 gate first.** Then: **which org?** (`headless-360` binds to the current OAuth session —
confirm before mutating); **milestone strategy?** (Phase 1.4); **target Account?** (for the
Entitlement); **milestone criteria?** (default `Status != Closed` + pattern-specific filters).

Default suggestion: SLA Policy `Incident SLA Policy`, default BusinessHours, the Account the user
picks, Entitlement `today → today + 1 year`, milestone strategy resolved per Phase 1.4.

---

## Workflow

All steps are sequential. **Always read before you write.** Every call goes through
`mcp__headless-360__*` tools.

### Phase 0 — Reuse what the session already knows

Each Phase 1 read carries a **skip-if-already-known** clause: skip only when the same fact was
produced **this session** by a successful `dispatch_readonly` on the current org and unwritten since —
a user statement is never cache-eligible. Cacheable: master Incident Mgmt pref (step 1, only if
`ENABLED`), SLA feature + Versioning (Phase 0.5), Incident describe (3), `BusinessHoursId` (4), Account
id (5), SLA Connect ops (2). **When in doubt, re-check.**

### Phase 0.5 — SLA Management for IT Service prerequisite gate

**Resolve this gate first, on its own. Reads are safe up front; confirm the org before any write.**
"SLA Management for IT Service" is enabled only when **both** Simplified SLA Setup (feature
`service-cloud-itsm-manage-sla-policies`) **and** SLA Versioning
(`EntitlementSettings.IsEntitlementVersioningEnabled`) are on; either off → not enabled. The one
feature-`enable` turns on both, **permanently** enabling versioning — inseparable. Shapes /
`enableBlockedReasons` / ack wording: `references/mcp-invocation.md`.

- **Read both** (`dispatch_readonly`); proceed to Phase 0.6 **only when both are on**.
- **On an OFF org, read the master license first** (Phase 1 step 1, `service-cloud-itsm-incident`):
  `NOT_AVAILABLE` → **HALT** — don't flip the permanent Versioning switch where Incident SLA can't run.
- **Two separate `AskUserQuestion` acks — never merge.** (a) master Incident Mgmt `NOT_ENABLED` → ask
  to enable it first (reversible, no permanence warning). (b) a *distinct* permanence ack: enabling
  **SLA Management** turns on **SLA Versioning**, which **can't be turned off** (the feature disables
  later but Versioning stays on). Offer **enable**/**stop** — no "versioning-off"; a bare "enable SLA"
  is **not** consent.
- **Decline (b), non-empty `enableBlockedReasons`, or a re-read mismatch → HALT** — enable no SLA
  Mgmt/Versioning, don't proceed to Phase 0.6/1 (a reversible master enable from (a) stands). **After
  any write, re-read both and report the REAL state** — never trust `201`/`204`.

### Phase 0.6 — Predefined (OOB) vs Custom

Once the gate passes, offer the OOB policy **before** any custom-flow questions. **Incident only.**

1. **Prerequisite + detect.** Confirm master Incident Mgmt pref `ENABLED` (Phase 1 step 1). Then `dispatch_readonly` `GET /connect/sla-management/sla-policies` with
   `query_params.processTypes=Incident`; match display name **"Standard Support for Incidents"**.
   - **Already present** → **no re-seed** (no idempotency), no custom upsell; report it is seeded.
     **If warn/escalate actions were requested → resolve the named existing milestones → Phase 2.5 →
     Phase 3 verify → STOP** (attach actions even though the policy was already seeded).
2. **Fork** — one `AskUserQuestion`, **Predefined first / recommended**: Salesforce's predefined
   Incident policy (*Standard Support for Incidents* — priority-tiered) **or** a custom one. One-way:
   predefined seeds an **active** policy + Entitlement, no un-seed path (manual delete only).
   - **Predefined →** resolve BusinessHours + Account (Phase 1 steps 4–5) → **Phase 2-OOB** → **Phase
     2.5** (if actions requested) → Phase 3 verify → **STOP**.
   - **Custom →** existing Phase 1 → 1.4 → 1.5 → 2 → 3, unchanged.

### Phase 1 — Preflight & discovery

**On any `401` / `403` / `404` from a step below, halt and surface the raw error** — the org/client is misconfigured. `401` → MCP auth (ECA/token). `403` → user perm OR ITSM Incident Management license/pref missing. `404` → `headless-360` not activated OR Entitlement Management not enabled for Incident.

1. **Master Incident Management pref — direct read** *(skip conditions in Phase 0)*.
   `dispatch_readonly` `GET .../connect/setup/discovery/features`, filter `features[]` to the **exact**
   `apiName == "service-cloud-itsm-incident"` — never a look-alike (`service-cloud-incident-management`
   is generic Case-based Incident Management, not our target). Read `status`: `ENABLED` → proceed;
   `NOT_AVAILABLE` (license missing) → **halt and surface it** — cannot be enabled here, no delegate/ack;
   `NOT_ENABLED` → **explicit `AskUserQuestion` ack first (never auto-enable as an implied SLA
   dependency)**, then delegate to `service-itsm-incident-mgmt-configure` inline (confirms-to-write) and
   re-read; if declined, halt — every SLA artifact below depends on the master being on. Full shape + why
   setup-org-preferences 404s here: `references/mcp-invocation.md` (Preflight A).
2. **Discover the Connect operations** — *(skip if already verified this session — see Phase 0)*.
   `mcp__headless-360__discover(query="sla-management milestone")` to confirm the SLA Management
   Connect API is indexed, then `mcp__headless-360__describe(id=<operation_id>)`
   for the `milestone-types`, `sla-policies`, and `sla-policies/{id}/milestones` POST operations to pull
   their exact input schemas + HTTP routes. If `discover` returns nothing after rewording the query,
   the corpus does not index this surface for the org — direct the user to **Setup → SLA/Entitlement
   setup** and stop.
3. **Verify Incident Management + SLA fields** — *(skip if `Incident.describe` result for the
   current org is already in context — see Phase 0)*. Otherwise `dispatch_readonly` on
   `GET /services/data/v67.0/sobjects/Incident/describe` and confirm `fields[]` includes
   `EntitlementId`, `SlaStartDate`, `SlaExitDate`. If the describe 404s or fields are missing, direct
   the user to enable Entitlement Management for Incident and stop.
4. **Find default BusinessHours** — *(skip if `BusinessHoursId` for the current org's default is
   already captured this session)*. Otherwise `dispatch_readonly` on `GET /services/data/v67.0/query` with
   `query_params.q="SELECT Id, Name FROM BusinessHours WHERE IsActive = true AND IsDefault = true"`.
   If `body.records` is empty, stop with a message to create default Business Hours in Setup. Capture
   `BusinessHoursId`.
5. **Resolve the target Account** — *(skip if already resolved this session)*. Phase 2's Entitlement
   needs an `AccountId`. If the user **named** one → look up (`SELECT Id, Name FROM Account WHERE Name
   = '<escaped>' LIMIT 1`); not found → **stop and ask**, never substitute. If the user **authorized
   any/existing Account** → pick the most recently active (`... WHERE IsDeleted = false ORDER BY
   LastModifiedDate DESC LIMIT 1`) and **surface which** in the plan. Otherwise → **ask via
   `AskUserQuestion`**: list real candidates by **name only** + "type a name"; **never auto-pick,
   pre-select, or expose an internal sort key** (e.g. recency). If none exists, stop. Capture `AccountId` + name.
6. **Read existing SLA artifacts (idempotency probe)** — `dispatch_readonly` SOQL for `SlaProcess` by
   name (`... WHERE Name = '<name>' AND SobjectType = 'Incident'` — the field is `SobjectType`;
   `ProcessType` returns `INVALID_FIELD`), each `MilestoneType` the strategy would create,
   `SlaMilestone` under the matched policy, and `Entitlement` by name on the resolved Account. If
   **every** artifact already exists with the requested config, set `noOp=true` and skip Phase 1.4 +
   Phase 2 (skip condition (b)); any missing/divergent artifact → proceed to Phase 1.4.

### Phase 1.4 — Milestone Strategy

Every SLA policy needs at least one milestone. Load `examples/milestone-patterns.md` — it lists the
skip conditions (concrete shape in prompt / idempotent no-op / explicit up-front authorization) and
the five strategy options with their `AskUserQuestion` prompt, defaults, and MilestoneType-reuse
rules. Skip condition (c) still requires Phase 1.5 plan-narration before dispatch. Multi-milestone
selection expands to N creates in Phase 2 step 10 (one POST per milestone, `order` 1..N, same SlaProcess).

### Phase 1.5 — Confirm before mutating

7. **Confirm the plan** — present the resolved config (target **org**, **SLA Policy** name, resolved
   **Account** name, **Entitlement** date range, and the **full per-milestone list** — never collapse
   Priority-tiered / Custom to "N milestones"). **Skip the `AskUserQuestion`** (but still narrate the
   plan before dispatch) when up-front authorization was granted (note `(authorized in prompt)`), the
   branch is a no-op, or it was already confirmed in conversation (note `(confirmed in conversation)`);
   otherwise require an explicit "yes" before Phase 2. Everything after this step mutates the org.

### Phase 2 — Create SLA Artifacts (exact order — each depends on the previous)

Capture each returned `id` for chaining only.

8. **Create MilestoneType(s)** — `POST /connect/sla-management/milestone-types`. One POST per
   distinct MilestoneType required by the strategy. Reuse a single MilestoneType across milestones
   that share a name (Priority-tiered "First Response" reuses one MilestoneType across all four
   milestones); create separate MilestoneTypes for distinct concerns (Response + Resolution =
   two MilestoneTypes; Escalation ladder = three). Capture each `id`. A feature enable pre-seeds a
   default MilestoneType catalog; a detected/reused one is narrated by name only (Output contract:
   name, never `→ <Id>`).
9. **Create SLA Policy** — `POST /connect/sla-management/sla-policies` with `processType='Incident'`
   and the `businessHourId` from Phase 1. Capture `id`. **The response echoes nulls — verify via
   SOQL, not the body; narrate the policy by name, never the Id** (Output contract).
10. **Attach Milestone(s)** — load the request-body template from `assets/attach-milestone.json`
    and, for each milestone in the strategy, populate `milestoneTypeId`, `timeTrigger`, `order`
    (1..N in the strategy's order) and any per-pattern `filterItems` additions from
    `examples/milestone-patterns.md`, then `POST /connect/sla-management/sla-policies/<slaId>/milestones`.
    Each `milestoneCriteria[]` item needs `milestoneAgreementType` (`SLA`/`OLA`) and
    `filterType: RuleFilter`. Do **not** put `slaProcessId` in the body — carried by the path.
    One POST per milestone; on any failure, halt and surface the raw error (no half-attached policy) —
    narrate each by `MilestoneType` name, never its Id/`triggerId` (Output contract).
11. **Create Entitlement** — `POST /sobjects/Entitlement` linking the resolved Account (from Phase 1
    step 5), the SLA Policy (`SlaProcessId`), and Business Hours. For immediate engagement, backdate
    `StartDate` to yesterday — narrate it by name/Account, never its Id (Output contract).

### Phase 2-OOB — Seed the Predefined Incident Policy

Reached only from Phase 0.6 Predefined (replaces Phase 1.4/1.5/2). Follow the seed recipe in
`references/mcp-invocation.md` (**Predefined Incident Policy**) with `assets/predefined-incident-policy.json`
— it uses the **Phase 2 routes** (2 MilestoneTypes → SLA Policy `active:true` → 6 milestones,
each `startTimeBasedOn: MILESTONE_CRITERIA` → Entitlement), validates each `Priority`/`Status`
against the live picklist, and avoids the Connect activate PATCH. Then Phase 2.5 (if actions requested), Phase 3 (a non-lowest tier — Moderate/Low, not Critical),
and **STOP** — no *proactive* custom offer.

### Phase 2.5 — Milestone Actions (optional: Warn / Escalate)

After milestones exist (Phase 2 or 2-OOB), **only if** the user asked to warn/escalate/notify: apply
the requested checkpoint(s) to **every milestone the user named** (not just one), each offset computed
from that milestone's own target. Map "warn at X%" → an offset *before* target, "on breach" →
*at/after* it; **confirm the full set before writing** (up-front auth waives the re-ask; narrate it
regardless — no headless delete), then, per milestone, delegate to headless
**`create-milestone-action`** (`discover` → `describe` → `dispatch`). **Confirm each from the response
body** (`success` + non-empty `actionMappings`; a *timed* checkpoint also returns a `triggerId`), never
the `201`. Narrate each by its **`MilestoneType` name**, never the milestone Id/`triggerId` (Output
contract). Formula, roles, proven body, defaults, IST business-hours note:
`references/mcp-invocation.md` (Milestone Actions).

### Phase 3 — Verify

12. **Verify the SLA Policy** — SOQL on `SlaProcess` (do not trust the create response).
13. **Create a test Incident** with `EntitlementId` set. For Priority-tiered / OOB strategies, test a
    tier **other than the lowest `order`** — Critical is order-1, the collapse fallback, so it can't
    detect a dropped criterion. If a direct `Priority`
    insert is rejected (it may be matrix-derived), set `Urgency`/`Impact` to derive the tier. Narrate
    by `IncidentNumber`, never the Id.
14. **Verify engagement + tiering** — SOQL that `Incident.SlaStartDate` is populated and the
    `EntityMilestone` lands on the **correct tier** (a Moderate/Low Incident → the 240/960 tier, NOT
    30/120). The create `201` always echoes `milestoneCriteria:[]`; only this runtime read proves the
    ACTIVE criteria persisted.
15. **Report results** using the output format below.

---

## Rules / Constraints

| Constraint | Rationale |
|-----------|-----------|
| Gate **SLA Management** first (Phase 0.5) — one enable turns on the feature **and**, one-way, **SLA Versioning**; **two separate acks (master, then permanence) — never merged**; decline/blocked/verify-fail → **HALT**; re-read + report real state | Versioning is irreversible; writes don't confirm state |
| Offer **predefined (OOB)** first (Phase 0.6, Incident only); detect before seed; if chosen, seed → verify → **STOP** (no custom upsell) | OOB seed isn't idempotent — re-seed duplicates |
| `discover` + `describe` before any mutation | Catches a missing SLA surface / disabled Incident Mgmt early |
| Ask (`AskUserQuestion`) the milestone strategy — never silently default to Single | Real ITSM policies have >1 milestone |
| Reuse one MilestoneType per shared name; a distinct one per distinct concern | Runtime keys milestones by MilestoneType |
| Multi-milestone: halt on any milestone POST failure (no half-attached policy) | Partial attach diverges from the confirmed plan |
| Priority-tiered: validate every `Priority` value against the live picklist before dispatch | Server accepts any string → an unknown value is a dead milestone |
| Entitlement is standard sObject DML; `StartDate` controls status (future = Inactive) | Not on the `/connect/sla-management/` surface |
| **No record Id in any message** (see Output contract, incl. reused artifacts); `AskUserQuestion` labels customer-facing (no "demo"/internal defaults) | The #1 retest failure; leaked Ids / internal framing look unprofessional |

Additional API quirks: `references/mcp-invocation.md`.

---

## Verification Checklist

- [ ] **SLA Management gated (Phase 0.5)** — feature + SLA Versioning both on, only after the **permanence ack** (separate from the master ack); reported state = a re-read, not the write. Declined / blocked / verify-fail → **HALTED** before Phase 0.6/1, no artifacts.
- [ ] **Predefined vs Custom offered (Phase 0.6)** — with the feature ON, OOB *Standard Support for Incidents* offered first; if present, reported not re-seeded; if chosen, seeded (2 MilestoneTypes + 6 milestones + Entitlement), verified, **no** custom offer after.
- [ ] Master Incident Mgmt pref (exact `service-cloud-itsm-incident`) `ENABLED` via live read, or delegated when `NOT_ENABLED` (`NOT_AVAILABLE` → HALT) — not a user assertion, not a look-alike.
- [ ] `discover`/`describe` confirmed the SLA Connect ops.
- [ ] Incident describe returned 200 with `EntitlementId`, `SlaStartDate`, `SlaExitDate`.
- [ ] Default BusinessHours found.
- [ ] **Milestone strategy resolved** — Phase 1.4 skip condition OR `AskUserQuestion`; Priority-tiered / Custom validated every `Priority`/criteria value against the live picklist before dispatch.
- [ ] **Configuration confirmed OR skip condition met** (up-front auth / no-op / prior confirmation / "yes"); the resolved plan (org, SLA name, account, entitlement range, per-milestone list) narrated before Phase 2.
- [ ] Artifacts created in order (MilestoneType(s) → Policy → Milestone(s) → Entitlement), each POST 201; any milestone POST failure halted (no partial attach). Trivial on no-op.
- [ ] **Milestone actions (Phase 2.5)** — if requested, attached to **every** named milestone; each confirmed from `body.success` + `actionMappings`, not the `201`; full set narrated before write.
- [ ] SLA Policy verified via SOQL, not the create response (no-op: the Phase-1 read is the verification).
- [ ] Test Incident has `SlaStartDate` populated (Priority matched for Priority-tiered) and ≥1 EntityMilestone with correct TargetDate; expected milestone(s) present. Skip on no-op.
- [ ] **No record Id in any message** — interim narration *and* final report; artifacts by name, test Incident by `IncidentNumber` (see Output contract).
- [ ] Before/after + summary shown; no-op states the pre-existing config verbatim + "no changes made".

---

## Output Format

Use the `examples/output-templates.md` templates; fill placeholders as-is. The success report must carry, unambiguously: the **SLA Policy**; **every milestone** by MilestoneType name + time + criteria; the **Entitlement → Account**; **every requested action** by milestone + Warning/Violation role + offset + how confirmed; a **Verification** section (SOQL-confirmed policy + test-Incident `SlaStartDate`/EntityMilestones, or an honest partial note); created-vs-reused per artifact; a **scope line** (only the Incident SLA). No record Id anywhere.

---

## Reference File Index

| File | When to read |
|------|--------------|
| `references/mcp-invocation.md` | Every phase — call shapes, templates, response envelope, discovery, gotchas |
| `examples/milestone-patterns.md` | Phase 1.4 — the five strategies: times, criteria, MilestoneType reuse, filter extensions |
| `assets/attach-milestone.json` | Phase 2 step 10 — milestone POST body; substitute ids/timeTrigger/order; append `filterItems` |
| `assets/predefined-incident-policy.json` | Phase 0.6 / 2-OOB — OOB seed template (policy + 2 MilestoneTypes + 6 milestones, Moderate+Low merged) |
| `assets/attach-milestone-action.json` | Phase 2.5 — Warn/Escalate action body templates (Field Update); pair with mcp-invocation.md (Milestone Actions) |
| `examples/output-templates.md` | Output Format — success/partial report templates; fill placeholders, no record Id |

---

## Related Skills

The priority matrix (Impact × Urgency → Priority) is separate — `service-itsm-incident-priority-configure`;
if a Priority-tiered strategy is requested but `Incident.Priority` lacks values, direct the user there
first. Other ITSM flows (Major Incident Mgmt, custom fields) are out of scope.
