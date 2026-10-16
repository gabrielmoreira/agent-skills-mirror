# Relationship & Feature Map — Volunteer Management

How the entities connect and combine into features. When a user expresses intent, find the feature
here first, then drill into `entities.md`. Theme references (`Tn`) point at `themes.md`.

## The backbone (structural spine)

```text
VolunteerInitiative  (optional top-level anchor; self-referential tree)
   │  (optional links from JobPosition / Shift / Assignment)
   ▼
Position  (reusable TEMPLATE; carries PositionQualification)
   │  JobPosition.Position  (lookup; JobPosition links UP — never the reverse; quals NOT copied)
   ▼
JobPosition  (concrete POSTING; optional Location; carries JobPositionQualification)
   │  JobPositionShift.JobPosition  (required; deleting the JobPosition deletes its shifts)
   ▼
JobPositionShift  (concrete DATED occurrence; capacity; optional RecurrenceSchedule)
   │  JobPositionAssignment.AssignedPositionShift  (optional)
   ▼
JobPositionAssignment  (a person doing it on a day; SOURCE OF TRUTH for hours)
```

**Rules that matter:**
- **Shift and Assignment attach ONLY to JobPosition, never Position** (T15). Position alone cannot
  be scheduled or assigned against. A JobPosition is required for scheduling/matching.
- **Parentage is optional and mix-and-match** (T7, T21). A JPA may link to a Shift, a JobPosition,
  a VolunteerInitiative, any mix, or none (standalone ad-hoc). VI may be absent entirely.
- Position → JobPosition is **template → concrete posting** (T15): one template, many localized
  postings, each able to add its own JobPositionQualifications.

## Delete behaviour (informational — these skills never delete)

| Deleting… | Effect |
|---|---|
| a Location | deletes its Addresses; blocked while a JobPosition uses it |
| a Position | deletes its PositionQualifications; blocked while a JobPosition uses it |
| a JobPosition | deletes its JobPositionShifts and JobPositionQualifications |
| an OperatingHours | deletes its TimeSlots |
| a Competency | blocked while a qualification uses it |

## The authenticated boundary (who links to Account vs Contact)

The single most important cross-cutting relationship rule (T2, T10, T16):

| Entity | Account | Contact | Meaning |
|---|---|---|---|
| JobPositionAssignment | `AssignedAccount` (opt) | `AssignedContact` (opt) | guest creates Contact-only; Account attached on conversion. **Per-person (DGS) rollups require Account; VI rollups don't.** |
| PersonLocationAvailability | required | optional | availability is authenticated-only (anti-bloat) |
| PersonExamination | VM-added (opt) | required | credentials via portal want authenticated Account |
| PersonCompetency | via polymorphic `Person` | via polymorphic `Person` | `Person` = {Account, Contact}; already had Account |
| DonorGiftSummary | `Donor` (master-detail) | — | engagement history is Account-only |

**Takeaway:** anything that persists a volunteer's own data trends toward requiring an authenticated
Account. Guest (Contact-only) records are tolerated at signup but don't feed the per-person (DGS)
rollups until an Account exists (VI rollups aggregate by initiative regardless).

## Feature: Volunteer Matching (T9)

Matches volunteers to opportunities on two axes — **held competency** and **availability**:

```text
HELD (supply)            REQUIRED (demand)                 WHERE/WHEN
PersonCompetency ── vs ── PositionQualification ──┐        PersonLocationAvailability
  → Competency            JobPositionQualification ├─       → Location ⇄ JobPosition.Location
                            → Competency-only ──────┘        → OperatingHours → TimeSlot
```

- **Supply side:** **PersonCompetency only** — declared by the volunteer via Experience Cloud or set
  by an internal user. The `Verification*` fields (`VerificationStatus`/`Date`/`Summary`) are
  informational and **NOT used in matching** (verified vs merely claimed is not weighed).
- **Demand side:** PositionQualification (template) + JobPositionQualification (extra, per posting).
  Matching uses QualificationLevel on Competency qualifications. A Job Position's own qualifications
  and its Position's qualifications are checked together, keeping the higher level per Competency.
  Nothing is copied from the Position to the Job Position. `QualificationReferenceRecordId` can point
  at a Competency or an Examination (T17); Examination qualifications are ignored, and a
  qualification with no QualificationLevel is skipped.
- **Examination is NOT a matching factor:** automated matching reads neither `PersonExamination` nor
  Examination-typed requirements. Examination is for **manual/internal qualification** — a manager
  reviews held credentials to qualify a volunteer (see `entities.md`).
- **Where/when:** PLA matched via **JobPosition.Location** + **time-window containment** (a TimeSlot
  must contain the shift window); with no time filter, matching falls back to Location-only.
- **Level-aware:** the volunteer's `PersonCompetency.QualificationLevel` must be at or above the
  required level. `ProficiencyLevel` is never read.

## Feature: Shift capacity (T22) — counted, never enforced

```text
JobPositionAssignment.DoesCountTowardShiftCapacity = true   (default true; any status)
        │  recounted on every JPA save and delete (NOT a rollup)
        ▼
JobPositionShift.PositionAssignmentCount  ──►  RemainingCapacity  [formula]
```

