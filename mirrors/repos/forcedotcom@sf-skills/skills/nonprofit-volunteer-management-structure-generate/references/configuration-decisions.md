# Configuration Decisions

**When to load:** Workflow step 4, after the discovery summary is confirmed.

**Purpose:** what to decide from the discovery answers, in order: Locations, parent Volunteer Initiative, Position template, shifts, recurrence, qualifications. For entity and field meaning, see `nonprofit-volunteer-management-model-get`. Field values are set by `nonprofit-volunteer-management-records-create`.

---

## How to run a decision turn

For each decision, use one turn and then wait:

1. **What I heard:** one sentence from the discovery answers.
2. **Options:** usually two, in the user's words.
3. **Recommendation and why**, including what the other option would cost later (see "Changing it later").
4. **Platform behavior:** only the one that should change the choice.
5. **Ask:** "Which do you want?", not "Does this whole plan look right?"

Don't stop to ask about Status, publishing or record names; records-create handles those. Recommend the simpler option, but don't treat it as accepted until the user picks it.

---

## Locations

**Options:** one Location / one Location per site / a "Virtual" Location.

**Default:** the Locations the discovery answers describe.

- Ask only for each Location's name, address, and whether it's onsite or virtual. records-create creates the address record and asks for anything else.
- A Job Position doesn't need a Location. Matching volunteers by location does, so virtual roles usually get a "Virtual" Location.
- For a program at several sites, plan one Location per site, and one Job Position per site where volunteers sign up per site.
- Run the Location reuse check before recommending; an existing site is usually the one to reuse.

**Reference:** model-get → Location, and Feature: Volunteer Matching.

---

## Parent Volunteer Initiative

**Ask:** "How many Volunteer Initiatives do you need, and should they be connected?"

**Default:** separate initiatives with no parent. Adding a parent later doesn't disturb anything.

**Check the org first.** Run the Volunteer Initiative reuse check before this turn. If the org already has initiatives that fit, raise them here: "Your org already has separate per-site Volunteer Initiatives. Do you want to extend those, or start a new shared one?" Never recommend a structure that conflicts with what's already there.

**Offer a parent (as an option, not a strong recommendation) when:**

- the programs share an umbrella identity;
- the user describes sub-programs and doesn't want them all in one initiative told apart only by role;
- the same program runs at several sites with a coordinator at each (parent = program, children = sites).

**Platform behaviors:**

- Publishing and Status don't pass down; each initiative is published and updated on its own.
- The rollup fields exist but stay empty until the customer builds Data Processing Engine automation.
- A Job Position belongs to one Volunteer Initiative.
- Sharing doesn't pass down the hierarchy.
- A hierarchy holds up to 1,000 records and 5 levels.

Common groupings for a parent: program type, season, location, funding source.

**Reference:** model-get → VolunteerInitiative.

---

## Position template

**Default:** no Position, unless the same role is reused across Job Positions with shared requirements.

**Use a Position when:**

- the same role is posted at several locations or in several programs;
- its qualifications should be defined once and used in matching for every Job Position that uses it;
- the role needs internal approval;
- the role links to a Program Management benefit.

**Skip it when** the role is unique to one posting, or there's no need to share qualifications.

**How to ask:**

- *Leaning toward it:* "You described the same role at two locations, so I'd recommend a Position template. Its qualifications are defined once, and both Job Positions use them in matching. Do you want a template?"
- *Leaning against it:* "This role only exists in one program, so I'd skip the Position template and put the qualifications on the Job Position. You can add a template later. OK to skip?"

**Platform behaviors:**

- A Position's only built-in effect on its Job Positions is in matching. Anything else the customer wants passed down needs their own automation.
- "Internal approval required" is a flag only. It does nothing until the customer builds an approval process that updates the assignment's status.

Run the Position reuse check before recommending.

**Reference:** model-get → Position, JobPosition.

---

## Shifts

**Default:** no shifts, unless volunteers sign up for set times.

**Use shifts when** volunteers sign up for specific dates and times, need a per-slot volunteer count, or the customer wants the Find Unfilled Shifts action.

**No shifts when** volunteering is flexible ("come when you can") and there are no slots to fill.

Assignments don't have to belong to a shift, a Job Position or an initiative; ad-hoc assignments are valid.

**Reference:** model-get → JobPositionShift.

---

## Recurrence

**Default:** none, unless the schedule repeats.

**Recurring** fits a regular weekly or monthly pattern ("every Tuesday 9–12"). One-time events and irregular dates don't need it.

**Collect the schedule details** for records-create (see `plan-output.md` → "Schedule details"): the pattern, the time window for each day (they may differ by day; don't flatten them into one), the start date, the end date or the number of shifts, and the time zone. The series always has an end: if the user gives neither an end date nor a count, ask for one.

**Platform behavior:** every shift in the series is created up front as its own record. Recurrence is a convenience when the shifts are created; nothing repeats at runtime.

If the Job Position already exists, plan the schedule the user wants anyway. records-create checks which of those shifts already exist and creates only the missing ones.

**Reference:** model-get → Feature: Recurrence.

---

## Qualifications

**Default:** none, unless the discovery answers showed skilled roles.

| Approach | When |
|---|---|
| On the Position (Position Qualification) | The requirement applies wherever the role is used |
| On the Job Position (Job Position Qualification) | The requirement is specific to one posting |
| Both | Shared requirements on the Position, plus posting-specific extras on the Job Position. Recommended when both apply |
| None | General volunteering, or roles filled by people who are already vetted |

Matching uses QualificationLevel on Competency qualifications. A Job Position's own qualifications and its Position's qualifications are checked together, keeping the higher level per Competency. Nothing is copied from the Position to the Job Position.

**Example:** the Position "Delivery Driver" requires a driver's license. The Job Position at the San Francisco site also requires a local certification. The New York Job Position needs nothing extra.

- Don't repeat a Position's qualifications on its Job Positions; matching already checks both.
- Requirements can vary by program as well as by location.
- Ask for the required level of each Competency qualification; a qualification without one is skipped by matching. Proficiency labels (Beginner, Intermediate, Advanced) are descriptive only and not used in matching.
- **Examinations** are optional. Matching doesn't use them; they're for manual checks and compliance tracking. A requirement a volunteer must meet before being matched (a cleared background check, a completed training) is a Competency with a required level, not an Examination.
- Also ask whether a requirement belongs on the role or on the person. A volunteer's own competencies are out of scope for this skill.
- Run the Competency and Examination reuse checks before recommending.

**Reference:** model-get → PositionQualification, JobPositionQualification, Feature: Volunteer Matching.

---

## Changing it later

Use this for the "what the other option costs later" part of a decision turn.

| Effort | Examples |
|---|---|
| Easy: add later | A parent initiative, a Position template, shifts, qualifications, Locations. Nothing that exists breaks |
| Some manual work | Moving a Job Position to another initiative, restructuring the hierarchy, moving a requirement between the Position and the Job Position |
| Hard: review the impact first | Changing a Job Position that already has shifts or assignments. Changing a Position's qualifications changes matching for every Job Position that uses it |
