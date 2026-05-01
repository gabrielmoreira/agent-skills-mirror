---
name: safety-check
description: "**WORKFLOW SKILL** — Risk awareness before action. USE FOR: assessing risks (security, data integrity, compatibility, operational, reversibility) of any task at variable depth. Accepts weight: Light (quick scan), Standard (dimensional analysis), Deep (full Risk Radar with evidence). Can be invoked multiple times in the same flow with increasing weight. DO NOT USE FOR: penetration testing, compliance audits, static security analysis tools."
argument-hint: Describe the task or change to assess for risks
license: MIT
---

# Safety Check — Risk Awareness with Variable Weight

## The Problem You Solve

Agents optimize for "it works" — but never ask "what breaks?". A rename is harmless. A schema change on a public API can break 50 consumers. A migration that drops a column destroys data that no `git revert` can recover. The agent doesn't distinguish between these scenarios because it has no risk radar.

The typical mitigation is "be careful" — a vague instruction that produces vague caution. The agent either ignores it (nothing changes) or applies it uniformly (everything gets a warning, nothing gets real analysis). Both outcomes are useless.

This skill replaces vague caution with **dimensional investigation at variable depth**. Instead of "be careful", the agent learns to ask "what can go wrong in THIS specific dimension, and can I verify it RIGHT NOW?". It transforms reflection into active research with evidence, scaling effort to match real risk — not perceived risk.

## Weight Model

The skill operates at three weights. The weight determines how deep the analysis goes. Start at Light by default; escalate when signals warrant it.

| Weight | Trigger | What it does | Output |
|--------|---------|--------------|--------|
| **Light (1)** | Any non-trivial task. Default when invoked without prior context | Quick scan: identify relevant dimensions, 1-2 questions per dimension, answer with available context | Risk Pulse: 2-3 bullets with dimension + signal |
| **Standard (2)** | Medium risk signals (multiple modules, external deps, persistent data). After contextação reveals complexity. When orchestrator requests | Each relevant dimension is actively investigated: search codebase, read docs, verify consumers, check breaking changes. Produces evidence | Risk Radar: table of dimension × level × evidence × action |
| **Deep (3)** | High risk signals (public API, production data, auth, irreversible). After validator discovers higher-than-expected risk. When orchestrator explicitly requests | All dimensions evaluated. Online research (CVEs, migration guides, changelogs). Cross-reference between dimensions. Complete evidence | Full Risk Radar + Mitigations + Accepted Risks |

Weight can escalate mid-analysis. If a Light scan reveals signals that warrant Standard, say so and escalate. The user or orchestrator can also request a specific weight directly.

## Risk Dimensions — Catalogue (Not a Fixed Checklist)

The agent does NOT evaluate all dimensions every time. At Light weight, evaluate 0-2 most relevant. At Deep, evaluate all that apply. The request context determines which.

### Core Dimensions

| Dimension | Key Question | Signals of Relevance |
|-----------|-------------|----------------------|
| **Security** | Does this change expose data, create injection vectors, or break auth? | Touches auth, input parsing, user data, external APIs, crypto |
| **Data Integrity** | Can data be corrupted, lost, or become inconsistent? | Touches DB schemas, migrations, cache, file I/O, transactions |
| **Backward Compatibility** | Will existing consumers break? | Alters exported APIs, public schemas, contracts, response formats |
| **Operational** | Can this cause downtime, resource exhaustion, or cascading failure? | Alters queries, loops, connections, rate limits, retry logic |
| **Reversibility** _(multiplier)_ | If it goes wrong, can you undo it? What's the blast radius? | `DROP TABLE`, secret push, production deploy, mutated data, public API consumed by third parties |

### Reversibility as Multiplier

Reversibility is not a standalone risk — it's a **multiplier** on every other dimension. Low risk + irreversible = effectively HIGH risk.

