# Skill Governance Rubric

Use this rubric after the static audit and before the final decision.

## Important Distinction

Do not collapse these into one score:

- `static quality`
- `trigger quality`
- `result quality`
- `maintenance cost`

A polished skill can still be useless.
A rough skill can still have strong empirical gain.

## Score Dimensions

Total: 100 points

### 1. Trigger Fit - 25

Questions:

- Does the description describe real user phrasing?
- Is the trigger boundary specific enough?
- Is the skill likely to be loaded for the right jobs and skipped for the wrong ones?

Red flags:

- vague phrases like `helps with tasks`
- no concrete scenarios
- overlaps with three other skills

### 2. Scope Discipline - 20

Questions:

- Is the skill doing one coherent job?
- Does it avoid swallowing neighboring workflows?
- Should the skill be split?

Red flags:

- multiple unrelated jobs in one skill
- planning, execution, and publishing all mixed together

### 3. Progressive Disclosure - 15

Questions:

- Is `SKILL.md` lean enough?
- Are detailed materials pushed into `references/` or `scripts/`?
- Does the body tell the agent when to load more detail?

Red flags:

- giant body with no structure
- duplicated instructions across files
- hidden critical details in random places

### 4. Structural Integrity - 15

Questions:

- Does frontmatter parse?
- Do referenced files exist?
- Is the directory internally consistent?

Red flags:

- missing `SKILL.md`
- broken references
- stale assets or scripts

### 5. Empirical Gain - 15

Questions:

- Does the skill improve real prompts?
- Does it help triggering, output quality, or both?
- Is there evidence beyond personal taste?

Red flags:

- no real case data
- no before/after comparison
- only abstract confidence

### 6. Maintenance Cost - 10

Questions:

- Is the skill expensive to keep current?
- Is it version-sensitive or likely to rot?
- Is the upkeep justified by the gain?

Red flags:

- highly fragile instructions
- depends on many fast-moving tools
- no clear owner or update path

## Suggested Decision Bands

- `85-100`: keep-enabled candidate
- `70-84`: keep, but narrow or revise
- `55-69`: keep-disabled or merge candidate
- `<55`: archive, split, or rewrite from first principles

These bands are defaults, not laws.
Empirical gain can outweigh a mediocre static score.

## Mandatory Notes

Always write down:

- strongest evidence for keeping
- strongest evidence for disabling
- the nearest competing skill
- whether the problem is routing, content, or scope
