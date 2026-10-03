---
title: Assess a codebase and prioritize improvements
cues:
- an existing codebase or software surface should be assessed for which improvements it needs and in what order
- the overall condition of an existing codebase or software surface should be assessed
goal: A prioritized, evidence-backed roadmap, led by the surface's overall condition when the request asks for it, covers the named software surface at the fixed depth, distinguishes inspected, sampled, and unreached parts, and leaves project source unchanged.
knowledge:
- authorized-software-surface
- project-grounding
- codebase-health-dimensions
guides:
- user-interface-work
- failure-investigation
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
  - When the requester authorized carrying out what the assessment recommends, and an established action within that authority changes anything beyond reader-facing project text and is neither carried out nor pending on this route
- task: document-software
  applicability:
  - When the requester authorized carrying out what the assessment recommends, and an established action within that authority changes only reader-facing project text and is neither carried out nor pending on this route
---

Produce one ranked account of what the existing software surface should improve, changing nothing in the project even when a repair appears obvious.

**Scope and depth.** Before analysis, establish the named surface, its current revision or working tree, the reader who will act on the result, whether the concern is broad or named, and the reading depth. The present codebase is the subject; do not invent a base revision. A narrowed assessment stays within its named concern except where evidence establishes a prerequisite of that concern or a limit on it. Fix the depth before reading units: if it covers the mapped surface, inspect every admitted unit; otherwise partition the surface and sample from evidence of risk rather than convenience. Completed bounded depth supports a roadmap with explicit limits; stopping before the fixed depth hands over the verified state and the next safe unit instead of presenting a partial roadmap as complete.

**Map.** Map the named surface before prioritizing: use manifests, build and deployment declarations, entry points, configuration, ownership boundaries, and directory structure to identify components and relationships, distinguishing maintained source from generated, vendored, lock, and output material.

**Evidence.** Spend reading from lower-cost, nearer evidence toward implicated code: applicable instructions and requester-supplied material; prior assessments, architecture decisions, and technical-debt registers; recorded CI, build, job, test, coverage, analyzer, audit, profile, and benchmark results; the structural map; change history for frequently changed or repair-heavy areas; targeted risk searches; then the mapped units those signals implicate. Place an unlisted source by its cost and distance from the question, and reuse a prior assessment that still matches the surface by assessing what changed. Do not fully read generated, vendored, lock, minified, or dependency material when its source or a targeted search settles the concern.

Bind recorded evidence to the revision, configuration, date, and scope it can describe. A confirmed revision mismatch makes it unavailable for the present claim; when identity is incomplete, use history to test whether later changes reached its scope where possible, and otherwise carry its currency as an assumption. Record missing evidence in re-readable working state and continue from what exists, lowering confidence only where the missing source matters.

**Commands.** An assessment describes the repository as received. Read the tests and their recorded results instead of running the suites: a test or benchmark run exercises the software, which makes it verification rather than assessment, and a result the roadmap needs but this assessment cannot obtain remains an evidence gap. Run no fix mode, snapshot update, code generation, dependency installation or upgrade, migration, persistent service, or command that mutates application or external state. An adopted build, linter, analyzer, diagnostic, or other command that exercises no behavior runs only when the project has adopted it, its effects are understood and confined to disposable local output outside the assessed surface, and each possible result could change a finding, action, or priority; a run wanted only to raise confidence in an established finding does not meet the last of these. Availability, a familiar command name, ecosystem convention, and read-only intent establish neither adoption nor harmless effects.

**Stopping.** Set each line of inquiry's stopping condition before reading it: stop when the concern is established or refuted, its affected surface is closed, required evidence is unavailable, or the fixed depth is exhausted and more reading cannot change a finding, action, or priority. A second pass needs a new question. A line that stops open is reported with its uncertainty and the evidence that would settle it.

**Dimensions and findings.** A broad assessment follows every material concern the evidence exposes: it weighs the three dimensions every broad assessment weighs and checks what opens each of the seven others, and a dimension that does not open is closed without being shown healthy. A narrowed assessment applies the same finding bar inside its scope. Let the request and observed project state decide which concerns are material rather than a conventional audit checklist, and consult external authority only after a dimension opens and only for a claim its finding needs. The ten dimensions are common owners, not an exhaustive taxonomy: retain another material concern when it meets the same finding bar, with its cause, reaching scenario, impact, and why no named dimension owns it. Admit every candidate under [[principle:finding-evidence]]; architecture labels, code size, dependency age, and hypothetical extensibility are signals, not findings.

**Roadmap.** Recommend an action only when evidence supports both the problem and its direction. A suspected production defect, unknown intended behavior, unreliable baseline, or unapproved compatibility change can make a nominally behavior-preserving action preserve the wrong result, turn an accident into a contract, or claim safety from evidence that cannot carry it. These are common shapes, not a closed list: any unsettled condition with the same effect is a finding the dependent actions must wait on. Name it as a prerequisite of every action whose safety depends on it and hold only those actions; independent areas continue. A small diff, easy reversal, or low implementation cost does not settle the condition, so a dependent behavior-preserving change waits for a separately scoped defect repair, contract decision, or baseline. Tests that record current behavior make a later change observable while intended behavior remains unknown, but that record does not establish that the behavior is correct or must be preserved, and a passing suite cannot override contradictory contract evidence.

Write the roadmap for the person deciding what work starts next, including a later reader who did not observe the assessment. Name the assessed surface, revision or working tree, intended reader, coverage boundary, and first action before background. When the request asks for the surface's overall condition, lead with it: for each dimension in scope, name the established findings it holds by identifier, or state that the covered material showed none or that the dimension did not open, each of which reports coverage rather than health. If the evidence supports no action, say so without implying health for sampled or unreached material. Keep demonstrated defects distinct from the actions that address them, and give a defect a stable identifier when more than one action or later reference needs to point to it. Rank defect severity, when useful, by impact and confidence, and rank actions by prerequisite and readiness into these horizons, omitting any that holds no action:

- **Now:** established, unblocked work the reader should start next, including conditions that must be settled and high-risk correctness or safety work.
- **Next:** supported work whose prerequisite, decision, or earlier action prevents it from starting now.
- **Later:** bounded lower-risk work that should be reassessed before execution.

Give more detail to nearer work. A Now action identifies the root cause, cited surface, intended outcome, smallest coherent change, behavior to preserve, prerequisites, verification strategy, documentation effect, and residual risk. A Next action identifies the problem, cited location, outcome, and prerequisite. A Later action can be one line naming the action and its cited location. Split actions with independent causes, and omit estimates, speculative extensibility, optional churn, and benefits the evidence did not establish.

Close with only material that changes what the reader does: unavailable evidence, commands run or skipped where that affects confidence, assumptions and open questions, pre-existing failures, coverage limits, and what was deliberately withheld. Keep those separate from confirmed findings, and, unless the request already authorized carrying out the recommendations, state that implementation needs a separately scoped request. Do not repeat the roadmap as per-dimension reports, narrate the assessment procedure, reproduce code or tool output in place of citations, or list candidates that failed the evidence bar.
