# architecture-threat-modeling

Reference for threat model analysis, C4 architecture diagrams, trust boundaries, dependency risk scoring, and security review.

## Type

**Knowledge package** -- install to `AI-Memory/knowledge/`, not to the brain. Consult during architecture planning or security audit phases.

## Source

Distilled from `archipilot` (agency-microsoft/playground) on 2026-05-03. 7 of 25 skills selected for reference value:

- `convert-tm7` -- parse Microsoft Threat Modeling Tool files
- `model-analysis` -- analyze architecture models for patterns and risks
- `security-analysis` -- comprehensive security posture review
- `trust-boundaries` -- identify and validate trust boundary definitions
- `executive-summary` -- generate stakeholder-ready architecture summaries
- `flow-analysis` -- trace data flows and identify exposure points
- `dependency-risk-scoring` -- score and prioritize dependency risks

## Install

```bash
mkdir -p "AI-Memory/knowledge/architecture-threat-modeling"
cp knowledge/architecture/architecture-threat-modeling/*.md "AI-Memory/knowledge/architecture-threat-modeling/"
```

## When to Consult

- Starting a new project and need architecture documentation patterns
- Preparing for a security review or threat modeling session
- Analyzing an existing system's trust boundaries
- Writing an architecture decision record (ADR)
- Scoring dependency risks for a new integration
