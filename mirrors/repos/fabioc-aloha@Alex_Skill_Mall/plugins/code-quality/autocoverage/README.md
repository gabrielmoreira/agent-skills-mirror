# autocoverage

Use when a user asks to generate or improve unit tests with measurable coverage gains using a strict staged workflow (build -> baseline -> plan -> generate -> verify -> coverage delta). Trigger phrases: generate unit tests, improve coverage, write tests for uncovered code, make PR-ready tests. Do not use for integration/E2E testing, production refactoring, or planning-only requests without code generation intent.

## Quick Facts

| Field | Value |
| --- | --- |
| **Category** | code-quality |
| **Shape** | `.S..` |
| **Tier** | standard |
| **Token cost** | ~16314 tokens |
| **Engines** | copilot |
| **Requires Edition** | >=1.0.0 |
| **Keywords** | autocoverage, user, asks, generate, improve, unit, tests, measurable |

## Installation

From ACT Edition:

```text
/mall install autocoverage
```

Or manually copy the plugin contents to `.github/skills/local/autocoverage/`.

## Artifacts

- **skill**: `SKILL.md`

## Shape: `.S..`

Skill only -- domain knowledge loaded when pattern matches.
