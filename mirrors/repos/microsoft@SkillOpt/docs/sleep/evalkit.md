# Paired A/B evalkit

Sleep contributors have a shared instrument for "condition B beats condition A":

```text
python -m skillopt_sleep.evalkit --manifest tasks.json --a cond_a.json --b cond_b.json
```

The kit pairs outcomes by task id, runs McNemar's test on binary successes, and
reports a percentile-bootstrap confidence interval on the success-rate delta.
It does not change the nightly gate.

## Inputs

- `--manifest`: JSON list of task ids, or `{"ids": [...]}` / `{"tasks": [{"id": ...}]}`.
  Every id must be a non-empty JSON string; ids are never coerced from numbers,
  booleans, nulls, arrays, or objects.
- `--a` / `--b`: JSON objects mapping those same ids to `0`/`1` (or an ordered
  list of repeated-seed `0`/`1` values). A wrapper `{"outcomes": {...}}` is also
  accepted. Direct keys that exactly match the manifest take precedence over
  wrapper detection, so a task literally named `outcomes` remains unambiguous.
- `--aa`: A/A identity smoke check (reuses `--a` as both conditions).
  Exactly one of `--b` or `--aa` is required.
- `--allow-graded`: permit non-binary scores. McNemar is omitted; bootstrap only.
- `--boot`, `--seed`, `--alpha`, `--json`.

The id sets of the manifest, A, and B must be identical. Cross-manifest
comparisons and duplicate JSON object keys are refused. Seed lists must be
non-empty. Scores must be JSON numbers (never booleans or numeric strings),
finite, and in `[0, 1]`. `alpha` must be strictly between 0 and 1, and `--boot`
must be between 1 and 1,000,000. The total bootstrap workload is capped at
50,000,000 paired draws (`n_tasks * n_boot`). Exact McNemar evaluation is capped
at 1,000,000 discordant pairs and accumulates its tail from a bounded-memory
stream. JSON parsing is strict throughout the document, including metadata, and
rejects `NaN`/`Infinity` rather than silently accepting non-standard constants.

## Multi-seed

When each task maps to a same-length list of seed repeats, the lists are
positional: A and B must use the same seed ordering. The JSON report calls each
position `seed_index`; it does not claim to verify the underlying RNG seed id.
The kit:

1. averages per task across seeds for the headline delta and bootstrap CI
2. resamples whole tasks, preserving the task as the independent cluster
3. omits McNemar rather than treating repeated seeds as independent samples
4. publishes the per-position deltas plus their mean and sample sd as a
   descriptive diagnostic only; the sd is not a confidence interval, standard
   error, or other inferential uncertainty estimate

That is the house answer to single-seed noise (see issue #108 and the
single-seed warning in `RESULTS.md`).

## RESULTS cell replay

`tests/fixtures/evalkit/results_searchqa_nano_gated.json` replays the published
SearchQA / GPT-5.4-nano / gated / cumulative nights=5 cell (baseline 0.560,
after 0.679, Δ +11.9 on n=1400). Per-task pairs were not published, so the
replay uses a documented maximum-concordance reconstruction: the first
`round(n * rate)` tasks succeed in each condition. The harness recovers the
published point delta only. It does not claim to recover the original microdata,
and p-values or confidence intervals from the reconstructed pairs must not be
cited as evidence for the published experiment.

## A/A checks

```text
python -m skillopt_sleep.evalkit --manifest tests/fixtures/evalkit/aa_manifest.json \
  --a tests/fixtures/evalkit/aa_outcomes.json --aa
```

The command above is an identity smoke check: identical conditions must report
delta 0, McNemar p_exact = 1, and a CI that includes 0. The test suite separately
runs seeded null simulations with genuine discordant pairs, bounds the empirical
McNemar type-I-error rate on both sides of its nominal level, and checks paired
bootstrap coverage. These are seeded null calibration checks. Comparing one
array with itself is not presented as a statistical calibration.
