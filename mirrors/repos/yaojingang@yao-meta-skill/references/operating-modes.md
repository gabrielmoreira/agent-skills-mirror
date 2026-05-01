# Operating Modes

This playbook expands the compact mode routing in `SKILL.md`.

## Scaffold

Use when:

- the skill is exploratory
- the workflow is personal or short-lived
- eval and packaging cost would exceed reuse value

Default deliverables:

- `SKILL.md`
- `agents/interface.yaml`
- `references/` only when a small amount of deferred reading is clearly helpful

Avoid:

- automatic `scripts/`, `evals/`, or `manifest.json`
- packaging targets the user did not ask for

## Production

Use when:

- the skill will be reused by a team
- routing mistakes would waste time
- a small amount of deterministic automation improves reliability

Default deliverables:

- lean `SKILL.md`
- `agents/interface.yaml`
- `references/` for policies, checklists, or examples
- `scripts/` only when deterministic logic is real
- `evals/` when trigger or output quality should be checked
- `manifest.json` when lifecycle metadata matters

Minimum gates:

- `resource_boundary_check.py`
- `validate_skill.py`
- `trigger_eval.py` when route confusion is plausible

## Library

Use when:

- the skill is organizationally important
- the package will be shared broadly
- maintenance and portability matter
- the skill itself shapes how other skills are created or governed

Default deliverables:

- trigger positives, negatives, and near neighbors
- packaging expectations
- maintenance metadata
- visible regression evidence
- governance review readiness

Minimum gates:

- `resource_boundary_check.py`
- `governance_check.py`
- `trigger_eval.py`
- `cross_packager.py` for requested targets

## Escalation Rules

- stay in Scaffold unless reuse is clearly real
- move to Production when team reuse or route confusion matters
- move to Library when the skill becomes shared infrastructure or a governed asset

## Context Discipline

- a mode upgrade does not justify a larger `SKILL.md`
- higher rigor should mostly add better references, reports, evals, and metadata
- if a mode upgrade bloats the initial load, move detail out before adding more checks
