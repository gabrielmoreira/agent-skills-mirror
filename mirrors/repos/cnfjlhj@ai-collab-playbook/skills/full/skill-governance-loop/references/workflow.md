# Skill Governance Workflow

This workflow is intentionally small.
It is designed to be repeated often, not perfected once.

## Phase 0: Frame the job

Classify the request:

- `single-skill review`
- `version update`
- `inventory cleanup`
- `AGENTS.md vs skill boundary`

If the class is unclear, choose the smallest safe class first.

## Phase 1: Start from evidence

Do not start with vague statements such as:

- `this skill feels bad`
- `the description seems weak`
- `we probably have too many skills`

Rewrite the trigger into a concrete case:

- what the user asked
- what skill should have happened
- what actually happened
- why this matters

If there is no historical case yet, treat the current request as the seed case.

## Phase 2: Inventory baseline

For collection-level governance:

1. Run `skills-governance` first.
2. Separate:
   - native skills
   - mirrored or symlinked skills
   - disabled skills
   - suspicious backup-like entries
3. Avoid making keep/disable decisions from memory alone.

For a single skill review, skip straight to Phase 3 after confirming the target path.

## Phase 3: Create the case folder

Use:

```bash
python3 scripts/init_case.py --skill <skill-name> --reason <short-reason>
```

Minimum files:

- `case.md`
- `scorecard.md`
- `decision.md`

These files are the durable memory of the loop.

## Phase 4: Static audit

Run:

```bash
python3 scripts/static_audit.py <skill-path>
```

Treat the result as a baseline, not a verdict.

Static audit is good at finding:

- weak descriptions
- unclear trigger boundaries
- bloated `SKILL.md`
- missing referenced files
- absent versioning
- weak progressive disclosure

Static audit is not enough to prove a skill is useful.

## Phase 5: Empirical check

If the decision matters, add empirical evidence:

- replay the failing prompt
- compare with and without the skill
- compare old and new versions
- use a trigger eval harness if available

If local tooling exists, prefer the existing eval stack instead of inventing another one.

Good prompts for empirical checks are:

- realistic
- multi-step
- close to the original failure mode

Bad prompts are tiny toy prompts that never needed a skill in the first place.

## Phase 6: Decision

Choose one primary decision:

- `keep-enabled`
- `keep-disabled`
- `merge`
- `split`
- `archive`
- `move-to-agents`
- `move-to-skill`

Write why the chosen action is better than the nearest alternative.

## Phase 7: Version update

Bump the version only when behavior or routing meaningfully changes.

Examples that justify a version bump:

- trigger description rewritten
- workflow materially changed
- scripts or references added or removed
- decision boundary changed

Examples that usually do not justify a version bump:

- typo fixes only
- tiny phrasing cleanup with no routing or workflow effect

Use simple semantic progression while the skill is still unstable:

- `0.1.x` for early iterations
- `0.2.x` after the loop is repeatable
- `1.0.0` only when the workflow has survived repeated real cases

## Phase 8: Leave the next hypothesis

Every run should end with one next hypothesis, for example:

- `description too broad; narrow trigger phrases`
- `skill should be split into planning and execution`
- `this rule belongs in AGENTS.md, not in the skill`
- `static quality is good, but no empirical gain yet`

That next hypothesis is what makes the system iterative instead of ceremonial.
