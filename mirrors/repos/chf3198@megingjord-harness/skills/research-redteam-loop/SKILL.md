---
name: research-redteam-loop
description: >
  Web-augmented cross-family consensus gate: produce/refresh research →
  fleet/free-cloud red-team rating /100 → Manager reworks on fail → repeat
  until > gate or cap exhausted. G3-first: fleet → free-cloud; no paid path.
argument-hint: "#N [--gate 93] [--web] [--reviewer cross-family] [--cap 5]"
user-invocable: true
disable-model-invocation: false
---

# Research Red-Team Loop Skill

## Purpose

Bundles the proven research→adversarial-review→rework→consensus cycle (validated
in #2710: 78→92→91→94 ACCEPT) into a single invocation. Fleet/free-cloud only.
Cross-family invariant: reviewer MUST NOT be Anthropic/Claude family.

## Invocation

```
/research-redteam-loop #N [--gate 93] [--web] [--cap 5]
```

**Arguments:** `--gate N` = minimum acceptance score (default 93). `--web` = inject
web search evidence (default on; degrades gracefully). `--cap N` = max iterations.

## Loop Protocol

1. **Produce/refresh** the research deliverable for issue #N (read existing body
   or linked wiki page).
1a. **Corpus-overlap stage (MANDATORY before ACCEPT — #2801).** Run
   `node scripts/global/corpus-overlap-scan.js --scope-file <deliverable> --json`.
   It reuses the #2617 tokenizer but scans **open AND closed** issues (the near-miss
   #2518 was a *closed* epic) via overlap-coefficient. Embed `buildOverlapBlock`
   (`related_tickets:` + `overlap_decision:`) in the deliverable and inject
   `reviewerOverlapFragment` into the reviewer prompt so the red-team validates the
   boundary (overlap vs conflict vs redundancy vs gap). **ACCEPT is blocked** when
   `shouldBlockAccept(scan, deliverable)` is true (overlap present, no
   `overlap_decision:`). Distinct from #2617/Epic #2623 (ticket-CREATION stage).
2. **Web augmentation**: fetch 3+ relevant references via WebSearch; inject into
   reviewer prompt. On search failure, log `web-search-unavailable` to
   `~/.megingjord/incidents.jsonl` and continue without web context.
3. **Dispatch review** (G3 fleet-first) — canonical CLI is `cascade-dispatch.js` (#2858 / Epic #2926 D1):
   - `node scripts/global/cascade-dispatch.js --prompt "<review prompt>" --model qwen2.5-coder:32b [--json]`
     — orchestrates fleet → free-cloud fallback → escalation; timeouts per `timeout-policy.json`. It already
     emits `[cascade] escalate→<tier>` to stderr on escalation.
   - On a fleet **availability** failure it fails over to the $0 free-cloud chain automatically (#2619/#2621);
     premium is reached only on a free-cloud **capability** failure (Epic #2926 D4).
   - `fleet-red-team-dispatch.js` is a LIBRARY (no CLI) — do NOT invoke it directly; it redirects here.
   - Cross-family invariant enforced at every tier (no Anthropic model).
4. **Score check**: if score > gate **and** `shouldBlockAccept` is false → post
   ACCEPT and stop. If overlap blocks (no `overlap_decision:`), record the boundary
   and re-review. Else → post ITER comment and proceed to rework.
5. **Manager rework**: revise deliverable using reviewer findings + web context.
6. **Repeat** steps 2–5 until ACCEPT or cap exhausted → post REJECT.

## Verdict Comments (posted to target issue)

Per-iteration:
```
RESEARCH_REDTEAM_ITER: N | score=<N>/100 | reviewer=<model@host> | web=<yes|no>
```
Terminal ACCEPT:
```
RESEARCH_REDTEAM_ACCEPT: score=<N>/100 | reviewer=<model@host> | iterations=<N>
```
Terminal REJECT (cap hit):
```
RESEARCH_REDTEAM_REJECT: max_iterations_reached | final_score=<N>/100
```
Final verdict + per-goal vector recorded to `~/.megingjord/incidents.jsonl`.

## Infrastructure Used (AC6 — no new plumbing)

- `scripts/global/fleet-red-team-dispatch.js` — HAMR-wrapped Ollama dispatcher
- `scripts/global/free-cloud-dispatch.js` — $0 cloud chain (gemini/groq/cerebras)
- `scripts/global/corpus-overlap-scan.js` — deterministic overlap scan (open+closed; #2801)

## Goal Lens

G3 Zero-Cost: fleet/free-cloud only; zero paid API calls during loop.
G2 Quality: gated loop with calibrated scoring, bounded iterations, audit trail.
G8 Observability: structured per-iteration comments + incidents.jsonl record.

## Related

- `skills/cross-family-review/SKILL.md` — cross-family invariant contract
- `skills/role-red-team-critique/SKILL.md` — single-shot adversarial review
- `config/red-team-model-matrix.yml` — model selection matrix
- `.claude/commands/research-redteam-loop.md` — slash command entry point
- `tests/research-redteam-loop.spec.js` — eval-harness test suite
