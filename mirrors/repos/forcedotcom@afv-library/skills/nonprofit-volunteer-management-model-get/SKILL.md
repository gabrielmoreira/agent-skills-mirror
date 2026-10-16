---
name: nonprofit-volunteer-management-model-get
description: "Use this skill to explain how the Salesforce Nonprofit Cloud Volunteer Management (VM) data model works and why, answering from reference material without connecting to an org. Answers what a VM object, field, or relationship is for and how features such as volunteer matching, shift capacity, hours rollups, sign-up approval, and permission gating behave, and maps a goal (\"track volunteer hours\", \"cap a shift\") to the objects and fields behind it. TRIGGER when a user asks what a VM object, field, or relationship is for, or how a VM feature works. DO NOT TRIGGER to plan a program (use nonprofit-volunteer-management-structure-generate), to create records (use nonprofit-volunteer-management-records-create), to enable Volunteer Management in an org, or for NPSP / Volunteers for Salesforce (V4S), which is unsupported."
metadata:
  version: "1.1"
  domains: ["Nonprofit"]
  relatedSkills:
    - "nonprofit-volunteer-management-records-create"
    - "nonprofit-volunteer-management-structure-generate"
  accessCheck: "(OrgPermissions.VolunteerManagement) && (OrgPreferences.VolunteerManagementEnabled)"
---

# Nonprofit Cloud Volunteer Management — Data Model Knowledge

This skill explains *why* the Volunteer Management object model is shaped the way it is: why so many
entities are borrowed from other clouds, how fields are gated by permissions, and how the pieces
combine into features. Object and field definitions give the fields; this skill gives the intent, so
an agent can map a user's goal ("track completed volunteer hours", "require approval before signup",
"cap a shift at 10 people") onto the right entities and fields.

## Hard rules

- **Never delete records.** No delete, rollback or cleanup of any kind. If a write fails part-way, report what was created and what wasn't; never undo it.
- **Never act on NPSP or Volunteers for Salesforce (V4S).** That legacy package is unsupported here. Say so and stop.
- **No acronyms or internal labels in what the user sees.** Write out Volunteer Initiative, Job Position, Job Position Shift, Job Position Assignment, Position Qualification, Job Position Qualification, Data Processing Engine, and "out of the box". Never show internal step or section labels.
- **No org operations.** This skill answers from its references; it never reads or writes an org.

## Scope

Only the entities in the **Volunteer** and **Volunteer Management** sections of the model, plus the
Address that a Location points at. Benefit is referenced by one in-scope bridge entity
(PositionBenefit) but belongs to Program Management: treat it as an external dependency and never
model it.

**Non-goals:**
- Planning or designing a program, or deciding which records a program needs → `nonprofit-volunteer-management-structure-generate`.
- Creating or reusing records, or how to fill in a field when creating one → `nonprofit-volunteer-management-records-create`.
- Turning Volunteer Management on in an org.

## Required Inputs

The user's question. No org connection is needed.

## Answering Workflow

1. **Identify the concept.** Work out which feature or entity the question touches: matching,
   capacity, rollups, approval, the benefit bridge, the hierarchy, or a single entity or field.
2. **Read the matching reference.** Features and how entities connect → `references/relationships.md`;
   one entity's purpose, fields and gotchas → `references/entities.md`; the design principle behind a
   choice → `references/themes.md`.
3. **Answer only what was asked, briefly.** Lead with the direct answer, then only the detail that
   earns its place. Don't tour the model or add features the user didn't ask about. If the user
   narrows the question ("just the permission model"), stay inside that boundary; mention a
   neighbouring mechanism only if the answer depends on it, in one line. Keep an answer to a few
   short paragraphs or bullets, about 300 words. Give each entity one line; list its fields, picklist
   values or a summary table only when the user asks for them.
4. **Mention caveats, don't list them.** If the topic has a "shipped but not configured" caveat (see
   "Mechanism shipped, configuration is the customer's" below), say that one exists and offer to show
   it. Give the detail only if the user asks.

## Rules / Constraints

The hard rules above apply to every answer. In addition:

| Constraint | Rationale |
|---|---|
| Answer from the references, not from memory | The references hold the verified behaviour; general Salesforce knowledge often gets Volunteer Management wrong (for example, capacity and qualification matching). |
| No record Id literals in answers | Ids differ per org; a hard-coded Id is wrong in every other org. |
| Scope tightly to the question | A long answer that tours adjacent features buries the part the user needed. |
| Caveats only on request | Say a caveat exists and offer it; dumping every caveat makes each answer longer and less useful. |
| Don't state how to fill in fields when creating records | That belongs to records-create's field guide; two copies drift apart. |

## The three things to understand first

### 1. Reuse over new entities — and Account is a "hero" entity
Most Volunteer Management entities are **not native**. They are borrowed from other clouds, and
Volunteer Management adds a small number of fields gated behind its permissions. This is deliberate:
Account is a "hero" entity that Salesforce makes hard to extend, so product data hangs off
**related entities** rather than new Account or Contact fields. Volunteer Management adds **no**
fields to Account or Contact. For volunteer data, look for the related entity.

