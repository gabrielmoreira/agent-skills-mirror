# Entity Reference — Volunteer Management Data Model

Every in-scope entity: **purpose/intent**, **origin** (native VM / reused-from-cloud / standard),
**VM-gated fields** (the only fields VM cares about on a borrowed entity), **key relationships**,
and **gotchas**. How to fill in fields when creating records is not here — that is records-create's
field guide.

Origin legend:
- **NATIVE** — defined by Volunteer Management itself.
- **REUSED (+VM fields)** — borrowed from another cloud; VM added gated field(s).
- **REUSED (as-is)** — borrowed; VM added nothing (used unchanged).
- **STANDARD** — core Salesforce object.

Theme references (`Tn`) point at `themes.md`.

---

## Picklists

**Restricted** means only the listed values are accepted; a customer can't add their own.
**Unrestricted** means the values are the customer's: admins add and change them, so the org's
object description is the only source for them. Either way, a record can only use a value that's in the list,
so a new value is added to the list before it's used.

| Picklist | Values | Kind |
|---|---|---|
| `VolunteerInitiative.Status` | Upcoming, In Progress, Complete, Canceled, Postponed, Archived | unrestricted |
| `Position.Status`, `JobPosition.Status`, `JobPositionShift.Status` | Upcoming, In Progress, Complete, Canceled | unrestricted |
| `JobPositionAssignment.Status` | Awaiting Approval, Upcoming, In Progress, Pending Verification, Complete, Canceled, Absent | unrestricted |
| `ConstituentRole.RoleType` | Donor, Philanthropic Prospect, **Volunteer**, Participant | unrestricted |
| `ConstituentRole.Status` | Active, Former | unrestricted |
| Position/JobPosition Qualification `ProficiencyLevel` | Beginner, Intermediate, Advanced | unrestricted |
| `Location.LocationType` and `Address.LocationType` (one shared set), `Address.AddressType` | Business Site | unrestricted |
| `Position.Type`, `Position.Sensitivity`, `Position.ScheduleType`, `Competency.Category` | none (customers add their own) | unrestricted |
| `Examination.Status` | Active, Inactive | unrestricted |
| `TimeSlot.DayOfWeek`, `TimeSlot.Type`, the `TimeZone` fields | platform values | restricted |

**Record types:** VM ships no record types on its objects, but a customer may create some. Account
has Person Account record types.

**Note:** This is about picklist **values**. Rollup *field data* (DonorGiftSummary,
VolunteerInitiative) is still empty out of the box — a customer-built Data Processing Engine fills
it; see T12.

---

## Identity anchors

### Account (Person Account) — STANDARD
**Purpose:** The volunteer. VM **requires Person Accounts enabled**; a volunteer is a Person
Account (authenticated identity). The "Business Account" in the diagram is just how Salesforce
renders Person Accounts — ignore that variant (T1).
**VM fields:** NONE. Account is a "hero" entity, deliberately hard to extend; volunteer data hangs
off related/extension entities instead (T4). The VM related lists on Account (Person Examinations,
Person Competency, Job Position Assignments, Person Location Availabilities) are UI only — they let
an internal user see at a glance what a volunteer is involved with.
**Gotcha:** Do not look for volunteer fields on Account. Look for a related entity.

### Contact — STANDARD
**Purpose:** The **guest / pre-account** identity. Public Experience Cloud signup can create a
Contact with no Account yet. When the person creates/converts to a Person Account, later work links
to Account. Contact is the unauthenticated side of the boundary (T2, T10).
**VM fields:** NONE.
**Gotcha:** Guest contact forms can create the same person many times with no dedup — this "Contact
bloat" is *why* data-persisting entities require an authenticated Account (T10).

---

## Who-is-a-volunteer / engagement

### ConstituentRole — REUSED (as-is; Education/Industries)
**Purpose:** Marks a **Person Account as a volunteer**. This is the flag that scopes who engagement
rollups apply to.
**Key fields:** `RoleType` (picklist — ships with **"Volunteer"** plus Donor, Philanthropic
Prospect, Participant, T6); `Status` (picklist — Active, Former) + `EffectiveStartDate`/
`EffectiveEndDate` (standing active/inactive status, T5).
**Relationship intent:** Informational/standing identity marker. Do **not** confuse with
JobPositionAssignment (the operational act). ConstituentRole = "is a volunteer"; JPA = "did a job."
**Gotcha:** VM adds no fields; it relies entirely on `RoleType`, which already has the
"Volunteer" value out of the box (see the picklist table above).

