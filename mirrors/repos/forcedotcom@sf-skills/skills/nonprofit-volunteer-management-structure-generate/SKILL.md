---
name: nonprofit-volunteer-management-structure-generate
description: "Use this skill to plan a Salesforce Nonprofit Cloud Volunteer Management (VM) program before anything is created: it interviews the user about their programs, sites, volunteer roles, requirements, and shift schedules, checks the org read-only for records to reuse, and presents a plan of the records the program needs. It never writes; on the user's yes it hands the plan to nonprofit-volunteer-management-records-create. TRIGGER when a user wants to plan, design, or structure a VM program, or asks \"what records do we need\" or \"how should we model this program\". DO NOT TRIGGER to explain what a VM object or field is for (use nonprofit-volunteer-management-model-get), to write records (use nonprofit-volunteer-management-records-create), to enable Volunteer Management in an org, for per-person records (JobPositionAssignment, PersonLocationAvailability, PersonCompetency / PersonExamination, ConstituentRole), or for NPSP / Volunteers for Salesforce (V4S), which is unsupported."
metadata:
  version: "1.2"
  domains: ["Nonprofit"]
  relatedSkills:
    - "nonprofit-volunteer-management-model-get"
    - "nonprofit-volunteer-management-records-create"
  cliTools:
    - tool: ["sf"]
      semver: ">=2.0.0"
  accessCheck: "(OrgPermissions.VolunteerManagement) && (OrgPreferences.VolunteerManagementEnabled)"
---

# Nonprofit Cloud Volunteer Management — Structure Planning

This skill turns a description of a volunteer program ("I run a weekly food pantry with team leads and general volunteers") into a plan of Volunteer Management records: the Volunteer Initiatives, Locations, Competencies, Examinations, Positions, Job Positions, their qualifications, and Job Position Shift series the program needs. It asks the discovery questions, walks through each configuration decision, checks the org for records it can reuse, and presents the plan. It adds only the structure the program needs.

## Hard rules

- **Never delete records.** No delete, rollback or cleanup of any kind. If a write fails part-way, report what was created and what wasn't; never undo it.
- **Never act on NPSP or Volunteers for Salesforce (V4S).** That legacy package is unsupported here. Say so and stop.
- **No acronyms or internal labels in what the user sees.** Write out Volunteer Initiative, Job Position, Job Position Shift, Job Position Assignment, Position Qualification, Job Position Qualification, Data Processing Engine, and "out of the box". Never show internal step or section labels, or a record's Id: name a reused record by its name; its Id goes only in the handoff.
- **Never create records.** This skill plans. It hands the plan to `nonprofit-volunteer-management-records-create` only after the user answers yes to "Do you want to create the records from the plan?".

## Mechanism

Org calls go through the connection the session has: the headless-360 tools (`dispatch_readonly` only; this skill never writes) or an authenticated Salesforce CLI. Both return the same results at API v67.0. Tell the user which one is in use. If neither is connected, stop and ask the user to connect one; never guess an org result. The exact call for each step, in both forms, is in `references/mcp-invocation.md`.

This skill only reads. With no org connection, planning still completes; see step 1.

## Scope