A borrowed entity's Volunteer Management fields are the only part of it that Volunteer Management
cares about. `references/entities.md` names every one.

### 2. The permission model mirrors an authenticated boundary
Records are gated by four permission expressions that map to three kinds of user:

| Permission | Who |
|---|---|
| `orgHasVolunteerManagement` | the org has the feature (API access, related lists) |
| `userHasVolunteerManagement` | internal staff (volunteer managers) |
| `userHasVolunteerManagementCmtyAccess` | a signed-in community volunteer (Experience Cloud) |
| `userHasGuestVolunteerManagementCmtyAccess` | a guest who hasn't signed in |

A volunteer can sign up **before** they have an account. A guest exists only as a **Contact**; once
they create or convert to a **Person Account** they are an authenticated volunteer. This boundary is
the most important pattern in the model: entities that store a volunteer's own data (availability,
credentials, engagement history) require an **Account**; the public signup path accepts a bare
Contact.

The volunteer is a **Person Account**, so Person Accounts must be enabled. The "Business Account"
box in the diagram is just how Salesforce draws Person Accounts.

`&&` (AND) gating across two clouds marks a deliberate **cross-product bridge** (Volunteer
Management && Benefit Management), unlike the usual `||` (OR) gating of plain reuse. See
`references/themes.md` T20.

### 3. Mechanism shipped, configuration is the customer's
Volunteer Management often ships the field or hook but not the behaviour. These are the caveats to
offer when a question touches them:

- **Engagement rollups** (4 fields on DonorGiftSummary, 6 on VolunteerInitiative) exist but are
  **empty** until the customer builds and schedules a Data Processing Engine definition.
- **Status** on Volunteer Initiative, Position, Job Position and Job Position Shift ships with
  out-of-the-box values that admins can change. Each lifecycle is independent: nothing moves
  one entity's Status when another's changes. Stage Management automation is the customer's to set up.
- **`Position.IsInternalApprovalRequired`** does nothing on its own. The customer wires Salesforce
  Approvals to it; approval moves the Job Position Assignment's Status.
- **Shift capacity is counted, never enforced.** Assignments are counted onto the shift and
  RemainingCapacity is a formula, but nothing blocks a signup when a shift is full.
- **`ConstituentRole.RoleType`** ships with "Volunteer" (plus Donor, Philanthropic Prospect and
  Participant), so the customer doesn't need to add it.

## The model at a glance

- **Who:** Person Account (authenticated volunteer) or Contact (guest). Marked as a volunteer by
  **ConstituentRole**. Engagement totals sit on **DonorGiftSummary** (a volunteer is assumed to be a
  likely donor).
- **What they can do:** **PersonLocationAvailability** (when and where), **PersonCompetency**
  (skills), **PersonExamination** (credentials). Matching uses availability and PersonCompetency;
  PersonExamination is for a manager's own review, not matching.
- **The work:** **Position** (reusable template) → **JobPosition** (a concrete posting, optionally at
  a Location) → **JobPositionShift** (a dated occurrence) → **JobPositionAssignment** (a person doing
  it on a day; the source of truth for hours).
- **Requirements on the work:** **PositionQualification** and **JobPositionQualification** point at a
  Competency or an Examination. Matching uses QualificationLevel on Competency qualifications. A Job
  Position's own qualifications and its Position's qualifications are checked together, keeping the
  higher level per Competency. Nothing is copied from the Position to the Job Position.
- **Organizing anchor:** **VolunteerInitiative** — an optional, self-referencing top-level parent.
- **Integrations:** **PositionBenefit** bridges to Benefit Management (volunteers provide a service
  that beneficiaries receive as a Benefit); Approvals and Stage Management hook into the Status fields.

## Output Expectations

- A direct answer in plain language, naming the entity and field API names the user needs.
- Only the entities and features the question needs, about 300 words, one line per entity. Say each point once: no restated summary, no closing recap, and no list of follow-up topics.
- When a caveat applies, one line saying it exists and offering to show it.
- When the request is out of scope, name the sibling skill that handles it, or say that NPSP / V4S is
  unsupported and stop.

## Cross-Skill Integration

| User wants to… | Use |
|---|---|
| Plan or design a program, or decide which records it needs | `nonprofit-volunteer-management-structure-generate` |
| Create or reuse records, or know how to fill in a field | `nonprofit-volunteer-management-records-create` |

Those skills come back here only for what an entity or field means.

## Reference File Index

| File | Read it for |
|---|---|
| `references/entities.md` | One entity's purpose, origin, Volunteer Management fields, picklist values and gotchas (workflow step 2) |
| `references/relationships.md` | How entities connect, delete behaviour, and how they combine into features; intent → entity lookup (workflow step 2) |
| `references/themes.md` | The design principles (T1–T26) behind the model's shape (workflow step 2) |
