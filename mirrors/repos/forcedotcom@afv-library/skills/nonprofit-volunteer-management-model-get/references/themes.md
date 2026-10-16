# Design Principles (Themes) — Volunteer Management

The recurring principles that explain *why* the model is shaped the way it is. `entities.md` and
`relationships.md` cite these by number. Read these to reason about parts of the model this skill
doesn't spell out explicitly — the principles generalize.

## Identity & the authenticated boundary

**T1 — The volunteer is a Person Account.** Person Accounts must be enabled (hard prerequisite).
The "Business Account" box in the diagram is just how Salesforce renders Person Accounts — ignore
that variant.

**T2 — The authenticated boundary drives the Contact-vs-Account split.** Contact-only = guest /
pre-account (public Experience Cloud signup). Person Account = authenticated volunteer after
creation/conversion. Entities choose Contact vs Account by whether the flow can be unauthenticated.
Assignment supports both (guest → convert); history/rollup entities require Account.

**T3 — Permission tiers mirror the boundary.** `userHasVolunteerManagement` = internal staff;
`userHasVolunteerManagementCmtyAccess` = authenticated community volunteer;
`userHasGuestVolunteerManagementCmtyAccess` = unauthenticated guest; `orgHasVolunteerManagement` =
org-level enablement (API access, related lists). Map any gate to these actor types.

**T10 — Guest Contact bloat is *why* the boundary exists.** Guest forms can create the same person's
Contact repeatedly with no dedup. To avoid record bloat, entities that persist a volunteer's own
data (availability, credentials, history) require an authenticated Account. This is the mechanical
reason behind T2.

**T16 — VM insists on Person Account at the portal boundary.** Where VM persists volunteer-owned
records via Experience Cloud (PersonExamination, PLA), it requires an authenticated Account — even
adding an Account link to a borrowed entity that only had Contact (PersonExamination). PersonCompetency
needed nothing because its polymorphic `Person` already included Account.

## Reuse philosophy

**T4 — Account is a "hero" entity.** Deliberately hard to extend with fields, so product data hangs
off related/extension entities rather than new Account/Contact fields. This explains the whole
"borrowed entity + related entity" shape of the model. VM adds zero fields to Account/Contact.

**T14 — Volunteer ≈ Donor.** VM assumes a volunteer is likely also a donor, so volunteer engagement
data is co-located on the Fundraising DonorGiftSummary rather than a new entity. Reinforces T4.

**T11 — "Generic entity, single current customer."** Some native-looking entities (PLA) were built
generic so any product could adopt them; VM is the only current customer. A UsageType/discriminator
field keeps products' records from colliding — set it to the VM value.

**T17 — Polymorphic scopes are deliberately narrow.** QualificationReferenceRecord supports
{Competency, Examination} only — the polymorphic lookup permits exactly those two targets. Reference
only the domains actually in a polymorphic set; do not assume other qualification types are targetable.

**T20 — Compound (AND) gating signals a cross-product bridge.** Most entities use OR gating (any of
several clouds can access — plain reuse). PositionBenefit uses AND (`VM && BenefitManagement`) — a
deliberate bridge requiring both products. When you see `&&` across clouds, it's a cross-product
feature, not reuse.

## Structural patterns

**T5 — Standing/informational vs operational/per-occurrence.** The model separates "who someone IS"
(ConstituentRole — is-a-volunteer, active/inactive, dates) from "what someone DID"
(JobPositionAssignment — a specific job, place, date; one record per occurrence).

**T7 — Optional / flexible parentage.** Many links are intentionally optional and mix-and-match
rather than an enforced hierarchy (e.g. JPA → Shift / JobPosition / VolunteerInitiative, any mix or
none). The model favors flexibility; structure-generate helps the user decide the shape.

**T15 — Position → JobPosition template model is the backbone.** Position = reusable template
(+ PositionQualifications); JobPosition = concrete posting (optionally at a Location) that
**references** the template via a lookup and can add JobPositionQualifications. A Job Position's own
qualifications and its Position's qualifications are checked together, keeping the higher level per
Competency. Nothing is copied from the Position to the Job Position (see `entities.md` → JobPosition). Shift &
Assignment attach ONLY to JobPosition. One template → many localized postings with location-specific
extra requirements.

