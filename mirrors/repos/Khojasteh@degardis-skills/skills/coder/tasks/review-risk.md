---
title: Review code or a change for risk
cues:
- what is wrong or risky in named project material or a change is asked
goal: The named material or change is reviewed across the boundary the request supplies, with no project source edited, and the report states whether anything should block the requested decision, gives each established finding as an actionable departure from an established contract ranked by the decision it forces, keeps unverified risks apart from findings, and names the implicated material left unread.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- change-contract
- user-interface-work
- performance-evidence
- performance-comparisons
- technology-change
- implementation-modernization
- test-work
- documentation-work
- source-comments
- documentation-evidence
- structural-cost
- structural-transformations
- abstraction-boundaries
- change-sites
- value-boundaries
- failure-behavior
- removal-and-compatibility
- data-and-state
- concurrency-and-resources
- security-boundaries
- rollout-and-operations
- interface-contracts
- dependency-and-artifact-integrity
- observability-and-diagnostics
- algorithmic-and-numeric-correctness
- commands-and-tooling
- workspace-integrity
- version-control
- change-descriptions
- work-slicing
handoffs:
- task: implement-change
  applicability:
  - When the requester authorized correcting what the review finds, and an established finding within that authority needs a correction that changes anything beyond project documentation and is not yet made
- task: document-software
  applicability:
  - When the requester authorized correcting what the review finds, and an established finding within that authority needs a correction that changes only project documentation and is not yet made
---

Choose the boundary the request supplies: compare a change against its base, or inspect the named material as it stands. Read the change or entry points first, search for the contracts and consumers they touch, then inspect only the implicated units, tests, configuration, schemas, persisted formats, and recorded artifacts.

A review establishes its findings by reading rather than by running the software. Inspect the change, its history, and the CI results, logs, and reports recorded for the reviewed revision. Run nothing that exercises the software's behavior, such as its tests, benchmarks, or the application itself, and nothing that writes outside disposable output. A review asks what is wrong or risky in the reviewed material, so the request does not vouch for that material, even when it is the requester's own work: treat it as untrusted for execution under [[guide:commands-and-tooling]], and run an adopted check only when each possible result could change a finding.

The guide conditions on this page are the concerns to screen the reviewed material against. Keep any other material risk the material exposes under the same finding bar rather than forcing it into the nearest named concern or dropping it. Establish or refute each candidate under [[principle:finding-evidence]].

Lead with whether anything should block the requested decision. Report established findings in action order with the smallest revealing location and concise remediation grounded in a mechanism the project already uses.