- **In scope:** the discovery interview, the configuration decisions, reuse checks against the org, the plan summary, and handing a confirmed plan to `nonprofit-volunteer-management-records-create`.
- **Out of scope:** writing records (records-create), setting field values (records-create's `field-guide.md`), explaining what an entity or field means (`nonprofit-volunteer-management-model-get`), turning Volunteer Management on, and day-to-day operations such as matching, assignments, or a volunteer's own availability and qualifications. Operating Hours and Time Slots are not planned here; records-create creates them only when the user asks for them.

## Required Inputs

- **The user's description of the program.** The interview fills in the rest.
- **An org connection (optional).** Used only for reads, and only after the user agrees.

**Defaults (Start Simple).** Recommend these unless the interview shows a clear need for more:

- One Volunteer Initiative, with no parent.
- No Position template; qualifications go on the Job Position unless the role is reused.
- One Job Position for the tasks the same volunteers do at one place ("greet guests and help set up" is one Job Position). Split it only when the user wants separate sign-up or tracking per task.
- No shifts unless volunteers sign up for set times.

A default is a recommendation. It is decided only when the user picks it.

When the user arrives with the decisions already made, still read `references/configuration-decisions.md` and `references/plan-output.md` before writing the plan; they hold the platform behaviors the plan has to state correctly.

## Workflow

1. **Ask for read consent.** Before the first org read, say what you'll read (the Volunteer Management check and the reuse checks) and why, and get a yes. Warn that declining means existing records can't be checked, so duplicates may be created. If the user declines, or no org is connected, skip steps 2 and 5 and keep planning; the plan is stamped `Reuse-check: DECLINED`. If the user agrees to some reads but not others, the plan is also stamped `DECLINED`. Without the read, a record the user says already exists stays New in the table; its Reason says the user named it and records-create finds and reuses it before writing.
2. **Check that Volunteer Management is on**, once, after the user agrees to the org read (calls in `references/mcp-invocation.md`):
   1. Read the org preference `VolunteerManagementEnabled`. `true` → on. `false` or 404 → off: stop and tell the user an admin turns it on in Setup → Volunteer Management Settings. 403 → the user has no access to org settings: stop and say so.
   2. Describe `VolunteerInitiative`. 200 → the user can see the Volunteer Management objects. Any error → stop and tell the user they need the Manage Volunteer Data permission set. Don't look up permission-set assignments beforehand.
3. **Run the discovery interview** (`references/discovery-interview.md`). Ask about these topics in this order, whatever the program's complexity: programs and how they relate, locations, roles, delivery format (onsite, virtual, hybrid), qualifications, scheduling, capacity. Stay on one topic at a time. Note anything the user says early about a later topic, but don't jump ahead. Finish every topic before deciding anything, then summarize what you heard and ask the user to correct it.
4. **Walk the configuration decisions** (`references/configuration-decisions.md`), one per turn: Locations, parent Volunteer Initiative, Position template, shifts or no shifts, recurrence, and qualifications (including whether a requirement belongs on the role or on the person). For each, say what you heard, give the options, recommend one with the reason, name the platform behavior that matters, and ask. Wait for an explicit answer before the next decision.
5. **Check for existing records** before planning anything as New. Run each check when its decision comes up, so the user decides with the org in view. The Volunteer Initiative check runs before the parent Volunteer Initiative decision. Check every planned record by its natural key:

   | Record | Natural key |
   |---|---|
   | Volunteer Initiative, Location, Position, Competency, Examination | Name |
   | Job Position | Name + Volunteer Initiative |

   Filter each query to the names in the plan, never the whole object. Escape apostrophes in names with a backslash. Locations, Competencies, Examinations and Positions are meant to be shared across programs, so look for them by the distinctive word stems too, and run the query again with a shorter stem when a near-match could be worded differently. When a match turns up, show it and ask whether it's the record the user means. Job Positions always get the check: if the Volunteer Initiative is New, check by name only; a match belongs to another initiative, so the Job Position is still New and records-create checks again before writing.
6. **Present the plan (message 1).** Read `references/plan-output.md` and use its template: the summary table, then one or two lines each, only where they apply, for what was left out on purpose, the schedule, what these records don't do on their own, and outstanding inputs, then the `Reuse-check:` line. Check that the plan is complete first. Don't restate the table or add other sections. End the message with exactly one question: "Do you want to see the additional configuration and extensions you can set up beyond these records?"
7. **Offer the additional configuration (message 2).** Send this only after the user answers, and never in the same response as the plan. On yes, show the Additional Configuration Considerations checklist and the Extensions table from `references/plan-output.md`, both in full and both informational, then ask "Do you want to create the records from the plan?" as the last line. On no ("no", "skip that"), the answer covers only the additional configuration, not the records: reply with only "Do you want to create the records from the plan?" and wait. Never treat it as a no to creating the records. If the user asks for changes instead, update the plan and repeat step 6.
8. **Act on the create answer.** On yes, hand the plan to `nonprofit-volunteer-management-records-create`. On no, or if the user wanted only the plan, stop. If the user asks for changes instead, update the plan and repeat step 6.

**Reuse-check line.** Every plan carries exactly one of these:

- `Reuse-check: RESOLVED — org read; the Reuse/New mapping is authoritative`
- `Reuse-check: DECLINED — org not read (or read only in part); every unchecked record planned as New; records-create checks before writing`

If the line is missing or unrecognized, records-create runs its own reuse checks.

## Rules / Constraints

| Constraint | Rationale |
|---|---|
| One read consent before any org read; declining doesn't stop planning | The user controls access to their org. Without the read, duplicates are possible, so the plan says so |
| Ask the discovery topics in order and finish them all before deciding anything | Later answers often change earlier decisions |
| One configuration decision per turn: recommend, then ask | These are the user's decisions: how many volunteers is too many, which qualifications matter, whether a program needs its own initiative |
| Never plan a record as New without checking the org first (unless the read was declined) | Orgs collect Volunteer Management records over time; a duplicate splits the data |
| Filter every reuse query to the planned names; never read a whole object | A reuse check looks for matches. It is not an inventory of the org |
| Presenting the plan isn't consent; an earlier "go ahead" isn't consent | Only a yes to "Do you want to create the records from the plan?" lets records-create write |
| Offer the checklist and Extensions after the plan and before the create question; on yes, show them in full, as information only. Don't offer to build them or suggest they'll be done later | The user owns that work. Shown with the plan it buries the question; shown after the create answer it scrolls away under the records step |
| Every limit that applies to a planned record goes in the plan itself, under "What these records don't do on their own" | A user who skips the additional configuration still needs to know a maximum isn't enforced or an approval flag does nothing on its own |
| A shift's maximum is counted, never enforced: nothing blocks a sign-up to a full shift until the customer adds a validation rule. Never say the platform stops sign-ups on its own | Saying the cap stops sign-ups leaves the user with overbooked shifts |
| Volunteer matching uses only Competency qualifications with a required level. A requirement a volunteer must meet before being matched (a background check, a training) is a Competency; an Examination is for manual checks and compliance tracking only | An Examination never affects who is matched |
| Every Position Qualification or Job Position Qualification has a row for the Competency or Examination it points at, Reuse or New | A qualification can't be created without the record it references |
| The plan records decisions, not fields. Never write a field name or "TBD" in it | records-create sets field values from its field guide and asks for anything missing |
| Hand schedule details to records-create; don't plan Operating Hours, Time Slots or individual shifts for an existing Job Position | records-create builds the shift series and checks for shifts that already exist |
| Don't change existing records, org settings, users or permissions. Point out a misconfigured record, but leave it as it is | This skill only reads |

## Output Expectations

- **Message 1:** the plan summary table (Record · Name · Reuse or New · Belongs to · Decision); then, each in a line or two and only when it applies, what was left out on purpose, one line per shift series, what these records don't do on their own, and the outstanding inputs; the `Reuse-check:` line; and "Do you want to see the additional configuration and extensions you can set up beyond these records?" as the last line. Nothing in the message repeats the table.
- **Message 2:** on yes, the Additional Configuration Considerations checklist and the Extensions table in full; either way, "Do you want to create the records from the plan?" as the last line.
- **Handoff (only on yes):** the plan table, the Id of each reused record, the schedule details, the outstanding inputs and the `Reuse-check:` line, passed to `nonprofit-volunteer-management-records-create`.

## Cross-Skill Integration

- **`nonprofit-volunteer-management-model-get`**: what an entity, field or feature means. Use it when the user asks "what is…" during planning.
- **`nonprofit-volunteer-management-records-create`**: writes the confirmed plan. It owns field values, the write order, the existing-shift check, and Operating Hours and Time Slots.

## Reference File Index

| File | Used in |
|---|---|
| `references/mcp-invocation.md` | Steps 2 and 5 — the exact calls for the Volunteer Management check and each reuse check, for headless-360 and the Salesforce CLI |
| `references/discovery-interview.md` | Step 3 — the discovery questions, probing prompts and summary |
| `references/configuration-decisions.md` | Step 4 — each configuration decision, its options, default and platform behaviors |
| `references/plan-output.md` | Steps 6–8 — the plan template, schedule details, platform limits, completeness check, checklist, Extensions table and handoff |
| `references/edge-cases.md` | Any step — hybrid programs, existing records, contradictions, several programs |
