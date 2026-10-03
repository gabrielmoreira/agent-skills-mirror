---
title: Create a new software product
cues:
- a new software product should be built
- software should be built in an empty or starter destination
goal: The bounded product the requester authorized exists in its destination, satisfies its accepted user-visible and operational criteria, and has current evidence for its delivered paths, with the remaining product boundary explicit.
knowledge:
- authorized-software-surface
- project-grounding
- design-integrity
- change-scope
guides:
- change-contract
- user-interface-work
- design-selection
- failure-investigation
- defect-repair
- performance-evidence
- performance-comparisons
- performance-cost-domains
- technology-change
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
---

This task owns delivery of a new working product, including product clarification, technology choices, project initialization, implementation, tests, documentation, packaging, and local verification that serve the accepted outcome. A starter, template, empty repository, or partial scaffold is starting material rather than an existing product contract; preserve constraints it actually establishes without inventing compatibility with behavior no consumer has used.

Establish the product's user or caller, first useful outcome, acceptance criteria, explicit non-goals, authorized destination, and any external or operational effect before creating files. Inspect the destination and the standing instructions that govern it. If it contains unexpected user material, preserve it and stop the affected unit until its role is established rather than treating the directory as disposable or silently redefining the request as a change to an existing product.

Separate choices fixed by the requester, target platform, integrations, or available environment from choices the implementation may make. Prefer an established starter or toolchain only when it satisfies those constraints; otherwise choose the smallest supported mechanism that can deliver the accepted outcome. Record material defaults in re-readable working state, and ask only when alternatives would change the product contract, compatibility, cost, authority, or irreversible structure. Do not add infrastructure, extensibility, services, or dependencies for hypothetical future requirements.

Partition the product into vertical slices under [[guide:work-slicing]]. The first slice establishes only the project foundation its end-to-end behavior needs; a generated scaffold, architecture skeleton, or passing empty build is not a delivered slice by itself.

After focused slices pass, verify their combined behavior from the documented starting state: installation or build where applicable, startup, the primary accepted path, material failure and persistence boundaries, and cleanup. Inspect the complete product surface for unused scaffold, placeholder behavior, accidental secrets, missing documentation, and undeclared external effects.

Report what the product now lets its user do, the destination and material created, the material defaults chosen, the decisive checks, the run or setup instruction the reader needs, and every accepted capability, environment, external effect, or release step left outside the delivered boundary.
