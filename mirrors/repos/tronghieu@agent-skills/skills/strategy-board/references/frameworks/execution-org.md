# Execution & Organization — Grove's Working File

Tools for testing whether the organization can do what the strategy asks, and
for turning a chosen option into work. Sources `[S#]`; internal facts come
from the executive, not from guessing.

## Capability assessment

**When:** before Gate 2 (every option's capability row) and at Phase 6.

**How:** list the 5–8 capabilities the option genuinely requires (skills,
systems, processes, relationships). Rate current state 1–5 (1 = absent,
3 = market parity, 5 = distinctive) — rated honestly from evidence the
executive provides, not aspiration. For each gap: build, hire, buy, or
partner; cost and time to close; and the option's survival if it closes late.

**Output format:**

```
| Capability | Need | Have (1–5) | Gap plan | Cost | Time | If late? |
|-----------|------|-----------|----------|------|------|----------|
### So what
[Which gaps are disqualifying, which are just expensive]
```

**Tips:** the most common lie in strategy documents is a 4 that is really a
2. Ask for the evidence behind any generous self-rating — "we're strong in
data" should name the team, the systems, and something they shipped.

## 7S alignment check

**When:** transformations, operating-model changes, post-merger, or when a
sound strategy keeps failing in execution.

**How:** for each element — Strategy, Structure, Systems, Shared values,
Skills, Style, Staff — one sentence on today's state and one on what the
proposed strategy requires. Misalignments between the *soft* elements and the
new strategy are the ones that kill it slowly.

Diagnostic questions per element (a coverage checklist, not a script — ask
the ones the decision touches):

- **Strategy:** is it articulated the same way by different leaders? What
  does actual resource allocation say it is?
- **Structure:** where do decisions actually get made vs the org chart? How
  do units coordinate — and where does work die between them?
- **Systems:** which processes and systems run daily life (planning, budget,
  hiring, reporting)? Which would silently fight the new strategy?
- **Shared values:** what behaviour gets rewarded and what gets punished in
  practice — not on the poster?
- **Skills:** what is the organization genuinely known for doing well? What
  does the strategy need that nobody here has shipped?
- **Style:** does leadership decide top-down or by consensus, fast or slow —
  and does the strategy need the opposite?
- **Staff:** where are the gaps and single points of failure in key roles?
  Can the pipeline fill them in time?

**Output format:** table — `Element | Today | Strategy needs | Aligned? ✓/✗ |
Action`, then the So-what: the 2–3 misalignments that will actually bite, and
whether they are fixable at acceptable cost.

## Operating model sketch

**When:** the chosen option changes who does what — new business line,
build-vs-buy aftermath, reorganization.

**How:** answer four questions concretely: what decisions move and to whom;
where the new work sits (existing unit vs new unit — pull in Christensen's
placement rule for disruptive initiatives); what processes and systems must
change first; and what the interface with the core business is (shared,
served, or separate).

**Output format:** the four answers in prose plus a RACI line for the top
5 decisions — `Decision | Responsible | Accountable | Consulted | Informed`.

## Roadmap (Phase 6)

**When:** after Gate 3 only — a roadmap for an unapproved strategy is
premature detail.

**How:** phase the work so that each phase produces *output someone can see*,
not internal progress. Start with the 90-day plan: 3–5 quick wins that prove
the direction cheaply and build the coalition. Every initiative gets an
owner (a name, not a department), a date, and an output metric. Include the
reallocation table — what gets defunded or stopped to pay for this; a
roadmap with no "stop" list is an unfunded wish (non-negotiable #5 applied
to execution). Wire Wack's signposts to explicit revisit triggers.

**Output format:** use `templates/roadmap.md`.

**Tips:** if no one is named as owner, the initiative does not exist. If a
metric measures activity ("workshops held") rather than output ("cost per
order down 8%"), replace it. And put the review cadence in the calendar
section of the roadmap — a strategy reviewed annually is reviewed never.