### DonorGiftSummary — REUSED (+VM fields; Fundraising)
**Purpose:** Per-person engagement summary. VM added **volunteer** rollups here —
not on a new entity — because **a volunteer is assumed likely also a donor** (T14), so an org sees
giving + volunteering in one place. `Donor` is master-detail → Account.
**VM-gated fields (4; all rollups calculated by a scheduled Data Processing Engine job — NOT real-time):**
- `TotalVolunteerHours` (DOUBLE) — total hours volunteered.
- `TotalVolunJobPstnAsgnCnt` (INTEGER) — number of job position assignments.
- `FirstVolunJobPstnAsgntDt` (DATEONLY) — first volunteer shift date.
- `LastVolunJobPstnAsgntDate` (DATEONLY) — most recent volunteer shift date.
**CRITICAL — not shipped populated:** there is **no Data Processing Engine definition out of the
box**. The customer must create and schedule one to fill these (T12). They exist empty until then.
**CRITICAL — description correction:** the field's description text says these aggregate JPAs "related
to a volunteer initiative." That is **misleading** (T13). Real intent: **any JobPositionAssignment on the Person
Account** (VolunteerInitiative linkage is NOT a filter). These rollups only count JPAs that have an
`AssignedAccount` — see JobPositionAssignment.

---

## Matching profile (what the volunteer can do) — the Volunteer Matching feature (T9)

### PersonLocationAvailability (PLA) — NATIVE (generic-but-VM-only-customer, T11)
**Purpose:** The **when + where** a volunteer can serve. Volunteer-supplied via Experience Cloud or
other means ("I'm available at these times in these locations"). One leg of Volunteer Matching (T9).
**Key fields/rels:** `Account` (**required** — authenticated only, prevents guest bloat, T10/T16),
`Contact` (optional), `Location` (**required** — where), `OperatingHours` (optional — when, via its
TimeSlots), `UsageType` (**required** picklist — discriminator; PLA was built generic so any product
could adopt it, and VM is the only current customer; VM's records carry the VM usage value, T11).
**Chain:** TimeSlot → OperatingHours → PLA (+ Location).
**Gotcha:** Availability is **authenticated-only** by design (Account required).

### PersonCompetency — REUSED (as-is; Position Recruitment)
**Purpose:** A skill the volunteer **holds** (supply side of matching). Declared by the volunteer
via Experience Cloud OR set by an internal user.
**Key fields:** `Person` is polymorphic → **Account, Contact** — already supports Account,
so **VM added nothing** (contrast PersonExamination). `Competency` → Competency. `QualificationLevel`
(a number — **the field matching reads**); `ProficiencyLevel` (picklist — not read by matching);
`VerificationStatus`/`VerificationDate`/`VerificationSummary`.
**Verification fields are NOT used in matching.** `VerificationStatus`/`VerificationDate`/
`VerificationSummary` record whether a manager has vetted a claimed skill, but matching does **not**
read them — it does not weigh verified vs merely claimed. They are informational only.
**Gotcha — matching reads `QualificationLevel` only.** A volunteer matches when their
`PersonCompetency.QualificationLevel` is at or above the required level. `ProficiencyLevel` is never
read, so a skill recorded only with a ProficiencyLevel doesn't help a volunteer match.
**Don't use PersonCompetency for interests or preferences** (e.g. a cause the volunteer cares about):
it feeds matching, so a non-skill entry distorts who matches.

### PersonExamination — REUSED (+VM field; Public Sector)
**Purpose:** A credential/exam the volunteer **holds**.
**Not used by automated Matching today.** The Volunteer Matching feature does **not** read
PersonExamination — it is not a factor in automated matching as currently shipped. It is still
useful **internally**: a volunteer manager (user) can review a volunteer's held credentials to
find the right volunteer for a role and confirm they are qualified before assigning them.
**VM-gated field:** `Account` (FK → Account, org-gated). Native person link is **Contact** only; VM
added `Account` because credentials assigned via the Experience Cloud portal require an
**authenticated Person Account** (T16). Asymmetry vs PersonCompetency is purely mechanical
(PersonCompetency's polymorphic Person already had Account; this one didn't).
**Other rels:** `Contact` (required), `Examination` (FK).

### Competency — REUSED (as-is; Position Recruitment)
**Purpose:** The definition of a skill or expertise, shared by every record that refers to it. Used unchanged; no VM fields. The demand side
(PositionQualification and JobPositionQualification) and supply side (PersonCompetency) both point
at it.

### Examination — REUSED (as-is; Public Sector)
**Purpose:** The definition of an authorized exam or credential. Used unchanged; no VM fields. Both
the requirements (PositionQualification and JobPositionQualification) and the held credential
(PersonExamination) point at it — but none of these participate in automated matching (T9). An
Examination qualification is optional and informational: a manager reviews it, matching doesn't.

### TimeSlot — REUSED (as-is; Field Service)
**Purpose:** One **weekly-recurring availability window** (`DayOfWeek` + `StartTime` + `EndTime`) inside
an OperatingHours — the atomic unit of "I'm free then." Master-detail child of OperatingHours; times
are interpreted in the parent's `TimeZone`. `Type` is unused by VM. No VM fields.

### OperatingHours — REUSED (as-is; Field Service)
**Purpose:** A named set of weekly TimeSlots plus the `TimeZone` they're read in (it also has a
`Description`). A PLA points at one (FK `OperatingHours`, optional). An OperatingHours isn't tied to
a person or a Location: several PLAs with the same weekly windows can share one. No VM fields.

