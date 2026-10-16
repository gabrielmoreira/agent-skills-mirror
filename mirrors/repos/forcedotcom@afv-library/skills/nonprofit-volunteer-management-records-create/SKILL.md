---
name: nonprofit-volunteer-management-records-create
description: "Use this skill to write Salesforce Nonprofit Cloud Volunteer Management (VM) records to an org once the user knows what to create, from a confirmed plan or a list of records: it reuses existing records by their Ids instead of duplicating them, asks for any missing required values, shows each object's records table for approval, inserts the records in dependency order, reads each write back, recovers from write errors, and reports every created Id. TRIGGER when a user wants to create, insert, import, or write VM records. DO NOT TRIGGER to decide what a program needs (use nonprofit-volunteer-management-structure-generate), to explain what a VM object or field is for (use nonprofit-volunteer-management-model-get), to enable Volunteer Management in an org, for per-person records (JobPositionAssignment, PersonLocationAvailability, PersonCompetency / PersonExamination, ConstituentRole), or for NPSP / Volunteers for Salesforce (V4S), which is unsupported."
metadata:
  version: "1.2"
  domains: ["Nonprofit"]
  relatedSkills:
    - "nonprofit-volunteer-management-model-get"
    - "nonprofit-volunteer-management-structure-generate"
  cliTools:
    - tool: ["python3"]
      semver: ">=3.8"
    - tool: ["sf"]
      semver: ">=2.0.0"
  accessCheck: "(OrgPermissions.VolunteerManagement) && (OrgPreferences.VolunteerManagementEnabled)"
---

# Nonprofit Cloud Volunteer Management — Record Creation

This skill writes Volunteer Management records to an org: a Volunteer Initiative and the Locations, Positions, Job Positions, qualifications and Job Position Shifts under it. It checks the org for records it can reuse, fills each field from `references/field-guide.md`, shows the user one records table per object, and writes that object only after the user confirms its table. **Open every run by telling the user that this skill reads and writes their org, and that nothing is read or written without their yes.**

## Hard rules

- **Never delete records.** No delete, rollback or cleanup of any kind. If a write fails part-way, report what was created and what wasn't; never undo it.
- **Never act on NPSP or Volunteers for Salesforce (V4S).** That legacy package is unsupported here. Say so and stop.
- **No acronyms or internal labels in what the user sees.** Write out Volunteer Initiative, Job Position, Job Position Shift, Job Position Assignment, Position Qualification, Job Position Qualification, Data Processing Engine, and "out of the box". Never show internal step or section labels.
- **Writes need a yes per object.** Nothing is written until the user confirms that object's records table.

## Mechanism

Org calls go through the connection the session has: the headless-360 tools (`dispatch_readonly` for reads, `dispatch` for writes) or an authenticated Salesforce CLI. Both return the same results at API v67.0. Tell the user which one is in use. If neither is connected, stop and ask the user to connect one; never guess an org result. The exact call for each step, in both forms, is in `references/mcp-invocation.md`.

## Scope

- **In scope:** Volunteer Initiative (including child initiatives), Location and its Address, Competency, Examination, Position, Position Qualification, Job Position, Job Position Qualification, Job Position Shift; Operating Hours and Time Slots only when the user asks for them. Reusing existing records, filling fields, detecting required custom fields, writing in dependency order, and recovering from write errors.
- **Out of scope:** deciding what to build (`nonprofit-volunteer-management-structure-generate`); explaining what an object or field means (`nonprofit-volunteer-management-model-get`); turning Volunteer Management on; any per-person record — volunteer sign-ups and assignments, a volunteer's availability, a person's qualifications, marking a person as a volunteer, the person or household itself. The full list is in `references/field-guide.md` "Out of scope".

## Required inputs

- **The records to create.** Chained: the plan from structure-generate — its summary table, the Id of each reused record, the schedule details, the outstanding inputs and the `Reuse-check:` line. Standalone: ask the user what to create.
- **Field values.** `references/field-guide.md` is the authority for every standard field: API name, required flag, tier, default and must-ask rules. Ask for each outstanding input from the plan when its object comes up.
- **Defaults:** propose Status `Upcoming` on a new Volunteer Initiative, Position, Job Position and Job Position Shift — offer Status's live values, and if none fits, offer to add one (step 6). Every other default is in the field guide. Location Type has no default and is always asked.

## Workflow

