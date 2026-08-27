# Discrimination fixtures

A scenario is cheap to add and easy to get wrong in two opposite ways, neither
of which is visible from reading the scenario file:

- a rubric whose patterns match almost anything **inflates the coverage count
  while testing nothing**;
- a rubric whose patterns match almost nothing **fails correct answers too**,
  and gets ignored.

Both become visible the moment you run the rubric against a *correct* answer and
a *plausibly wrong* one and ask whether the verdicts differ. That is all a
fixture pair is:

```
eval-harness/fixtures/<scenario-id>/
    pass.md    what a careful, correct answer looks like
    fail.md    what an agent that knows the syntax but not the inference says
```

`fail.md` is not a strawman. It should be the answer someone would actually
write and defend — the folk move the scenario exists to catch, argued
confidently. A rubric that only separates a good answer from gibberish has not
been tested.

## The bar

```bash
python3 eval-harness/run_evals.py --selftest
```

For every scenario with fixtures:

1. **Every auto-checkable rubric item must PASS on `pass.md`.** An item no
   correct answer can satisfy is a broken item, not a strict one.
2. **At least one REQUIRED auto-checkable item must FAIL on `fail.md`.** A
   rubric the wrong answer sails through is not testing anything.

Manual (`check = "manual"`) items are excluded — they exist precisely because no
regex settles them.

A fixture directory that matches no scenario id fails too, so a renamed or
deleted scenario cannot leave orphaned fixtures behind.

## Which scenarios need fixtures

Every scenario with `severity = "critical"` **must** have them: a check the repo
leans on hardest is the worst place to lean on an unproven rubric. `--selftest`
fails when a critical scenario has none.

Everything else is encouraged, and `make eval-harness` enforces a floor via
`--min-fixtures` that only ratchets upward.

## Relationship to `candidates/_example/`

Different jobs, and they are allowed to diverge.

- [`../candidates/_example/`](../candidates/_example/) is a **grading** fixture
  set: full-length agent outputs that the smoke test grades end to end with
  expected scores, proving the scorer works.
- This directory is a **rubric** fixture set: the smallest answers that exercise
  each rubric item, proving the scenario discriminates.

Several `pass.md` files here started as a copy of the corresponding candidate,
because a good candidate answer is already a good correct answer. Editing one
does not require editing the other.