**T21 — VolunteerInitiative = optional top-level parent.** VI is the intended parent of
JobPosition/Shift/Assignment and is self-referential (a hierarchical tree), but linkage is
deliberately optional — ad-hoc work with no VI is allowed. VI is the organizing anchor when you want
one, not a required root.

## "Mechanism shipped, enforcement/config is the customer's"

**T6 — Most picklists ship with values.** Most of VM's picklists have values out of the box —
including `ConstituentRole.RoleType = "Volunteer"` (see the picklist table in `entities.md`).
Position Type, Sensitivity and Schedule Type and Competency Category ship empty. When a needed
value already ships, tell the user it's there; otherwise an admin can add it. Only the platform
picklists (TimeZone, TimeSlot DayOfWeek and Type) can't take a new value.

**T12 — Some rollups/features are NOT shipped populated.** DonorGiftSummary's 4 fields and
VolunteerInitiative's 6 fields have no Data Processing Engine definition out of the box — the
customer creates and schedules one. Fields exist empty until then. Real-time isn't feasible at this volume.

**T18 — Fields as hooks into other platform features.** Some VM fields are inert flags meant to be
wired into existing features. `Position.IsInternalApprovalRequired` → Salesforce Approvals. The
`Status` picklists → Stage Management. These need configuration to do anything.

**T22 — Capacity is counted, never enforced.** A hook recounts `JobPositionShift.PositionAssignmentCount`
on every JPA save and delete (JPAs with `DoesCountTowardShiftCapacity = true`); `RemainingCapacity` is
a formula. Nothing blocks a signup when a shift is full — a customer who wants a hard limit adds a
validation rule.

**T23 — VM decouples RecurrenceSchedule and pre-generates all shifts.** Unlike other products that
use the shared recurrence engine for dynamic generation, VM treats RecurrenceSchedule as purely
informational and ships a feature that materializes every JobPositionShift upfront (time-bounded,
capped). Recurrence is a generation-time convenience, not runtime behavior.

**T24 — The Status lifecycles are independent.** VI / Position / JobPosition / JobPositionShift /
JobPositionAssignment each have their own Status picklist with values that ship out of the box (see
the picklist table in `entities.md`). There is **no cross-entity propagation** (closing a JobPosition
does not auto-close its Shifts; a JPA "Complete" doesn't auto-feed VI — that's the Data Processing
Engine job's work). No Status is "primary" — treat each as separate.

**T25 — Stage Management is the platform feature the Status picklists plug into.** It enables
automations as a Status progresses through stages. A Status field alone is just a picklist; registering it with
Stage Management makes it a governed lifecycle. VM ships the field as the hook.

**T26 — The approval flag ultimately plays out on JPA.Status.** `Position.IsInternalApprovalRequired`
(flag on the template) → Salesforce Approvals (customer-wired) → JPA.Status advanced by Stage
Management (e.g. "Awaiting Approval" → "Upcoming"). VM ships the flag and the Status values; the
customer still wires the Approvals process and any Stage Management automation.

## Trust intent over doc text

**T13 — Field description text can be misleading.** Capture intended behavior, and note corrections
where shipped text misleads. Known case: DonorGiftSummary rollup fields say "related to a volunteer
initiative" — the real intent is "any JPA related to the Person Account" (VolunteerInitiative is NOT
a filter).

## Features (composite themes)

**T8 — Deprecated (was: Corporate / group volunteering).** Removed — VM has no supported solution
for corporate/group volunteering yet. Number retained to keep existing theme references stable; do
not reuse it. Do not advise agents to model corporate/group volunteering (e.g. via
`ConstituentRole.Institution`).

**T9 — Volunteer Matching.** Matches volunteers to opportunities on two axes: **held competency**
(PersonCompetency vs Position/JobPosition Qualification requirements) and **availability**
(PersonLocationAvailability ↔ JobPosition.Location + TimeSlot time-window containment). Matching
uses QualificationLevel on Competency qualifications; ProficiencyLevel is never read. A Job
Position's own qualifications and its Position's qualifications are checked together, keeping the
higher level per Competency. **Competency-only:** matching reads neither PersonExamination nor
Examination qualifications. Examination is for manual/internal qualification.

**T19 — Volunteering ↔ Benefit Management bridge.** Volunteers provide a service beneficiaries
receive as a Benefit. PositionBenefit is the bridge (Position → Benefit), requiring both clouds.
Benefit itself is out-of-scope (Program Management) — external dependency.
