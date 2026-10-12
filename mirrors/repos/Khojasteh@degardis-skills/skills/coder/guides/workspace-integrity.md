---
title: Workspace integrity
applicability:
- Before the first action that can alter workspace state
---

Observe the starting state of every path the work may change. Identify unrelated modifications and do not overwrite, revert, stage, commit, format, or regenerate them. Where version control is unavailable, retain another checkable baseline for touched material.

Use existing project mechanisms for generated files and dependencies. Remove what the run created only to obtain evidence, such as temporary files, probes, focused-run markers, debug output, and caches, once that evidence is consumed, along with any other unrequested residue.

Inspect the complete final changed surface against the baseline. Every remaining movement must belong to the requested outcome, its necessary verification, or correction of a defect this work introduced. If cleanup would destroy unrelated or still-needed state, stop and report the exact residue.
