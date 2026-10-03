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
  - When the evidence establishes a defect in a supplied Degardis source that the requester authorized correcting, the host permits changing that source, and that defect has neither an unfinished revision responsible for it nor a revision outcome on this route
- task: plan
  applicability:
  - When the evidence establishes a defect in a supplied Degardis source that the requester authorized correcting, host instructions prohibit changing that source, and that defect has neither an unfinished plan responsible for it nor a planning outcome on this route
---

Close every started case as supported, failed, blocked, or inconclusive rather than smoothing a gap into a general judgment.
