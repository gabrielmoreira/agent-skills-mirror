# Discovery Interview

**When to load:** Workflow step 3, at the start of a planning session.

**Purpose:** the discovery questions, in order, with probing prompts and what each answer feeds in `configuration-decisions.md`. The interview is for understanding. It decides nothing.

---

## How to run it

- Ask about the topics below in order, whatever the program's complexity. Use the probing questions only when an answer is unclear or incomplete; skip any the user has already answered.
- Stay on one topic at a time. Group a few closely related questions when they're easy to answer together; split them across turns when they need long answers. Record anything the user says about a later topic, but don't move on early.
- With several programs, get the full list first, then go deep on one at a time. Keep one program active. Note what the user says about another, but don't follow it up until the active one is finished and confirmed. For later programs, offer the decisions made for the first.
- When every topic is done, summarize back (see the end of this file) before any configuration decision.

---

## Programs

**Ask:** "Tell me about your volunteer program(s). What do your volunteers do?"

**Probe:**

- "How many distinct volunteer programs or activities do you run?"
- "Are they connected (same volunteers, shared reporting) or independent?"
- "Do different teams or coordinators manage them?"

**Feeds:** how many Volunteer Initiatives, and the parent Volunteer Initiative decision.

---

## Locations

**Ask:** "Where does this volunteering happen? Is there a site volunteers go to, and how many sites are involved?"

**Probe:**

- "Does the same program run at more than one site?"
- "If there are several sites, is it the same program at each, or different programs?"

For each site, collect only the name, the address, and whether it's onsite or virtual.

**Feeds:** the Locations decision, and the parent Volunteer Initiative decision when the same program runs at several sites.

---

## Roles

**Ask:** "What types of volunteer roles need to be signed up for and tracked separately?"

**Probe:**

- "Are there different jobs (Team Lead, Driver, Tutor) that need separate sign-up and tracking?"
- "Is the same role used in more than one program, or at more than one location?"
- "Where the same role appears in more than one place, do its requirements stay the same?"

**Notes:**

- Different onsite tasks that don't need separate tracking can share one Job Position.
- A Position is a reusable role template. Matching checks a Job Position's own qualifications together with its Position's. Status, publishing and capacity are not passed from the Position to the Job Position.
- **Suggests a Position template:** the same role across programs or locations, with requirements that should stay consistent.
- **Suggests a Job Position only:** the role exists in one program, its requirements are unique, and no reuse is expected.

**Feeds:** the Position template decision, and later the qualifications decision.

---

## Delivery format

**Ask:** "Is the work done onsite, virtually, or both? Do any volunteers work remotely?"

**Feeds:** the Locations decision. Matching volunteers by location needs a Location, so virtual roles usually get a "Virtual" Location.

---

## Qualifications

**Ask:** "Is there anything volunteers must have or prove to sign up?"

**Probe:**

- "Are certifications, training or skills required for any of these roles?"
- "Do those requirements apply everywhere the role appears, or change by program or location?"
- "Is there anything volunteers must show before they sign up, such as a background check or a certification?"

**Feeds:** the qualifications decision and the Position template decision.

---

## Scheduling

**Ask:** "Do volunteers sign up for set times, or come when they can?"

**Probe:**

- "Does it happen on a regular schedule (weekly, monthly) or once?"
- "What are the days and times? Are they the same every day, or different on some days?"
- "When does it start, and when does it end, or how many sessions are there? Which time zone?"

**Feeds:** the shifts and recurrence decisions, and the schedule details handed to records-create.

---

## Capacity

**Ask:** "How many volunteers do you need for each shift or opportunity?"

**Probe:**

- "Is there a maximum number of volunteers per shift?"
- "Is there a minimum?"

**Notes:**

- The maximum is counted, never enforced: the remaining capacity is a formula, and nothing blocks a signup when a shift is full. Mention it when the user describes a hard limit.
- Matching and the Find Unfilled Shifts action rely on a maximum being set.
- A minimum isn't a standard field; the customer may want a custom field for it.

**Feeds:** the capacity in the plan.

---

## Summary back

Summarize before any configuration decision, so the user can correct it:

"Here's what I've understood about your program:

- **Programs:** …
- **Locations:** …
- **Roles:** …
- **Delivery format:** …
- **Qualifications:** …
- **Scheduling:** …
- **Capacity:** …

Does this sound right? Anything I'm missing or got wrong?"
