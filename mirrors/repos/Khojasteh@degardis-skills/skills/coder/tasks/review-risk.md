---
title: Review code or a change for risk
cues:
- what is wrong or risky in named project material or a change is asked
goal: Every reported finding is an actionable departure from an established contract, ranked by the decision it forces, with no project source edited.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- change-contract
- user-interface-work
- performance-evidence
- performance-comparisons
- performance-cost-domains
- technology-change
- implementation-modernization
- test-work
- existing-test-maintenance
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
- work-slicing
handoffs:
- task: implement-change
  applicability:
  - When the requester authorized correcting what the review finds, and an established finding within that authority needs a correction that changes anything beyond reader-facing project text and is neither made nor pending on this route
- task: document-software
  applicability:
  - When the requester authorized correcting what the review finds, and an established finding within that authority needs a correction that changes only reader-facing project text and is neither made nor pending on this route
---

Choose the boundary the request supplies: compare a change against its base, or inspect the named material as it stands. Read the change or entry points first, search for the contracts and consumers they touch, then inspect only the implicated units, tests, configuration, schemas, persisted formats, and recorded artifacts. Treat the covered surface as bounded when the request or available evidence does not establish the whole set.

A review establishes its findings by reading rather than by running the software. Inspect the change, its history, and the CI results, logs, and reports recorded for the reviewed revision; a result recorded for another revision or configuration is not evidence about this one. Run nothing that exercises the software's behavior, such as its tests, benchmarks, or the application itself, and nothing that writes outside disposable output. Before any other project command, establish whether it can load or execute code, plugins, build scripts, hooks, configuration, or dependencies from the reviewed material. An adopted check may run only when each possible result could change a finding and either it is established not to execute that material or the requester has explicitly authorized the identified execution and its effects are understood and confined to disposable output. A candidate that only execution could settle stays an unverified risk beside the check that would settle it.

The guide conditions on this page are the concerns to screen the reviewed material against; read each guide whose condition holds. Keep any other material risk the material exposes under the same finding bar rather than forcing it into the nearest named concern or dropping it. Establish or refute each candidate under [[principle:finding-evidence]], and drop observations that ask the reader for no action.

Lead with whether anything should block the requested decision. Report established findings in action order with the smallest revealing location and concise remediation grounded in a mechanism the project already uses. Keep unverified risks separate from established findings. State the coverage boundary only where it limits the review.
