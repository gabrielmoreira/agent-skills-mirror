---
title: Evidence behind a software finding
applicability:
- Before a candidate defect, risk, or improvement is reported or acted on
---

A capable agent reports a lead as a finding, a preference as a defect, and one cause as several findings; each costs the reader a decision the evidence does not support. A candidate becomes a finding only with four linked parts, stated here for a candidate judged by what the software does when it runs:

1. A concrete input, state, configuration, or sequence and a reachable caller or entry point that can supply it.
2. A traced path to the smallest location where behavior departs from an established contract.
3. The expected and actual result, with the contract that supplies the expectation, and the impact: what a user, operator, or downstream system then experiences.
4. The guards, caller preconditions, configuration, version behavior, tests, and alternate paths searched for that would refute the candidate.

A candidate judged another way keeps the same four parts in its own terms:

- **What a reader or consumer relies on**, as with documentation or test quality: the reader task or consuming contract that reaches the passage or check, the passage or check where it departs from what the evidence supports, the expected and observed effect on that reader or consumer, and the evidence searched for that would refute it.
- **What a structure, mechanism, or dependency costs**, rather than a wrong result: the named future change or measured workload that meets the cost, the location that imposes it, what that change or workload pays here against what it would pay without the candidate, and the evidence searched for that would refute it, such as a measurement within budget or a change the structure does not obstruct.

A warning, failed job, log line, suspicious name, or familiar defect class is a lead until the mechanism is traced. Report a lead that could still matter as an unverified risk beside the check that would settle it, never as a finding. A departure from ecosystem custom, an unadopted tool, or a missing dependency is a defect only with project evidence that the resulting behavior or cost matters here. A clarity or maintainability issue is a defect only when a concrete future change, named with it, would be misled or made costlier by it; unfamiliar style, a different abstraction, missing comments, and a locally surprising mechanism are not defects by themselves.

Independent causes remain separate findings; several manifestations of one cause become one finding at the cause.
