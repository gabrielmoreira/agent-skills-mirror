# Skill Token Overhead Review Checklist

## Inspect

- Frontmatter description breadth
- SKILL.md length and specificity
- Reference files loaded by default
- Duplicate guidance across skills
- Scripts or dependencies invoked
- Host-specific details inside portable files
- Repeated safety text that could live in bundle docs

## Value Check

Keep overhead when it:

- prevents a known failure
- improves acceptance criteria pass rate
- adds needed safety or approval boundaries
- provides domain-specific process
- reduces repeated manual correction

Trim overhead when it:

- repeats generic model knowledge
- duplicates another skill
- loads irrelevant references
- explains repo history instead of workflow
- includes stale platform facts without a freshness rule

## Recommendation Options

- Keep
- Trim SKILL.md
- Move details to references
- Split skill
- Merge with existing skill
- Narrow trigger description
- Defer until more scenarios prove value
