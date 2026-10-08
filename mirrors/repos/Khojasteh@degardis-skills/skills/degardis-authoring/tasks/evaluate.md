---
title: Evaluate observed skill behavior
cues:
- the requester asks to obtain behavioral evidence by running a skill with an agent
- the requester supplies completed interactions and asks what the observed agent behavior establishes about the skill
goal: Return a behavior claim no broader than the supplied or freshly obtained evidence supports, with this task itself changing neither source nor evaluated artifacts.
knowledge:
- working-accounts
- evidence-bounds
- compiler-evidence
- compiler-integrity
- behavior-attribution
- behavioral-evaluation
guides:
- effective-compiler
- fresh-evaluator-protocol
- supplied-artifact
handoffs:
- task: revise
  applicability:
  - When the evidence establishes a defect in supplied Degardis source, the requester asked to fix it, changing the source is authorized and permitted by the host, and no unfinished revision or revision outcome on this route covers the defect
- task: plan
  applicability:
  - When the evidence establishes a defect in supplied Degardis source, the requester asked to fix it, host instructions prohibit changing the source, and no unfinished plan or planning outcome on this route covers the defect
---

Close every started case as supported, failed, blocked, or inconclusive rather than smoothing a gap into a general judgment.
