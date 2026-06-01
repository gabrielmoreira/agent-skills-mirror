---
name: cross-family-review
description: >
  Dispatch an adversarial cross-family review to a non-Anthropic fleet model.
  Enforces the cross-family independence contract (Epic #2511) at L1-L5
  lifecycle points. Returns ACCEPT/PARTIAL/REJECT verdict + rationale.
argument-hint: "[ticket:#N] [--lifecycle L2|L3|L4] [--model qwen2.5-coder:32b|7b]"
user-invocable: true
disable-model-invocation: false
---

# Cross-Family Review Skill

## Purpose

Dispatches to a non-Anthropic fleet model (Qwen via Ollama) and returns a
structured verdict. Implements the cross-family independence contract:
the reviewing model's AI family MUST differ from the implementing role's family.

## Lifecycle Points

| Point | Who | When | Required? |
|-------|-----|------|-----------|
| L1 | Manager | Pre-implementation orientation | Advisory |
| L2 | Collaborator | Pre-COLLABORATOR_HANDOFF | **REQUIRED** |
| L3 | Admin | Receipt of COLLABORATOR_HANDOFF | **REQUIRED** |
| L4 | Consultant | Pre-CONSULTANT_CLOSEOUT | **REQUIRED** |
| L5 | Manager | Tier-2 anneal on repeated same-family | Advisory |

**Use L2 before every COLLABORATOR_HANDOFF.** L3 and L4 are CI-gated.

## Invocation

```bash
# L2 — standard (7B fast, ~30-60s)
node scripts/global/fleet-red-team-dispatch.js \
  --artifact-type collaborator-handoff \
  --ticket <N> \
  --model qwen2.5-coder:7b

# L2 — high-stakes (32B, ~3-5 min)
node scripts/global/fleet-red-team-dispatch.js \
  --artifact-type collaborator-handoff \
  --ticket <N> \
  --model qwen2.5-coder:32b

# Direct curl (fallback when dispatcher unavailable)
curl -s -X POST http://100.91.113.16:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:7b","prompt":"<review prompt>","stream":false}'
```

## Model Routing (G3 fleet-first)

Dispatch order: `36gbwinresource (100.91.113.16)` → `OpenClaw (100.78.22.13)` → paid.

If all fleet nodes unavailable: record `fleet_unavailable: true` in handoff.
Do NOT substitute a same-family model. Defer if needed (G6 degradation).

## Required Output Fields

### COLLABORATOR_HANDOFF (L2)
```
cross_family_reviewer: qwen2.5-coder:7b@100.91.113.16
cross_family_rating: <N>/100
reviewer_family: qwen
cross_family_findings: <findings>
```

### CONSULTANT_CLOSEOUT (L4)
```
cross_family_verdict: ACCEPT|PARTIAL|REJECT — <model@host> — <rationale>
```

## Advisory vs. Blocking

- L1, L5: advisory only (no CI gate).
- L2: advisory in current soak; CI hard-gate after Epic #2511 C3 promotion.
- L3: hard-gate via `admin-gate` in `baton-gates.yml` (`reviewer_family_verified`).
- L4: advisory in current soak via `GATE_ADVISORY_MODE=1`; promote to blocking
  by unsetting `GATE_ADVISORY_MODE` in `baton-gates.yml` consultant-gate job.

## Related

- `instructions/cross-family-review.instructions.md` — canonical contract
- `scripts/global/megalint/signer-fidelity.js` — `extractAIFamily()` (#2511 C1)
- `scripts/global/megalint/consultant-closeout.js` — `checkCrossFamilyVerdict()`
- `.github/workflows/baton-gates.yml` — consultant-gate advisory bridge (#2511 C3)
