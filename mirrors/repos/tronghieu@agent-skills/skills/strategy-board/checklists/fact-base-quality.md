# Fact Base Quality Check

*Run by Drucker at the end of Phase 1, before any framework touches the
numbers. Also re-run whenever a later phase adds facts. `scripts/board_check.py`
catches the mechanical part; this checklist is the judgment part.*

## Sourcing

- [ ] Every fact row has a source `[S#]` with a date — no orphan numbers.
- [ ] Every number that will appear in analysis exists here first (analyses
      cite the fact base; they don't introduce fresh numbers).
- [ ] No source is a bare "web search" — each names the publication, dataset,
      filing, or interview.
- [ ] Each source has an incentive note where it matters: vendor studies,
      sponsor business cases, and broker research are testimony, not evidence.

## Coverage

- [ ] The facts cover what the *decision* needs, not what was easy to find —
      check against the brief: market, competitors, economics, internal
      capabilities as applicable.
- [ ] Failures are represented, not just winners: if benchmarks/cases are all
      successes, survivorship bias is already in the base (Taleb's `bias sweep`
      names the missing dead).
- [ ] Internal facts came from the executive or their documents — not from
      plausible inference about their own company.
- [ ] Dates: facts older than ~18 months that describe a fast-moving quantity
      (market size, pricing, technology capability) are flagged or refreshed.

## Assumptions

- [ ] Every gap that analysis will lean on is a *named* assumption `[A#]` with
      a value, a basis, an owner, and a verify-by plan.
- [ ] No assumption is disguised as a fact (the tell: a precise number with a
      vague source).
- [ ] The assumptions register is short enough to be real — twenty
      assumptions means the fact base isn't done or the question is premature.

## Honesty

- [ ] Conflicting evidence is recorded as conflicting — both values, both
      sources — not silently resolved to the convenient one.
- [ ] "We don't know and can't cheaply find out" appears where true, in the
      Gaps section, with its consequence for confidence.