**Modeling availability:** **1 PLA = 1 Location + 1 OperatingHours**, and **one TimeSlot per weekly
window**. "Free Mon mornings and Sat afternoons at the SF site" → 1 PLA → 1 OperatingHours (TimeZone =
SF) → 2 TimeSlots. A **different Location is a separate PLA**.
**Matching (T9):** with a shift time filter, a TimeSlot must **contain** the shift window (day-of-week +
time-of-day); with none, matching falls back to Location-only. A PLA with no OperatingHours/TimeSlot is
dropped from time-based matches.

### Location — STANDARD
**Purpose:** The "where" — a physical/logical place. Referenced by PLA (availability) and by
JobPosition (where the job is, optional). No VM fields. The Location link on JobPosition is what ties
availability to opportunities in matching.

### Address — STANDARD
**Purpose:** The street address of a Location. Master-detail child of Location (deleting a Location
deletes its Addresses); a Location's `VisitorAddressId` points at the one shown to visitors. A
virtual Location may have none. `LocationType` and `AddressType` are unrestricted picklists; each ships
with Business Site. No VM fields.

---

## The work backbone (Position → JobPosition → Shift → Assignment)

### Position — REUSED (+VM field; Position Recruitment)
**Purpose:** The reusable **template** for a job to be done (T15). Carries PositionQualifications.
Does not itself carry a Location and does not link down to JobPosition (JobPosition links up).
`Status` is an unrestricted picklist (Upcoming, In Progress, Complete, Canceled, T24).
**VM-gated field:** `IsInternalApprovalRequired` (BOOLEAN). When true, signup for a JobPosition
under this Position needs internal approval. **The field is inert on its own** — it is a hook for
Salesforce **Approvals**; approval ultimately advances JobPositionAssignment.Status (T18, T26).
Placed at the **template** level on purpose: approval is a property of the role.

### PositionQualification — NATIVE
**Purpose:** A requirement the **template** demands (demand side of matching).
**Fields:** `Position` (master-detail, required), `Description`, `QualificationReferenceRecordId`
(polymorphic — **Competency or Examination only**, T17), `QualificationLevel` (number),
`ProficiencyLevel` (picklist — Beginner, Intermediate, Advanced). There is **no `Type` field**; what
a qualification refers to is the type of its QualificationReferenceRecord.
**Matching (T9):** uses QualificationLevel on Competency qualifications — "at or above the required
level," not just "has." Examination qualifications are ignored, a qualification with no
QualificationLevel is skipped, and ProficiencyLevel is never read.

