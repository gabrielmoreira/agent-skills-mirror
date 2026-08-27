# `aers-score` — take the AERS benchmark and score yourself

The [AERS numeric benchmark](../benchmark/README.md) is a shared exam for
empirical-research agents. Each task ships a deterministic dataset with a known
truth, and the grader **recomputes every data-derived gold from the committed
CSV** — so a pipeline cannot pass by reporting plausible-looking numbers it
never computed.

`aers-score` is the front door to that exam for someone who did not write it.
It reimplements no grading: it loads
[`benchmark/check_benchmark.py`](../benchmark/check_benchmark.py) and calls its
own `validate_candidate` / `compute_truth` / `grade` functions, so the score it
prints is the score CI gives the reference pipeline.

## Install

```bash
git clone https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills
cd Auto-Empirical-Research-Skills
pip install -e .            # or: uv tool install --editable .
aers-score tasks
```

No dependencies — stdlib only, Python 3.9+.

Working outside the checkout? Point the CLI at it once:

```bash
export AERS_REPO=/path/to/Auto-Empirical-Research-Skills
```

or pass `--repo PATH` per invocation. `aers-score where` prints which checkout
was resolved and how.

The exam is not bundled into the package on purpose. A task spec is meaningless
without the dataset its golds are recomputed from, and you need those datasets
to produce a candidate in the first place — so a second copy inside the wheel
would only be a way for the two to drift apart.

## The four-command loop

```bash
aers-score tasks                          # what is on the exam
aers-score describe rdd-recovery          # what one task grades, and the trap it sets
aers-score init ./my-run                  # scaffold candidates with the exact fields
#   ... run your agent over each task's dataset, fill in the numbers ...
aers-score grade ./my-run                 # score yourself
```

`init` writes one `<task-id>.json` per task with every gradeable field present
and `null`. Unfilled fields are reported as unfilled rather than as type errors,
so a half-finished run still scores the half that is finished.

Useful flags:

| Flag | Effect |
|---|---|
| `--json` | machine-readable output on every subcommand |
| `--task <id>` | scaffold or grade a single task |
| `--verbose` | print every gold item, not just the failures |
| `--strict` | exit non-zero when any required gold fails |

By default `grade` exits `0` even when you fail required golds — falling into a
task's trap is an informative result, not a tooling error. `--strict` is for CI.

## Submitting to the public scoreboard

```bash
aers-score submit ./my-run --agent my-agent --url https://github.com/me/my-agent
```

This writes `submission.json` next to your candidates. The scoreboard
**regrades your raw candidate files** with the repo's own graders rather than
trusting the numbers in that file, so submit the candidates alongside it. The
rules — who may submit, how ties and duplicates are handled, and why
cherry-picking tasks is visible — are in
[`docs/SCOREBOARD_RULES.md`](../docs/SCOREBOARD_RULES.md).

## What a score does and does not mean

A clean 17/17 says: *on these seventeen deterministic tasks, your pipeline
recovered the known truth and did not fall for the folk move each task is built
to catch.* It does not say your agent is correct on real data, where the truth
is unknown and the identification argument is the hard part. The benchmark is a
floor, not a ceiling — see [`docs/SCOREBOARD.md`](../docs/SCOREBOARD.md) for how
the repo reads its own numbers.
