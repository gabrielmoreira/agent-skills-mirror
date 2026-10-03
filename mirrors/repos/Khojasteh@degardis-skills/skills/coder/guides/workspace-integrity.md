---
title: Workspace integrity
applicability:
- Before the first action that can alter workspace state
---

Observe the starting state of every path the work may change. Identify unrelated modifications and do not overwrite, revert, stage, commit, format, or regenerate them. Where version control is unavailable, retain another checkable baseline for touched material.

Use existing project mechanisms for generated files and dependencies. Isolate a diagnostic reconstruction or temporary probe from maintained source where practical, and establish what prior state it represents. Remove temporary files, focused-run markers, debug output, caches created only for the run, and other unrequested residue after their evidence is consumed.

Inspect the complete final changed surface against the baseline. Every remaining movement must belong to the requested outcome, its necessary verification, or correction of a defect this work introduced. If cleanup would destroy unrelated or still-needed state, stop and report the exact residue.
