# Edge Cases

**When to load:** any step, when a situation doesn't fit the standard flow.

**Purpose:** hybrid programs, existing records, contradictions, several programs, and an unsure user.

---

## Hybrid programs ("sometimes shifts, sometimes flexible")

Plan both under the same Volunteer Initiative: Job Positions with shifts for the scheduled work, Job Positions without shifts for the flexible work. Don't force the program into one model. Adding shifts to a Job Position later is easy.

---

## Existing records in the org

Assume the org may already hold relevant records, and check every session (Workflow step 5).

- Show what you find and ask before planning anything new: "You already have a Location called 'Eastside Pantry' and a Competency called 'Food Safety'. Should I use these, or plan new ones?"
- Locations, Competencies, Examinations and Positions are meant to be shared. A "Food Safety" Competency planned for one program should be reused for the next.
- If the user wants shifts for a Job Position that already exists, plan the schedule they want. records-create checks which of those shifts already exist and creates only the missing ones.
- If an existing record looks incomplete or misconfigured, say what's missing. This skill doesn't change it.

---

## User contradicts themselves

Example: "No qualifications needed", then later "oh, drivers need a license". Or: "no shifts", then "we need 5 volunteers every Saturday at 9", which is a shift.

Raise it gently and let the user choose: "Earlier you said X, but now it sounds like Y. Which is right?" Don't pick the later answer silently, and don't run the reuse checks for the affected records until it's settled.

---

## Several programs

Get the full list first, then plan one program at a time.

- Reuse a Location when the same site serves several programs, and reuse Competencies across programs.
- Each program gets its own Volunteer Initiative and Job Positions, and possibly its own Position templates.
- For later programs, offer the earlier decisions: "You put qualifications on the Position for the first program. Same approach here?" Configure each program for its own needs.

---

## User is unsure about a parent Volunteer Initiative

Recommend no parent: "When in doubt, start without one. You can add a parent later without changing anything already set up."

If the user describes four or more related programs with shared reporting but still hesitates, ask one question: "Would it help to see combined numbers across all of them, or do you manage each one separately?" If they're still unsure, plan no parent.