1. **Open and pick the mode.** Give the opening notice above. Chained: work from the handed-off plan and don't re-interview. Standalone: gather the records from the user.
2. **Ask for the read consent, once.** Say what you'll read and why: the Volunteer Management check, the reuse checks, the existing-shift check, and the object descriptions used for required custom fields and live picklist values. Declining means existing records can't be checked, so duplicates may be created, and required custom fields surface only as write errors. If declined, proceed from the plan without reading: every record not already marked Reuse is New, and picklist values are the user's; one the org doesn't accept surfaces as a write error.
3. **Check that Volunteer Management is on**, once, after the user agrees to the org read (calls in `references/mcp-invocation.md`):
   1. Read the org preference `VolunteerManagementEnabled`. `true` → on. `false` or 404 → off: stop and tell the user an admin turns it on in Setup → Volunteer Management Settings. 403 → the user has no access to org settings: stop and say so.
   2. Describe `VolunteerInitiative`. 200 → the user can see the Volunteer Management objects. Any error → stop and tell the user they need the Manage Volunteer Data permission set. Don't look up permission-set assignments beforehand.
4. **Reuse checks, by the plan's `Reuse-check:` line.**
   - `RESOLVED` → the plan's Reuse/New mapping is authoritative. Use its reused Ids as-is and don't re-run the reuse checks.
   - `DECLINED` → run the reuse checks for every record the plan marks New.
   - Missing or unrecognized line, or standalone → run the reuse checks for every planned record.

   One bounded query per object, filtered to the planned names (never the whole object). Match a Job Position on Name + Volunteer Initiative, Operating Hours on Time Zone + its set of Time Slot windows (never the name), everything else on Name. Escape an apostrophe in a name with a backslash (`O\'Brien`); doubling it fails. Query only fields the field guide documents. For a reused Location, read its Visitor Address: if it has one, don't create another.
5. **Existing-shift check — on every plan, including `RESOLVED`.** For each Job Position that is reused, query its shifts by that Job Position's Id and the series' date range; never by name or Position. If N of the M planned shifts already exist, stop and ask: "N of M shifts already exist (dates X–Y). Create only the missing ones, create all M (duplicates), or cancel?" On "only the missing ones", pass the existing shifts to `scripts/expand-series.py` as `excludeExisting`. A new Job Position has no shifts to check.
6. **Read the object descriptions** for each object you'll write: find required custom fields (custom, createable, not nillable, not defaulted on create) and the live picklist values. Never describe an object to learn its standard fields — the field guide is the source for those — but when a description is in hand and differs from the field guide (a renamed label, a picklist value), the description wins. A required custom field becomes a `needs-input` column on that object's table.
   - **Platform picklists** (Time Zone, Time Slot Day of Week and Type): offer only the live values. A value outside them is rejected before the write, never sent.
   - **Every other picklist:** offer the live values. If none fits, ask whether to add one; on a separate yes, get it added before the write. On headless-360 the user adds it in Setup and you give them the exact path; on the Salesforce CLI you add it for them (`references/mcp-invocation.md`). Use it only once a fresh describe lists it; a value that isn't in the list yet is rejected on write.
7. **Summarize, then review one object at a time.** Lead with the insert summary in `references/review-format.md`: what will be written, Reuse ("Name · object") and New counts per object, how the records fit together, and the write order. Ask the fill mode: prefill everything, or generate together. Then, for each object in write order, show its field guide and its records table. **Render every records table with `scripts/render-review-table.py`, never by hand** — it keeps every value under its own column. Invite edits and re-render. Confirming an object's table is the yes to write it; there is no second confirm.
8. **Write each confirmed object, parents first.** Order: Volunteer Initiative (parents, then child initiatives) → Location → its Address → back-fill the Location's Visitor Address → Competency / Examination → Position → Position Qualification → Job Position → Job Position Qualification → Operating Hours → Time Slot (only on request) → Job Position Shift. Skip objects the plan doesn't use.
   - Several records of one object go in one tree call (all-or-nothing, up to 200 records). Over 200, split into batches.
   - A parent written in an earlier call is referenced by its literal Id. A `@refId` reference works only inside the same call.
   - A child Volunteer Initiative goes in a second call after its parent, with the parent's literal Id.
   - A new onsite Location gets its Address (street, city, state, postal code and country from the user; Location Type and Time Zone copied from the Location), then the Location's Visitor Address is set to the new Address. A virtual Location, or a reused one that already has an Address, gets none.
   - Feed returned Ids forward to children; don't re-query records you just created.
   - Read each write back to confirm it.
   - **Shift series:** build the `scripts/expand-series.py` spec from the plan's schedule details — days and windows (`windowsByDay` when windows differ by day), start date, end date or `count`, time zone, volunteers per shift, the confirmed Status, and `excludeExisting` from step 5. A monthly or irregular schedule goes in as `oneOffDates` with the dates the user confirms. Tell the user the series ends there; later shifts are added in a later run.
