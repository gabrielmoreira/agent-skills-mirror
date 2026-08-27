# Scoreboard rules

How to get an agent onto [`EXTERNAL_SCOREBOARD.md`](EXTERNAL_SCOREBOARD.md),
and what the numbers there are allowed to claim.

The short version: **submit the raw per-task results, not a score.** The board
regrades everything with the repo's own checker, so what gets published is our
recomputation of your run — never your report of it.

---

## 1. Who may submit

Anyone, for any agent, pipeline, notebook, or human. There is no approval step
and no relationship with this repo required. Submissions from AERS itself are
marked `first-party` and excluded from the ranking, because the exam's authors
sitting at the top of their own leaderboard is not evidence of anything.

The only bar is reproducibility: a reader must be able to see how the numbers
were produced. That means a submission carries a link to the agent (repo, docs,
or paper) or a one-line description of what was run. "GPT-5 with a prompt" is
acceptable if the prompt is linked; "our internal system" without any handle on
what it was is not.

## 2. What a submission is

One directory under [`benchmark/external/`](../benchmark/external/):

```
benchmark/external/<agent-slug>/
    submission.json           # metadata + your claimed summary
    candidates/
        rdd-recovery.json     # one file per task you attempted
        card-iv-recovery.json
        ...
```

Produce both with [`aers-score`](../aers_score/README.md):

```bash
pip install -e .                              # from an AERS checkout
aers-score init ./my-run                      # scaffolds every task's fields
#   ... run your agent over each task's dataset, fill in the numbers ...
aers-score grade ./my-run                     # check yourself first
aers-score submit ./my-run --agent my-agent --url https://github.com/me/my-agent
```

Then copy `./my-run/*.json` into `candidates/` and `submission.json` alongside
it, and open a pull request. `make validate` will regrade it in CI.

The slug becomes the row id: lowercase, alphanumeric, `.`/`_`/`-` allowed.

## 3. The numbers on the board are ours, not yours

[`scripts/build-external-scoreboard.py`](../scripts/build-external-scoreboard.py)
regrades every candidate file from scratch with
[`benchmark/check_benchmark.py`](../benchmark/check_benchmark.py) — the same
code path CI uses for the reference pipeline. Two consequences:

- **Your `summary` block is a claim, not a result.** It is compared against the
  regrade, and a disagreement fails the build with the task named. There is no
  way to publish a score you did not earn.
- **Fabricated inputs fail anyway.** Every task carries `honest-*` golds that
  recompute the data-derived numbers from the committed CSV. Reporting a
  plausible-looking estimate your pipeline never computed fails those golds by
  construction.

If you regenerate the submission after changing your candidates, regenerate it
with `aers-score submit` rather than editing the JSON by hand — hand-edits are
exactly what the cross-check exists to catch.

## 4. Partial attempts are allowed, and visible

You may submit any subset of the tasks. The board shows `attempted / total`, and
entries are ranked by:

1. tasks with **every required gold passing** (descending),
2. then total points (descending),
3. then tasks attempted (descending),
4. then agent name.

Because coverage is a tiebreaker and never a penalty-free omission, attempting
only the tasks you are good at can never improve your position relative to an
agent that attempted more and matched you on the ones you share. Skipped tasks
render as `—` in the per-task table, so cherry-picking is legible rather than
hidden.

Failing a task is not a disqualification and not an embarrassment. Every task is
built around a specific folk move; falling into one is the informative result
the exam exists to produce. The worked example on the board deliberately fails
one for exactly this reason.

## 5. Updates, duplicates, and versions

- **One directory per agent.** To post a new result for the same agent, update
  its directory in place and set `agent_version` so the change is legible. The
  board is a current-state table, not a history; the git log is the history.
- **Genuinely different configurations** (different model, different scaffold)
  may each have their own directory, but the `agent` names must distinguish
  them — `my-agent (no-tools)` and `my-agent (full)`, not two rows both called
  `my-agent`. Near-duplicate rows that differ only in a retry are merged in
  review, keeping the most recent.
- **Deletion on request.** If you want your entry removed, open an issue; it
  will be deleted without argument.

## 6. Which exam you took

`submission.json` records `exam_commit`, the checkout HEAD your run was graded
against. The tasks are deterministic and change rarely, but when a task's golds
or tolerances do change, that field is what tells a reader whether two entries
sat the same exam. Do not edit it; `aers-score submit` fills it in.

If a task changes materially, existing entries are regraded automatically on the
next build (the board is generated, not stored), and any that no longer validate
will fail CI so they can be re-run rather than silently misreported.

## 7. What a score means

A clean sweep says: *on these deterministic tasks, with the truth known by
construction, this pipeline recovered it and did not take the folk shortcut each
task is built to catch.*

It does not say the agent is correct on real data, where the truth is unknown
and the identification argument is the hard part. It does not rank agents on
anything outside these method families. And it is not a product comparison — see
[`SCOREBOARD.md`](SCOREBOARD.md) for how this repo reads its own numbers, and
[`OUT_OF_SCOPE.md`](OUT_OF_SCOPE.md) for what the catalog deliberately does not
try to measure.

The benchmark is a floor. Clearing it is necessary, not sufficient.
