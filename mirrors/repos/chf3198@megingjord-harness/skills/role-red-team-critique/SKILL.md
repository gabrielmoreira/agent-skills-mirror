---
name: role-red-team-critique
description: >
  Adversarial cross-family review of baton artifacts, PRs, and governance docs.
  Dispatches a non-Anthropic fleet model (cross-family invariant) and returns
  structured findings with ACCEPT/REJECT/PARTIAL verdicts and hallucination-risk
  classifications. Operates as a bounded, non-blocking advisory layer.
argument-hint: "[artifact-type] [ticket:#N] [--model qwen2.5-coder:32b|7b]"
user-invocable: true
disable-model-invocation: false
---

# Role: Red-Team Critique

## Purpose

Red-Team critique provides an adversarial second opinion on baton artifacts and
governance documents by routing to a cross-family fleet model. The cross-family
invariant (non-Anthropic reviewer) eliminates same-family echo-chamber effects
where the primary model overlooks its own blind spots.

This skill is the canonical umbrella over:
- `scripts/global/fleet-red-team-dispatch.js` — HAMR-wrapped Ollama dispatcher
- `scripts/global/baton-fleet-review-comment.js` — structured comment formatter
- `scripts/global/red-team-evidence-quality.js` — validator for evidence blocks
- `.claude/commands/fleet-review.md` — slash command entry point
- `config/red-team-model-matrix.yml` — A1 model-selection function

## Dispatch Protocol

### When to invoke

Red-Team is ADVISORY on all lanes. Invoke before posting the-collaborator-handoff
on tickets labeled `area:governance`, `area:instructions`, or `area:scripts`. For
`lane:code-change` touching deployed runtime artifacts, invoke before
the-admin-handoff. Invocation is always optional; skipping must be noted in
the-collaborator-handoff as `red_team_review: skipped — <rationale>`.

### How to invoke

```bash
# High-stakes review (32B model, ~3-5 min)
node scripts/global/fleet-red-team-dispatch.js \
  --artifact-type collaborator-handoff \
  --ticket 2317 \
  --model qwen2.5-coder:32b

# Fast fallback (7B model, ~30-60 sec)
node scripts/global/fleet-red-team-dispatch.js \
  --artifact-type collaborator-handoff \
  --ticket 2317 \
  --model qwen2.5-coder:7b
```

Model selection at dispatch time uses `config/red-team-model-matrix.yml` via
`selectModel(taskContext, opts)` in `fleet-red-team-dispatch.js`. Pass
`--stakes high` to force 32B; omit for automatic selection per the matrix.

### Cross-family invariant

The dispatched model MUST differ from the primary authoring model family.
Claude Code sessions use Anthropic models; therefore all red-team dispatches
MUST target Ollama-hosted models (Qwen, Llama, Mistral, etc.) or an
OpenRouter non-Anthropic provider. Dispatching to another Claude model
violates the cross-family rule and produces findings that must be discarded.

Enforce via `config/red-team-model-matrix.yml` `cross_family_required: true` field.

## Output Format

Each red-team run produces a structured comment posted to the linked GitHub issue.
The comment format is governed by `scripts/global/baton-fleet-review-comment.js`.

### Per-finding structure

Every finding carries three required fields:

| Field | Values | Description |
|---|---|---|
| verdict | ACCEPT / REJECT / PARTIAL | ACCEPT = valid; REJECT = false positive; PARTIAL = needs iter |
| text | string | One-sentence finding description |
| hallucination_risk | low / medium / high | Likelihood the model invented this finding |

`hallucination_risk: high` findings MUST be discarded or independently verified
before acting. The primary author classifies risk per these heuristics:
- **low**: finding cites a specific line, file, or label that exists in the diff
- **medium**: finding references a pattern or convention that is plausible
- **high**: finding cites an arxiv URL, a non-existent function, or implausible claim

arxiv URLs are auto-stripped by `stripArxivHallucinations()` in the dispatcher.
Any stripped reference automatically elevates finding risk to `high`.

### Rubric output

The comment includes a summary rubric block:

```
## Red-Team Rubric (iteration N)
| Goal | Score | Rationale |
|---|---|---|
| G1 Governance | N/10 | ... |
| G2 Quality   | N/10 | ... |
```

Rubric scores are deterministic: each goal has a binary checklist and the score
is `(boxes_checked / boxes_total) * 10`. Do NOT inflate scores to avoid
uncomfortable findings. A perfect 10/10 across all goals on a non-trivial
artifact is a red flag indicating the model failed to engage adversarially.

Score-honesty discipline: if the model returns 9s across orthogonal goals for a
multi-file change, treat the output as `hallucination_risk: high` for the rubric
and re-run with a more specific prompt or escalate to the 32B model.

### Iteration protocol

Red-Team converges in 2-3 iterations per the memory `feedback-red-team-iteration-pattern`:

1. **Iteration 1**: broad sweep — primary author posts findings to the issue
2. **Iteration 2**: primary explicitly classifies each finding as ACCEPT/REJECT/PARTIAL
   and re-prompts with yes/no question format for each PARTIAL item
3. **Iteration 3** (only if needed): targeted re-run on unresolved PARTIAL items

Stop after 3 iterations regardless of unresolved partials. Remaining partials
become `recommended_follow_ups` in the-collaborator-handoff.

## Score-Honesty Discipline (normative)

- Rubric scores must reflect the deterministic checklist output only.
- Do not add subjective positive framing that inflates scores.
- If a goal has no applicable checklist items for this artifact type, score it N/A.
- Record `boxes_checked`, `boxes_total`, and `score` for audit traceability.
- A closeout citing red-team rubric MUST include the raw `boxes_checked/boxes_total`
  for at least two goals.

## Cross-Runtime Loadability (AC6)

This skill must be loadable in:
- Claude Code: via `CLAUDE.md` include reference
- Codex AGENTS.md: via `skills/role-red-team-critique/SKILL.md` reference block
- Copilot Agent HQ: as a skill card with the frontmatter `name` field as identifier
- Antigravity SDK: via skill registry JSON entry pointing to this file

The skill body MUST NOT contain Claude-Code-specific syntax. Cross-runtime
loadability is validated by the loadability smoke test in the test spec.

## Must Not Do

- Do not use another Anthropic/Claude model as the red-team reviewer.
- Do not act on `hallucination_risk: high` findings without independent verification.
- Do not run more than 3 iterations on a single artifact.
- Do not block the baton on unresolved red-team partials — they become follow-ups.
- Do not inflate rubric scores to signal "all good" when the checklist disagrees.
