# External benchmark submissions

One directory per agent. Everything here is regraded from scratch by
[`scripts/build-external-scoreboard.py`](../../scripts/build-external-scoreboard.py)
to produce [`docs/EXTERNAL_SCOREBOARD.md`](../../docs/EXTERNAL_SCOREBOARD.md);
`make validate` fails if the committed page does not match a fresh regrade.

```
<agent-slug>/
    submission.json         # metadata + claimed summary (aers-score submit)
    candidates/<task>.json  # the raw per-task results, regraded here
```

The submitted `summary` is a **claim**, cross-checked against the regrade — a
mismatch is a build failure, not a footnote. And the graders recompute every
data-derived gold from the committed CSVs, so numbers a pipeline never actually
computed fail the `honest-*` golds regardless of what the summary says.

Full rules: [`docs/SCOREBOARD_RULES.md`](../../docs/SCOREBOARD_RULES.md).
Tooling: [`aers-score`](../../aers_score/README.md).

## `example-agent/`

A hand-written worked example, not a real system. It exists to document the
file layout and to keep the regrade path exercised in CI. It attempts three
tasks and deliberately takes the folk move on one of them — regressing the
outcome on treatment *and* the mediator to read off a "direct effect" — so the
board demonstrates a partial score rather than only perfect ones. It carries
`"origin": "example"` and is never ranked.
