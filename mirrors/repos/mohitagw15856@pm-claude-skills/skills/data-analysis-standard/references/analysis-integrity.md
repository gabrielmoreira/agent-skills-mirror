# Analysis Integrity: the Checks Between Query and Conclusion

Most wrong analyses aren't math errors — they're integrity skips: the sanity check not run, the confound not considered, the confidence not stated. This is the between-query-and-conclusion checklist.

## Before trusting the data

- **Row-count sanity** — does the base population match known reality (MAU, order volume)? A join that silently duplicated or dropped rows produces beautiful nonsense.
- **The time-window edges** — partial weeks/months at the range edges poison trends; trim or annotate.
- **Instrumentation archaeology** — did the event's definition change in-window? Check the tracking changelog BEFORE explaining a step-change with strategy. ("We broke the event" outnumbers "the market moved.")
- **Nulls and defaults** — what does the pipeline do with missing values? A default-to-zero can manufacture a trend.

## Before trusting the pattern

- **Decompose before diagnosing** — any moving average is suspect: split by segment/mix/geography first. Two stable segments with shifting proportions imitate change (Simpson's paradox is a weekly occurrence, not a textbook curiosity).
- **The denominator interrogation** — every rate: who exactly is in the bottom? "Conversion improved" often means "the denominator shrank" (a marketing pause 'improves' conversion instantly).
- **Seasonality & calendar** — compare like-for-like periods; a B2B metric "dropping" into late December is a calendar, not a crisis.
- **Correlation discipline** — observed correlations (feature users retain better) get the selection-effect interrogation before ANY causal phrasing. The honest verbs: "is associated with", "predicts" — never "drives" without an experiment or a serious identification argument.

## Before shipping the conclusion

- **The disconfirming pass** — spend 15 minutes genuinely trying to break your own finding: what query result would kill it? Run that query.
- **Confidence labelling** — each claim tagged: solid (multiple cuts agree) / probable (one strong cut) / speculative (pattern needs a test). Stakeholders remember your claims uniformly; the labels are how nuance survives.
- **The "so what" completion** — an analysis ends in a decision-shaped sentence ("this supports doing X / kills Y / needs test Z"), or it's a chart delivery service.
- **Reproducibility** — the query/notebook linked, the definitions stated. "Trust me" is not a methods section.
