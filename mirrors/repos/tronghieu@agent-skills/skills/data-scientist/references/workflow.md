# The Engagement Workflow

One pipeline underlies every flow. Short flows enter and exit partway; a full
engagement runs it end to end. Phases are sequential, but findings flow
backward freely — EDA routinely rewrites the framing, and a failed review
reopens modeling. What never happens is *skipping forward*: no modeling before
EDA, no reporting before review.

## Phase 0 — Setup

Create `ds-workspace/{project-slug}/`. Copy `templates/project-brief.md` in and
start filling it during Phase 1. Every later artifact lives here.

## Phase 1 — Framing

Read `references/framing.md`. Output: a completed `project-brief.md` stating
the decision at stake, the question level (descriptive → prescriptive), the
unit of analysis, the target or quantity of interest, and what "good enough to
act on" means. Do not touch data-analysis code until the brief has an answer
for "what will change based on this analysis?" — analysis without a decision
attached is a report nobody reads.

If the user's ask is narrow and well-posed ("compare these two variants"), the
brief can be five lines. It still gets written: the discipline is cheap and
catches silent misunderstandings early.

## Phase 2 — Data audit

Run `scripts/profile_data.py` on every input dataset. Read the warnings
section first. Then work through `checklists/data-quality.md`. Output:
`data-profile.md` in the workspace plus a short verdict — is this data fit for
the question? Common early exits here: the target can't be constructed, the
grain is wrong, the history is too short. Saying so *now* is a good outcome,
not a failure.

## Phase 3 — EDA

Read `references/eda.md`. Explore with the question in mind — this is directed
exploration, not a museum tour of the columns. Output: `eda-report.md` ending
with a ranked list of hypotheses and (if modeling is next) candidate features
and expected leakage traps.

**Explore-flow exit:** for "explore this dataset" asks, the engagement ends
here. Deliver the EDA report; its hypotheses section is the bridge the user
can pick up later.

## Phase 4 — Analysis or modeling

Two branches, chosen by the question level from Phase 1:

- **Diagnostic (Inquire):** read `references/statistics.md`. Select the test
  via the decision tree, check assumptions with the bundled snippets, compute
  effect sizes with confidence intervals. If the question is causal, apply the
  causality section's standards before any "because" appears in your notes.
- **Predictive (Predict):** read `references/modeling.md`. Run
  `scripts/baseline_model.py` first — its report is the floor. Then iterate:
  features, stronger models, tuning. Log every run in `experiment-log.md`
  before looking at the next idea; untracked experiments are how test-set
  overfitting sneaks in.

## Phase 5 — Validation

For models: read `references/evaluation.md`, run `checklists/leakage.md`, and
confirm the final model beats the baseline by a margin that survives the CV
spread. For statistical results: verify assumptions held and effect sizes are
practically (not just statistically) significant. Output: `model-card.md` for
anything that will be used again.

## Phase 6 — Review gate

Switch hats. Run `checklists/analysis-review.md` against your own work as if a
rival wrote it. Anything that survives goes forward; anything that doesn't
goes back to Phase 4. Surviving concerns become the Limitations section — a
deliverable with no limitations listed is a deliverable that wasn't reviewed.

## Phase 7 — Communication

Read `references/communication.md`. Output: `insight-report.md` — answer
first, evidence second, limitations honest, recommendation with quantified
trade-offs, decision handed back to the owner.

## Flow entry/exit map

| Flow | Enters at | Exits after | Notes |
|---|---|---|---|
| Full engagement | 0 | 7 | The whole pipeline |
| Explore | 0 | 3 | Brief may be minimal; hypotheses are the handoff |
| Inquire | 0 | 6 | Phases 2–3 compressed to what the test needs — but never skipped |
| Predict | 0 | 6 (7 if asked) | Baseline script is mandatory, not optional |
| Review | 6 | 6 | Apply the review checklist to someone else's work; deliver the critique |
| Communicate | 7 | 7 | Inputs are existing results; verify numbers trace to executed code before writing |

Two cautions for the compressed flows:

- **Inquire** still profiles the data (Phase 2). Most "significant" results
  that later collapse were tested on data nobody had looked at.
- **Communicate** does not launder unverified numbers. If the user hands you
  results you can't trace to executed code, either re-run the computation or
  label the figure as supplied-by-user in the report.
