---
description: "Supervisor: Escalate a framework-level concern to AlexMaster's feedback queue"
application: "When the Cardinal Test fails: the planned change touches the framework, not just curation"
agent: Brain Ops
mode: agent
lastReviewed: 2026-04-30
---

# /escalate-to-master

Forward a framework-level concern to AlexMaster. Use this when in-house resolution would constitute scope creep.

## Inputs

- The triggering item (feedback file, observed pattern, heir request)
- AlexMaster workspace location (typically `c:\Development\AlexMaster\AI-Memory\feedback\`)

## Steps

1. Load [escalation-routing](../skills/escalation-routing/SKILL.md) and [escalation-rules](../instructions/escalation-rules.instructions.md)
2. Run the Cardinal Test: *Does AlexMaster do this?* If no, abort — handle in-house instead
3. Identify which Escalate signal fired (tenet, spec, artifact-type, cross-fleet, scope-question)
4. Apply the multi-observation rule — confirm at least one of:
   - 3+ independent heir observations
   - direct impact on brain spec or ACT pass
   - structural class of concern
5. Run a full ACT pass — escalations are framework-level claims; full pass is mandatory
6. Strip project context per [pii-memory-filter](../instructions/pii-memory-filter.instructions.md): no file paths, no client names, no domain identifiers
7. Write the escalation file using [escalation-routing](../skills/escalation-routing/SKILL.md) §Output Template to `AlexMaster/AI-Memory/feedback/<YYYY-MM-DD>-<short-slug>.md`
8. Record in `decisions/curation-log.md` with route = `AlexMaster`, M/S = S
9. **Do not** modify Edition or Mall artifacts pre-emptively — wait for AlexMaster's response

## Verify Before Proceeding

- ✅ Cardinal Test confirmed framework-level (signal cited)
- ✅ Multi-observation rule satisfied
- ✅ Project context stripped (no PII, no domain identifiers)
- ✅ Full ACT pass markers visible in the file
- ✅ Curation log updated
- ✅ No pre-emptive Edition or Mall edits

## Output

A single feedback file in AlexMaster's queue and a curation log entry. The file becomes the contract; AlexMaster acts on it asynchronously.

## When NOT to Use

| Situation | Use instead |
|---|---|
| New skill submission | `/review-skill` |
| Mall add/prune | `/add-store`, `/prune-store` |
| Edition release | `/cut-release` |
| Coherence violation | `/audit-coherence` |
| Single heir's domain complaint | `/triage-feedback` (then handle in-house) |

## Related

- [escalation-routing](../skills/escalation-routing/SKILL.md)
- [escalation-rules](../instructions/escalation-rules.instructions.md)
- `/triage-feedback` (the most common upstream)