The agent MUST challenge claims of reversibility. "Git revert solves it" is often false — production data was already mutated, consumers already consumed the broken API, secrets were already scraped. Ask: *"After reverting the code, is the STATE also reverted?"* If the answer is no, the risk is higher than it appears.

### Contextual Dimensions

Beyond the 5 core dimensions, the agent can add domain-specific dimensions when context demands it:

- **Cost** — cloud resources, API call billing, storage growth
- **Compliance** — GDPR, HIPAA, PCI-DSS, data residency
- **UX Impact** — user-facing behavior changes, accessibility regressions
- **Performance** — latency, throughput, memory footprint

Add contextual dimensions only when the request context strongly signals them. Do not add them speculatively.

## Procedure

### Light (Weight 1)

1. Read the request/context
2. Identify which dimensions are relevant (0-2)
3. For each: 1 quick question, check if you can answer with available context
4. Produce **Risk Pulse**

### Standard (Weight 2)

1. Read request + output from prior skills (task-intent, contextação if available)
2. Identify relevant dimensions (2-4)
3. For each dimension: **actively research** — search codebase, read docs, verify consumers, check breaking changes
4. Evaluate reversibility as multiplier
5. Produce **Risk Radar**

### Deep (Weight 3)

1. Read all accumulated context
2. Evaluate ALL 5 core dimensions + any relevant contextual dimensions
3. For each: **research online** (changelogs, CVEs, migration guides, official docs). Search codebase exhaustively
4. **Cross-reference**: does risk in one dimension affect another? (e.g., security fix that breaks backward compatibility)
5. Evaluate reversibility of each risk individually
6. Produce **Full Risk Radar** with Mitigations and Accepted Risks

## Active Research Gate

For every risk identified, ask: *"Can I verify this right now with available tools?"*

- If **yes** → verify. Fetch the doc, search the repo, check the changelog, read the spec.
- If **no** → mark as `[unverified]` with an explicit note on the impact of being wrong.

Prefer online and up-to-date sources. A risk you CAN verify but DON'T is an unforced error.

## Output Formats

### Risk Pulse (Light)

```
### Risk Pulse
- **[Dimension]**: [signal identified] — [action: proceed / investigate]
- **[Dimension]**: [signal identified] — [action: proceed / investigate]
```

### Risk Radar (Standard / Deep)

```
### Risk Radar

| Dimension | Level | Evidence | Action |
|-----------|-------|----------|--------|
| Security | 🟢/🟡/🔴 | [what was verified] | proceed / investigate / block |
| Data Integrity | 🟢/🟡/🔴 | [what was verified] | ... |
| ... | ... | ... | ... |
| **Reversibility** | ↑ multiplier | [blast radius assessment] | ... |

### Mitigations (Standard/Deep only)
- [Risk]: [concrete mitigation — NOT generic]

### Accepted Risks (Deep only)
- [Accepted risk]: [explicit justification]

### Recommendation
[proceed / proceed with caution / stop and redesign]
```

Levels:
- 🟢 — No signal or verified safe
- 🟡 — Signal detected, manageable with mitigation
- 🔴 — Confirmed risk, requires action before proceeding

## Companion Skills

- **task-intent**: Provides WHY/WHAT FOR context that informs which dimensions are relevant
- **contextação**: The Failure Modes axis from contextação can serve as initial seed. Safety-check expands with active dimensional research
- **task-map**: Accepted risks should be documented in the task-map for future reference
- **error-learning**: If an undetected risk causes a problem, register it as a lesson

## Quality Checklist

- [ ] Weight (Light/Standard/Deep) explicitly declared?
- [ ] Dimensions evaluated are contextual to the request (not a fixed checklist)?
- [ ] For each risk: concrete evidence or marked as `[unverified]`?
- [ ] Reversibility evaluated as multiplier?
- [ ] Recommendation is one of the 3 options (proceed / proceed with caution / stop and redesign)?
- [ ] At Deep weight: online research performed for external risks?