### JobPosition — REUSED (+VM field; Position Recruitment)
**Purpose:** The concrete **posting** — optionally at a **Location** — that references its
**Position** via a **lookup** (restrict — a Position that still has postings can't be deleted; nothing
is copied from it). This is the operational anchor: **Shift and Assignment attach ONLY to
JobPosition, never Position** (T15). A JobPosition is required for any scheduling/matching.
**Qualifications are checked together, never copied.** Template-wide requirements live on the
Position; per-posting extras live on the JobPosition (`JobPositionQualification`). Matching checks a
Job Position's own qualifications and its Position's qualifications together, keeping the higher
level per Competency. Nothing is copied from the Position to the Job Position. The Position's
qualifications are *shown* on the JobPosition through a computed related list, which is why it can
look like inheritance.
**VM-gated field:** `VolunteerInitiative` (FK, org-gated) — optional link to the organizing
initiative (T21). `Location` (FK, optional) is what matching compares against PLA; a JobPosition
with no Location can't match on availability. `Status` is an unrestricted picklist (Upcoming, In
Progress, Complete, Canceled, T24).
**Required text fields:** `Name` and `Title` are both required and are separate fields. How to fill
them is records-create's job.

### JobPositionQualification — NATIVE
**Purpose:** A requirement **added to a specific posting** beyond the template's (e.g. an extra
certification required only at the SF location). Same shape as PositionQualification but
`JobPosition` (master-detail, required) + `QualificationReferenceRecordId` {Competency, Examination}.
**Canonical example:** one Position "Delivery Driver" (requires license) → two JobPositions NY & SF;
add a JobPositionQualification (certification) to SF only. NY needs license; SF needs license + cert.

