# Postmortem Review Meeting — [Incident title]

> 45 minutes, document-first. The meeting's job is to *improve the analysis and commit to actions* — not to relive the incident or perform accountability. Facilitator ≠ incident commander if possible.

**When:** within 5 working days of resolution · **Doc circulated:** ≥24h before · **Facilitator:** [name] · **Scribe:** [name]

## Ground rules (read aloud, 1 min)

- Blameless: we discuss what the *system* allowed, not who did what. The facilitator interrupts blame-shaped sentences and reframes them (see references/root-cause-digging.md).
- Everything surprising said here goes into the doc — the doc is the artifact, the meeting is scaffolding.

## Agenda

**1. Silent read / corrections (10 min)**
Attendees who haven't read it, read it. Everyone marks factual errors in the timeline. Fix them live — a wrong timeline poisons every conclusion downstream.

**2. Root cause challenge (15 min)**
- Does anyone believe the stated root cause is actually a trigger? What's underneath it?
- Which safeguard should have caught this, and why didn't it? (If the doc answers this weakly, dig now.)
- Are there why-chains not followed — detection chain? response chain?

**3. Action items (15 min)** — the only part that changes the future
For each proposed action: is it specific enough to close as done/not-done? Who owns it (a name)? By when?
- Kill or rewrite any "improve X" items.
- Check coverage: at least one action each for *prevent*, *detect faster*, *respond faster* — or an explicit "not needed because…".
- P1 actions: agree they block incident closure.

**4. Lessons worth exporting (5 min)**
What here applies beyond this team? Who tells them, in what channel?

## Close

- [ ] Doc updated during the meeting (scribe confirms)
- [ ] Actions filed in the tracker with owners + dates *(the action-runner skill can do the filing)*
- [ ] Follow-up date set to review action completion: [date, ≤30 days]
- [ ] Doc shared to [where postmortems live]

**Signals the meeting worked:** the doc changed; at least one action got more specific; nobody apologised.