- `RemainingCapacity` = MAX(0, MaximumAttendeesCount − PositionAssignmentCount) when both are set and
  MaximumAttendeesCount is above 0; otherwise blank.
- Per-assignment boolean so waitlisted/observer assignments needn't be counted.
- **Nothing blocks a signup when a shift is full.** A customer who wants a hard limit adds their own
  validation rule.

## Feature: Engagement rollups (T12, T13, T14)

**Source of truth = JobPositionAssignment** (`ActualDuration` for hours).
Two rollup targets, **both shipped empty — the customer builds and schedules a Data Processing Engine job**:

- **Person-level → DonorGiftSummary** (4 VM fields): any JPA on the Person Account (NOT filtered by
  VolunteerInitiative — the XML description saying otherwise is wrong, T13). Volunteer ≈ donor is why
  it lives on the Fundraising entity (T14).
- **Initiative-level → VolunteerInitiative** (6 fields): rolls up assignments for the initiative and
  **up its self-referential tree** to parent initiatives. `TotalActiveVolunteerCount`/`AttendanceRate`
  depend on customer-configured eligibility (which JPA `Status` values count).

**ConstituentRole** is the companion flag: it marks *who is a volunteer* (`RoleType` = "Volunteer",
a value that ships out of the box, T6) so the rollups are meaningful. ConstituentRole =
the flag; the rollup fields = the totals.

## Feature: Recurrence (T23)

VM **decouples** RecurrenceSchedule from the shared recurrence engine other clouds use. In VM it is
**purely informational** — viewing a JobPositionShift, you can see it's part of a series and what the
series looks like. VM ships a feature that, on creating a recurring schedule, generates the
RecurrenceSchedule record AND **materializes every JobPositionShift upfront** (time-bounded, capped).
All shift rows exist in the DB immediately; nothing appears dynamically later.

## Feature: Approval + Stage Management (T18, T24, T25, T26)

```text
Position.IsInternalApprovalRequired = true   (inert flag on the template)
        │  customer wires Salesforce Approvals to it
        ▼
Salesforce Approvals runs on a JobPositionAssignment
        │  on approval, Stage Management advances…
        ▼
JobPositionAssignment.Status  (e.g. "Awaiting Approval" → "Upcoming")
```

- VI, Position, JobPosition, JobPositionShift and JobPositionAssignment each have their own `Status`
  picklist with values that ship out of the box (see the picklist table in `entities.md`) —
  **independent lifecycles** (T24). No cross-entity status propagation (closing a JobPosition does not auto-close its Shifts; a JPA
  "Complete" doesn't auto-feed VI — that's the Data Processing Engine job's work).
- **Stage Management** (a built-in platform feature) drives automations as an enum progresses
  through stages (T25). The Status field alone is just a picklist; registering it with Stage
  Management makes it a governed lifecycle.
- The Position approval flag ultimately resolves on **JPA.Status** (T26).
- **No Status is "primary."** structure-generate and records-create treat each lifecycle separately.

## Feature: Benefit bridge (T19, T20)

```text
PositionBenefit  (requires VM && Benefit Management — compound AND gating)
   Position (master-detail)  ──►  Benefit  (OUT OF SCOPE — external dependency)
```

Volunteers provide a service that beneficiaries receive **as a Benefit**. Attached at the Position
(template) level since all its JobPositions provide the same service. Benefit itself is Program
Management — treat as an external dependency, never model it.

## Quick intent → entity lookup

| User intent | Entities / fields |
|---|---|
| "Mark someone as a volunteer" | ConstituentRole (`RoleType`="Volunteer", ships out of the box) |
| "Track completed volunteer hours" | JobPositionAssignment.`ActualDuration` → DonorGiftSummary/`VolunteerInitiative` rollups (build a Data Processing Engine job) |
| "Let volunteers say when/where they're free" | PersonLocationAvailability (+ Location, OperatingHours, TimeSlot) |
| "Record a volunteer's skills / credentials" | PersonCompetency (matched vs Competency qualifications) / PersonExamination (credentials; manual qualification only, not matched) |
| "Record a cause or interest a volunteer cares about" | Not PersonCompetency (it feeds matching). Use a customer-defined interest or preference field on a related record |
| "Define a reusable job" | Position (+ PositionQualification) |
| "Post that job (optionally at a location)" | JobPosition (+ JobPositionQualification for extra local reqs) |
| "Schedule a specific dated slot" | JobPositionShift (+ capacity fields) |
| "Sign someone up" | JobPositionAssignment (link to Shift/JobPosition/VI as desired) |
| "Cap a shift at N people" | JobPositionShift.`MaximumAttendeesCount` + JPA.`DoesCountTowardShiftCapacity` — counted, never enforced; a hard limit needs a customer validation rule |
| "Require approval before signup" | Position.`IsInternalApprovalRequired` + Salesforce Approvals + JPA.`Status`/Stage Management |
| "Organize activities under a campaign/initiative" | VolunteerInitiative (self-referential tree) |
| "Volunteers deliver a benefit to those we serve" | PositionBenefit (needs VM && Benefit Management) |
| "Recurring shifts" | RecurrenceSchedule (informational) + a shipped feature pre-generates all Shifts |
