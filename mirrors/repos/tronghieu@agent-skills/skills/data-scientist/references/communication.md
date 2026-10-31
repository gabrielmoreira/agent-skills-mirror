# Communicating Results

The deliverable of an engagement is not a model or a notebook — it's a
decision made better. This file governs anything a stakeholder will read,
especially `insight-report.md`.

## Principles

- **Answer first.** The first paragraph states the answer to the framing
  question in plain language, with the headline number and its uncertainty.
  Nobody should read to page two to learn what you found. Structure everything
  as answer → evidence → detail (the reader can stop at any depth and leave
  with a correct picture).
- **Business units, always.** Percentage points, customers, days, currency.
  Standardized effect sizes, AUCs, and model jargon go in the appendix. If a
  number can't be expressed in a unit the decision-owner manages by, question
  whether it belongs in the report at all.
- **Uncertainty in plain language, not hedging.** "Between 0.9 and 2.7
  points, most likely ~1.8" is honest and readable. "It's hard to say for
  sure" is hedging; a bare "+1.8pp" is overclaiming. Give the range and then
  say plainly what you'd do — ranges inform decisions, they don't excuse you
  from making a recommendation.
- **Causal language matches the evidence.** The summary carries the *weakest*
  causal claim in the chain (see statistics reference). It is the summary,
  not the methods section, that gets forwarded.
- **So-what filter.** Every section must change what the reader decides, does,
  or watches. Interesting-but-inert findings go to the appendix or die.

## The insight report

Use `templates/insight-report.md`. Its logic:

1. **The question** — one line, as framed and confirmed with the user.
2. **The answer** — the finding, its size in business units, its confidence.
3. **The evidence** — the two or three load-bearing results, each with a
   number, an uncertainty, and (only if it carries weight text can't) a chart.
4. **The recommendation** — concrete actions with quantified trade-offs. For
   models: the threshold table from `references/evaluation.md`. For analyses:
   the levers and their expected effects. Then hand the choice back: state
   which option you'd pick and why, but mark the decision as the owner's.
5. **Limitations** — what would change the conclusion: data gaps, causal
   ambiguity, segments where results are weaker, assumptions from the brief.
   Written by the review-gate pass, in specific terms ("history covers only
   14 months, so seasonality is estimated from one cycle") — not boilerplate
   ("more data needed").
6. **Appendix** — methods, model card pointer, full tables, exploratory
   findings.

## Charts

Read the `dataviz` skill first if the session has one. Regardless:

- One message per chart, stated in the title as a claim ("Churn concentrates
  in month 1–2"), not a variable name ("Churn by tenure").
- Prefer the boring chart that's read in three seconds — bars, lines,
  scatter. Annotate directly (label the line, mark the threshold) instead of
  relying on legends.
- Show uncertainty where it exists: error bars, CI bands, or fold spread.
- Never truncate a bar-chart axis to inflate an effect; never use dual axes
  to imply correlation.

## Numbers hygiene

Every figure traces to executed code (non-negotiable #2) — when writing the
report, re-check each number against the artifact it came from
(`experiment-log.md`, profile output, test results). Round to the precision
the data supports: "23.4712%" from n=200 is false precision; "23%" or "roughly
1 in 4" reads better and claims less. Numbers supplied by the user that you
couldn't verify are labeled as such.

## Communicating a Review-flow critique

When the deliverable is a critique of someone else's analysis, structure it
as: what the analysis claims → what checks were run → findings ranked by how
much they change the conclusion (fatal / material / minor) → what would make
it sound. Verify each finding before reporting it (run the code, reproduce
the number). The goal is a stronger analysis, not a gotcha list — say what
was done well, and make every criticism actionable.
