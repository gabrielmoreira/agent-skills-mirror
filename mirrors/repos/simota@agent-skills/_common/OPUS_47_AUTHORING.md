# Opus 4.7 Authoring Protocol

> Source: Anthropic "Best Practices for Using Claude Opus 4.7 with Claude Code" (2026)
> Owner: Architect (canonical doc); referenced by orchestrators, reviewers, investigators

Shared protocol that aligns generated and existing skills with Opus 4.7 default behaviors. Reference this file from any SKILL.md that needs Opus 4.7 alignment instead of duplicating the rules.

---

## Why This Exists

Opus 4.7 changes several defaults vs Opus 4.6:

| Default | Opus 4.6 | Opus 4.7 |
|---------|----------|----------|
| Response length | Verbose by default | Calibrated to task complexity |
| Tool calls | Eager | Reasons more, calls less |
| Subagent spawning | Frequent | Sparse — must be explicit |
| Extended thinking | Fixed budget supported | Adaptive only (per-step decision) |
| Default effort | (n/a) | `xhigh` |

Skills that assume 4.6 behaviors will under-deliver on 4.7. Apply the seven principles below.

---

## The Seven Principles

### P1. Front-Loaded Task Specification

State intent, constraints, acceptance criteria, and file locations on the first turn. Do not reveal requirements progressively.

**Apply by:**
- Trigger Guidance enumerates first-turn required inputs.
- INTERACTION_TRIGGERS batch related confirmations into a single multi-question prompt.
- AUTORUN `_AGENT_CONTEXT` schemas require all decision-affecting inputs up front; ambiguity resolves to safe defaults (documented), not follow-up questions.

### P2. Calibrated Response Length

Opus 4.7 calibrates verbosity to task complexity. Skills must state expected output shape and length explicitly.

**Apply by:**
- Reference `_common/OUTPUT_STYLE.md` from the SKILL.md `Output Contract` section. That file is the single source of truth for tier definitions (`S`/`M`/`L`/`XL`), banned filler patterns, and format priority.
- Declare a default tier and per-task overrides in SKILL.md instead of duplicating style rules.
- Output sections specify length envelopes (line counts, bullet counts, table dimensions).
- `_STEP_COMPLETE` and `## NEXUS_HANDOFF` blocks already provide envelopes — keep them; do not let agents emit free-form summaries instead.
- For prose, state length explicitly: "1-3 sentence summary", "5-bullet checklist".

### P3. Explicit Tool-Use "When/Why"

Opus 4.7 reasons more and calls tools less by default. Skills that need aggressive tool execution must say so explicitly.

**Apply by:**
- For each tool a skill expects to use, document the trigger condition (when) and value (why).
- For eager tool use: "Read all candidate files before deciding, even if confidence seems sufficient — grounding cost is low compared to wrong-decision cost."
- For think-first behavior: "Reason about the design before invoking tools; do not begin file reads until the section contract is decided."

### P4. Explicit Parallel Subagent Triggers

Opus 4.7 spawns fewer subagents by default. Skills that benefit from parallel fan-out must spell it out.

**Apply by:**
- For independent subtasks (multi-file reads, multi-target analysis, voting/consensus), include: "Spawn N subagents in the same turn when fanning out across [items]."
- Reference `_common/SUBAGENT.md` for the parallelism-layer choice (skill-internal subagents vs Agent Teams).
- Do not assume the model will infer parallelism from workflow structure alone.

### P5. Adaptive Thinking Hints

Extended thinking with fixed budgets is no longer supported; Opus 4.7 decides per step. Skills steer this at decision points.

**Apply by:**
- High-stakes decisions: "Think carefully and step-by-step before responding; this decision affects [downstream impact]."
- Throughput-sensitive points: "Prioritize responding quickly rather than thinking deeply."
- Do not embed numeric thinking budgets — they are no longer respected.

### P6. Effort-Level Awareness

Default effort is `xhigh`. Skills should be sized for `xhigh` as the assumed runtime envelope.

| Effort | When skills should expect this |
|--------|-------------------------------|
| `low`/`medium` | Cost/latency-sensitive narrow scope; lightweight skills |
| `high` | Concurrent sessions or budget constraints |
| `xhigh` (default) | Most coding/agentic skills — design baseline |
| `max` | Reserve for genuinely hard problems; flag in `description` if a skill expects `max` |

### P7. Delegation-Engineer Framing

Treat the model as a capable engineer being delegated to, not a line-by-line pair programmer.

**Apply by:**
- Skills must be self-directing for the bulk of their workflow.
- Reserve user check-ins for genuine `Ask first` decisions, not micro-steps.
- Provide enough context inside the skill (or via references) that the model does not need to ask clarifying questions for documented decisions.
- Avoid micro-step instructions that prevent the model from exercising judgment; prefer phase-level contracts with verification gates.

---

## Per-Role Apply Matrix

Reference this matrix to know which principles your skill must address.

| Role | Critical (◎) | Recommended (○) |
|------|---|---|
| Orchestrators (Nexus, Titan, Sherpa, Rally, Arena, Magi, Darwin, Orbit) | P4, P6, P7 | P1 |
| Investigators (Scout, Lens, Trail, Atlas, Fossil, Triage) | P3, P5 | P2 |
| Reviewers (Judge, Gauge, Sentinel, Probe, Radar, Warden, Attest) | P2, P5 | P1 |
| Builders (Builder, Artisan, Forge, Anvil, Native) | P5, P7 | P3 |
| Designers (Vision, Muse, Palette, Schema, Gateway, Stratum) | P1 | P5 |
| Knowledge/Meta (Lore, Compass, Sigil, Architect) | P6, P7 | P1 |

(◎ = address explicitly in SKILL.md; ○ = address if relevant)

---

## Validation Hooks

When validating a skill against this protocol, use the seven checks below (mirrors Architect `validation-checklist.md` Section 7):

- R7.1 Front-loaded context capture
- R7.2 Calibrated response length
- R7.3 Explicit tool-use rationale
- R7.4 Parallel subagent triggers
- R7.5 Adaptive thinking hints
- R7.6 Effort-level expectations declared
- R7.7 Delegation-engineer framing

Pass criterion: skills must address all `◎` principles for their role; aim for ≥ 5/7 total.

---

## How to Reference This File

In a SKILL.md:

```markdown
- Author for Opus 4.7 defaults. See `_common/OPUS_47_AUTHORING.md` (apply P[X], P[Y], P[Z] for this role).
```

Avoid duplicating the principle text in individual SKILL.md files. Cite by ID (P1–P7) and let this file be the single source of truth.
