# Plan Output

**When to load:** Workflow steps 6–8, after every configuration decision has an answer.

**Purpose:** what goes in message 1 (the plan) and message 2 (the additional configuration and the create question), and what is handed to `nonprofit-volunteer-management-records-create` on yes. The consent rules and the `Reuse-check:` values are in SKILL.md.

---

## Message 1 — the plan

### Summary table

One row per planned record. The table is both the record of the user's decisions and what records-create works from, so the rest of the message never repeats it.

| Column | What goes in it |
|---|---|
| Record | The object, written out (Volunteer Initiative, Job Position, …) |
| Name | The record's name, or the shift pattern. Use the user's names; if one isn't given yet, propose a plain name rather than a bracketed placeholder |
| Reuse or New | **Reuse** for an existing record (its name is in Name; never show an Id), otherwise **New** |
| Belongs to | The parent records ("Weekly Food Pantry, at Eastside Pantry"), or "—" for a record that stands alone |
| Decision | A few words: what the user decided and why, using only values from the interview (capacity, schedule pattern, onsite or virtual, required level, no parent, no template). Never a field name, never "TBD" |

Rows, in this order, for the records the plan includes: Volunteer Initiative, Location, Competency, Examination, Position, Position Qualification, Job Position, Job Position Qualification, Job Position Shift.

**Example:**

| Record | Name | Reuse or New | Belongs to | Decision |
|---|---|---|---|---|
| Volunteer Initiative | Weekly Food Pantry | New | — | One program, no parent |
| Location | Eastside Pantry | Reuse | — | Onsite; already in your org |
| Competency | Driver's License | Reuse | — | Drivers transport groceries |
| Job Position | Driver | New | Weekly Food Pantry, at Eastside Pantry | No template; only this program uses the role |
| Job Position Qualification | Driver's License | New | Driver | Required level 1 |
| Job Position Shift | Saturdays 9:00–12:00 | New | Driver | 12 weekly shifts, up to 5 volunteers each |

### After the table

Each part below is one or two lines, and only when it applies. Don't restate the table, add a record diagram, or add sections beyond these.

### Left out on purpose

One line naming what the user decided against (a parent Volunteer Initiative, a Position template, shifts, qualifications), and that each can be added later without recreating these records. Leave it out when the plan includes all of them.

### Schedule details

One line per shift series, with what records-create needs to build it: the pattern (one-time, weekly on ‹days›, monthly on ‹day›), the time windows (per day when they differ), the start date and either the end date or the number of shifts, the time zone, and the volunteers per shift if the user set a maximum. Write only what the user said; a date or time zone they haven't given goes under Outstanding inputs, never an assumed one. Never list the individual shift dates.

Example: *Driver — weekly on Saturdays, 9:00–12:00, from 3 Oct 2026 for 12 shifts, Eastern Time, up to 5 volunteers.*

### What these records don't do on their own

One short line for each limit below that applies to this plan, each with what the customer adds to close it. Leave the section out when none applies. These lines are in the plan, not only in message 2, because the user may skip the additional configuration.

| When the plan includes… | Line |
|---|---|
| A maximum number of volunteers per shift | Sign-ups are counted against the maximum but never blocked when a shift is full. To stop sign-ups to a full shift, add a validation rule. |
| Qualifications on a Position or Job Position | Qualifications guide matching only. Nothing stops a volunteer who doesn't meet them from signing up unless you add a validation rule. |
| An Examination as a qualification | Matching doesn't use Examinations; they're for manual checks and compliance tracking. |
| A Position that requires internal approval | The approval setting does nothing on its own. Assignments wait for approval only once you build a Salesforce Approvals process that updates their status. |
| Tracking volunteer hours or engagement totals, when the user asked for it | The engagement and hours totals stay empty until you build Data Processing Engine definitions for them. |

### Outstanding inputs

One line listing any value a planned record needs that the user hasn't decided yet, e.g. "the Downtown Center's address, the series start date". records-create asks for these when it writes. Leave it out when nothing is outstanding. Don't list the out-of-scope work from message 2 here.

### Reuse-check line

Add the one `Reuse-check:` line from SKILL.md under the table.

### Completeness check (before sending)

- Every child has its parent in the plan or the org: Job Position → Volunteer Initiative, Position Qualification → Position and Competency, Job Position Qualification → Job Position and Competency, Job Position Shift → Job Position.
- Nothing points at a record that is neither planned nor reused.
- The plan matches what the user said: shifts for a shift-based program, qualifications for skilled roles, an end date or count for every recurring schedule.
- Raise any gap before asking: "You described a skilled Team Lead role, but no qualification is planned for it. Do you want to add one?"

End message 1 with this one question and nothing after it: **"Do you want to see the additional configuration and extensions you can set up beyond these records?"**

---

## Message 2 — additional configuration and the create question

Send after the user answers, never with the plan.

- **On yes:** present both parts below in full, as information only. Say plainly that building these items is outside what this skill does and is the user's to own. Don't say "not building these now" or "we'll set these up later". End with **"Do you want to create the records from the plan?"**
- **On no:** send only **"Do you want to create the records from the plan?"** A no here (including "skip that") declines the additional configuration only; it is never an answer to the create question.

On a yes to the create question, hand off (below). On no, stop.

### Additional Configuration Considerations

Share this checklist as written:

**Foundational configuration**

- Build a way for volunteers to sign up: an internal process, an Experience Cloud portal, or another volunteer-facing channel.
- Automate communication and engagement: Flow for confirmations, reminders and follow-ups; Notification Builder for alerts; Marketing Cloud for journeys and campaigns.
- Confirm or update the Status values for Volunteer Initiatives, Job Positions, Job Position Shifts and Job Position Assignments (with Stage Management if you want it).
- Build reports and dashboards for your volunteer programs.

**Advanced configuration**

- Data and metrics:
  - Build Data Processing Engine definitions for the volunteer-engagement rollup fields on Donor Gift Summary.
  - If you add engagement rollups, show the Donor Gift Summary record on the Person Account page with a related record component. A related list won't work, because each person has one summary record.
  - Build Data Processing Engine definitions for the Volunteer Initiative metric fields.
- Validation and approvals:
  - If you set capacity, add a validation rule to block signups to a full shift. Capacity is counted, never enforced.
  - If you use qualifications, add a validation rule to block signups by volunteers who don't meet them.
  - If a Position requires internal approval, set up Salesforce Approvals.
- Data migration:
  - Add external ID fields to the objects you'll import data into.
- To support volunteer groups, consider turning on Group Membership and "Allow users to relate a contact to multiple accounts".

### Extensions

| Extension | What it is |
|---|---|
| Experience Cloud Portal | Sign-up and registration for volunteers |
| Form Framework | Registration and application forms, built on Action Plans. A simple registration form is enough if complex applications aren't needed |
| Action Plans | Templated task checklists, such as onboarding → background check, orientation and training |
| Stage Management | Tracks volunteers through lifecycle stages |
| Position Benefits | Links a Position to Program Management benefits; not needed for core Volunteer Management |
| Constituent Role | Tags a Person Account as a volunteer |
| Agentforce Shift Capacity and Coverage | An Agentforce subagent that reports on shift capacity and coverage. Whether it's available depends on your org's licensing and setup |

Show the Agentforce row as written; don't say the subagent is available in this org.

---

## Handoff to records-create (only on yes)

Pass:

- the summary table;
- the Id of each reused record (kept out of the table the user sees);
- the schedule details;
- the outstanding inputs;
- the `Reuse-check:` line.

records-create sets every field value, decides the write order, checks for shifts that already exist, and asks the user to confirm each object before writing.
