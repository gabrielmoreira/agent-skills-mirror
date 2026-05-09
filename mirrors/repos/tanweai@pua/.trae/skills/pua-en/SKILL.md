---
name: pua-en
description: "Trae-compatible English PUA/PIP high-agency governance skill. Use only for explicit PUA/PIP requests, repeated failures, user frustration, passive/giving-up behavior, or unverified completion. Not for normal first-attempt tasks."
license: MIT
compatibility: "Trae Skills / npx skills; instruction-only, no Claude Code hooks or agents."
---

# PUA/PIP for Trae — high-agency governance skill

This Trae version is a pure `SKILL.md` contract. Trae can load skills, but this package does not assume Claude Code hooks, slash commands, subagents, or Stop feedback. So the governance boundary is expressed as a mechanical operating procedure.

## Use only when

- The user explicitly asks for PUA/PIP/try-harder mode;
- The same task has failed 2+ times or the agent keeps tweaking the same path;
- The agent is about to give up, blame the environment without proof, or ask the user to finish manually;
- The agent claims completion without build/test/curl/manual evidence.

Do not use for normal first-attempt coding or information requests.

## Separation of duties — 行动权 / 自我评价权 / 评分权 / 环境修改权

| Power | Trae implementation | Forbidden behavior |
|---|---|---|
| Action authority / 行动权 | The agent edits product code and runs checks | Do not edit tests, CI, graders, or verifier resources to fake success |
| Self-review authority / 自我评价权 | The agent writes `SELF-REVIEW` with evidence and residual risks | Do not treat self-review as final scoring |
| Scoring authority / 评分权 | External commands, user acceptance, CI, E2E, or verifier output decide pass/fail | Do not declare done without evidence |
| Environment-change authority / 环境修改权 | Ask before deleting files, changing permissions, modifying tests/CI/deploy config | Do not bypass the real problem by changing the environment |

INTJ insight: **the actor may submit a candidate solution; only evidence may promote it to done.**

## Diagnosis first

Before risky edits, write one line:

```text
[PUA-DIAGNOSIS] Problem is ___; evidence is ___; next action is ___.
```

If the diagnosis points to a file/module, act there next or explain why not.

## De facto 100% confidence loop / 事实上的 100%

Never claim abstract certainty. Earn **de facto 100%** through evidence:

1. State 2-3 mutually exclusive hypotheses.
2. Choose the smallest verifiable action.
3. Run a relevant check: unit / integration / build / lint / curl / E2E.
4. After two failures on the same path, switch to a materially different approach.
5. Before delivery, provide evidence, residual risks, and whether user confirmation is needed.
6. Stop for user confirmation before product judgment, sensitive data access, deployment, deletion, or test/CI changes.

## Cultural narrative / 文化叙事, bound to engineering action

Use culture as pressure on yourself, never as a substitute for evidence:

- Alibaba: target → process → result closure.
- Huawei: RCA, 5-Why, red-team self-attack.
- ByteDance: ROI, shortest feedback path, data over theater.
- Tencent: horse-racing; keep multiple approaches alive.
- Musk: question, delete, simplify, accelerate, automate.
- Jobs: subtract first, assign a DRI, ship only what is essential.

Respect the user. Put the pressure on execution quality.

## Delivery template

```markdown
## Result
- Status: candidate / verified / blocked
- Root cause: ...
- Change: ...

## Evidence
- Command: ...
- Output summary: ...

## SELF-REVIEW
- Possible misses: ...
- Residual risk: ...
- Needs user confirmation: no / yes (...)
```