### JobPositionShift — NATIVE
**Purpose:** The **concrete dated/timed occurrence** volunteers actually sign up for (e.g. "Tue
9–12 at SF"). Bottom of the backbone above the assignment.
**Key rels:** `JobPosition` (FK, **required**; deleting the JobPosition deletes its shifts);
`RecurrenceSchedule` (FK, optional).
**Scheduling fields — exact API names (a common guess-trap):** `StartDate`/`EndDate` (DATE) and
`StartTime`/`EndTime` (TIME) are **four separate date-and-time fields** plus `TimeZone` (picklist,
IANA names e.g. `America/Los_Angeles`). There is **NO `StartDateTime`/`EndDateTime`** on this object —
do not invent them. (The combined-datetime shape you may be reaching for is `ScheduledStartTime`/
`ScheduledEndTime` on the **different** object JobPositionAssignment.) `Name` is **auto-numbered**.
**Capacity model (T22, optional) — counted, never enforced:** `MaximumAttendeesCount` (the
intended limit); `PositionAssignmentCount` (recounted by a hook whenever a JPA is saved or deleted:
it counts the shift's JPAs with `DoesCountTowardShiftCapacity = true`, which defaults to true, in any
status — NOT a rollup); `RemainingCapacity` (formula = MAX(0, Max − Count) when both are set and Max
is above 0; otherwise blank). `Status` is an unrestricted picklist (Upcoming, In Progress, Complete,
Canceled, T24).
**Gotcha:** Nothing blocks a signup when a shift is full. A customer who wants a hard limit adds
their own validation rule.

### RecurrenceSchedule — STANDARD (platform scheduling)
**Purpose:** Out-of-the-box recurrence *pattern definition* (not a shift) that generates `JobPositionShift`
occurrences via `JobPositionShift.RecurrenceSchedule` (FK, optional). The UI owns it; records-create writes discrete `JobPositionShift` rows instead.
**Real fields (guess-trap — do NOT invent cadence fields):** cadence lives in `ScheduleFrequency` (req) + `ScheduleDayValue`; also `ProcessName` (req), `StartDate` (**DATETIME**, req), `NextScheduleDateTime` (req), plus `EndDate`/`TotalRecurrencesCount`/`CompletedScheduleCount`/`ReferenceRecordId` bookkeeping. **NO** `RecurrenceType`/`RecurrenceInterval`/`DayOfWeek`/`DayOfMonth`/`MaxOccurrences`.

### JobPositionAssignment (JPA) — NATIVE
**Purpose:** A person assigned to a job on a specific day — the **act of volunteering** and the
**single source of truth for hours served**. Everything engagement-related is measured from here.
**Person link — both optional:** `AssignedAccount` (Account) + `AssignedContact` (Contact). A guest
can create a Contact-only JPA; the org can later attach the Account (manual — **no automation out of the box**).
**`AssignedAccount` gates per-person (DGS) rollups only** (T2/T16): a JPA feeds a person's volunteer
totals only if it has an `AssignedAccount` — a Contact-only JPA doesn't roll up until an Account is
attached. **VolunteerInitiative rollups are unaffected** — they aggregate JPAs by
`RelatedVolunteerInitiative`, so the person link (`AssignedAccount` *or* `AssignedContact`) doesn't
matter for them.
**Parent links — all optional, any mix (T7):** `AssignedPositionShift` (JobPositionShift), `JobPosition`,
`RelatedVolunteerInitiative` (VolunteerInitiative; this FK is itself VM-gated). Standalone ad-hoc is
allowed — no parent is mandatory.
**Key fields:** `ScheduledStartTime`/`ScheduledEndTime` (what they signed up for) vs
`ActualStartTime`/`ActualEndTime` (what really happened) — commitment vs reality, kept separate on
purpose. `ActualDuration` (DOUBLE, hours) — the hours source for rollups; **NOT auto-computed out of the box**
because it must stay editable (auto-calc would overwrite manual edits) — customer can build their
own. `Status` (required picklist — Awaiting Approval, Upcoming, In Progress, Pending
Verification, Complete, Canceled, Absent; T24/T26). `DoesCountTowardShiftCapacity` (BOOLEAN,
default true, per-assignment) — so a waitlisted JPA needn't be counted (T22).

---

## Organizing anchor

### VolunteerInitiative (VI) — NATIVE
**Purpose:** "All volunteer activities within a single volunteering initiative" — the **logical
top-level** object. Optional parent of JobPosition/Shift/Assignment; ad-hoc work with no VI is
allowed (T21).
**Self-referential tree:** `ParentVolunteerInitiative` (FK → self, optional) — a real hierarchy
(e.g. "2026" → "Fall Food Drive" → "Thanksgiving Week"); rollups aggregate **up** to parents.
**Rollup fields (6; shipped but NOT populated — the customer builds a Data Processing Engine job, T12):**
`TotalVolunteerHours`, `TotalActiveVolunteerCount` (unique active volunteers meeting the customer's
configured eligibility), `AttendanceRate` (PERCENT — % who fulfilled commitments to date),
`OpenAssignmentCount`, `FilledAssignmentCount`, `TotalAssignmentCount` (open + filled).
`TotalActiveVolunteerCount`/`AttendanceRate` depend on **customer configuration** of which JPA
`Status` values count — VM ships no fixed eligibility store.
**Other fields:** `Status` (unrestricted picklist — Upcoming, In Progress, Complete, Canceled,
Postponed, Archived; T24), `StartDate`/`EndDate`,
`IsPublished` (BOOLEAN — intended to signal visibility in Experience Cloud, but **not automated
out of the box**: nothing flips it or gates visibility on it automatically — the customer wires it into their
site). VI being "top" is a data-model statement;
customers can build their Experience Cloud site to let volunteers browse JobPositions/Shifts however.

---

## Cross-product bridge (requires two clouds)

### PositionBenefit — NATIVE (requires VM AND Benefit Management)
**Purpose:** Bridges Volunteering ↔ Benefit Management: **volunteers provide a service that
beneficiaries receive as a Benefit** (T19). NOT perks for volunteers. Ties a Position to the
Benefits that position provides.
**Compound gating (T20):** `userHasVolunteerManagement && userHasBenefitManagement` — unusable
unless BOTH clouds are enabled — the org needs Benefit Management as well as VM. The `&&` signals a
deliberate cross-product bridge.
**Key rels:** `Position` (master-detail, required — attaches to the **template**, since all its
JobPositions provide the same service); `Benefit` (lookup, required) → **Benefit is OUT OF SCOPE**
(Program Management). Treat Benefit as an external dependency; do not model it.

---

## Entities to IGNORE

### ContactProfile — REUSED (Education), but IGNORE
Appears in the diagram, but VM adds nothing to it (no VM-gated fields). Treat as noise; do not model.