9. **Recover from errors.** Show the error, propose a fix grounded in the error message and the object description, and re-send only the records that weren't created. If a write fails part-way, say which records exist and which don't; never undo.
10. **Final report.** One table of every record this run wrote or reused (object, name, Id, Reuse or New) and the planned-versus-written count, in the layout in `references/review-format.md`. For a shift series, state the dates it covers.

## Rules

| Constraint | Rationale |
|-----------|-----------|
| One read consent; one write consent per object, given on that object's records table | Approving a read is not approval to write. A partial decline is treated as declined. |
| Reuse existing records; never duplicate | Every planned record gets a reuse decision before it's written; shifts of a reused Job Position are checked on every run. |
| Every org query is bounded to the plan | Filter on the planned names; never read a whole object. The query is a duplicate check, not a listing. |
| Never write tier 4 or 5 fields | They are system-managed, auto-numbered, formulas or owned by another feature; writing them errors or is overwritten. |
| Never create a Recurrence Schedule | Volunteer Management's own recurrence feature owns it; this skill writes one Job Position Shift per occurrence. |
| Every shift series has an end date or a count | Each shift is its own record; an open-ended series would never stop. |
| Operating Hours and Time Slots only when the user asks | Nothing links them to a Location or Job Position; they are used only for volunteer availability matching. |
| Never build a series or a records table by hand | `scripts/expand-series.py` and `scripts/render-review-table.py` are reviewed and tested; hand-built dates and tables shift values. |
| Show names, not Ids or API names, before the final report | The user reviews records in plain language; Ids appear only in the final report. |

## Gotchas

| Issue | What to do |
|-------|------------|
| Location and Address point at each other | Write the Location, then the Address with its Parent set to the Location, then update the Location's Visitor Address. |
| Operating Hours and Time Slots | Write the Operating Hours first, then its Time Slots in a second call with the literal Id. |
| Child Volunteer Initiative in the same call as its parent | A self-reference fails with `MALFORMED_ID`; write parents first, then children with the literal parent Id. |
| Job Position Shift dates and times | Separate StartDate, EndDate, StartTime, EndTime and TimeZone fields; there is no combined date-time field. |
| Qualifications | Matching uses QualificationLevel on Competency qualifications. A Job Position's own qualifications and its Position's qualifications are checked together, keeping the higher level per Competency. Nothing is copied from the Position to the Job Position. |
| Shift capacity | Counted, never enforced: nothing blocks a signup when a shift is full. |
| A required field the description didn't show (a validation rule) | It surfaces as a write error; handle it in step 9. |

## Output expectations

- The confirmed Volunteer Management records written to the org in dependency order, or reused.
- A final report of every record written or reused, with its Id, and the planned-versus-written count.
- Keep every message compact, in the layout in `references/review-format.md`: one field guide and one records table per object, one row per record (a shift series is one row; past 10 series, one row per shared schedule), and say each point once. Don't restate a table in prose, add sections the layout doesn't have, or show a write payload per record; if the user asks to see the payload, show one representative example per object.

## Cross-skill integration

| When | Do |
|------|----|
| The user doesn't know what to build | Defer to `nonprofit-volunteer-management-structure-generate`; it produces the plan this skill writes. |
| The user asks what an object or field means | Defer to `nonprofit-volunteer-management-model-get`. |
| Chained from structure-generate | Work from the handed-off plan. Handle its `Reuse-check:` line as in step 4, and run the existing-shift check in step 5 regardless. |

## Reference file index

| File | When to read |
|------|-------------|
| `references/mcp-invocation.md` | Steps 3–6, 8 — the exact read and write calls for headless-360 and the Salesforce CLI, the Volunteer Management check, apostrophe escaping, adding a picklist value. |
| `references/field-guide.md` | Steps 4, 6–8 — every object's fields, API names, tiers, defaults, must-ask rules and limits. |
| `references/review-format.md` | Steps 7 and 10 — the insert summary, the per-object review, the origin tags and the final report. |
| `scripts/render-review-table.py` | Step 7 — renders each records table from JSON (field → value + origin tag). Spec in its docstring. Tests: `scripts/tests/test_render_review_table.py`. |
| `scripts/expand-series.py` | Step 8 — expands a shift or time-slot series into tree-call records: weekly windows or per-day windows, date ranges, one-off dates, `excludeDates`, `count`, `excludeExisting`. Spec in its docstring. Tests: `scripts/tests/test_expand_series.py`. |
