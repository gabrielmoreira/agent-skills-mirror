---
title: Evidence behind a software finding
applicability:
- Before a candidate defect, risk, or improvement is reported or acted on
---

A capable agent reports a lead as a finding, a preference as a defect, and one cause as several findings; each costs the reader a decision the evidence does not support. A candidate becomes a finding only with four linked parts:

1. A concrete input, state, configuration, or sequence and a reachable caller or entry point that can supply it.
2. A traced path to the smallest location where behavior departs from an established contract.
3. The expected and actual result, with the contract that supplies the expectation.
4. The guards, caller preconditions, configuration, version behavior, tests, and alternate paths searched for that would refute the candidate.

The impact is what a user, operator, or downstream system experiences.

For a finding whose subject is documentation, test quality, configuration, or another surface judged by what its reader or consumer can rely on rather than by execution, the same four parts hold with that reader or consumer in place of the caller: the reader task or consuming contract that reaches the passage or check, the passage or check where it departs from what the evidence supports, the expected and observed effect on that reader or consumer, and the evidence searched for that would refute it.

A warning, failed job, log line, suspicious name, or familiar defect class is a lead until the mechanism is traced. Report a lead that could still matter as an unverified risk beside the check that would settle it, never as a finding. A departure from ecosystem custom, an unadopted tool, or a missing dependency is a defect only with project evidence that the resulting behavior or cost matters here. A clarity or maintainability issue is a defect only when a concrete future change would be misled, and that change is named with it; unfamiliar style, a different abstraction, missing comments, and a locally surprising mechanism are not defects by themselves.

Independent causes remain separate findings; several manifestations of one cause become one finding at the cause.
