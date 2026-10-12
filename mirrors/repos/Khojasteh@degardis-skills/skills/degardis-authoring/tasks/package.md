---
title: Build or package a Degardis source
cues:
- the requester asks for a bundle built from a Degardis source
goal: Build the exact supplied source into the requested bundle form, leaving the source and other host locations unchanged and reporting the artifact identity and every unsupported part of the requested package.
knowledge:
- working-accounts
- evidence-bounds
- child-skill-and-agent
- compiler-evidence
- compiler-integrity
guides:
- effective-compiler
- version-selection
---

Confirm that the final compiler evidence was taken from the exact bytes being packaged before building. Where the requester made an earlier stage a gate to packaging and it did not pass, leave the artifact unbuilt and report the gate.

Before a build, establish its output directory, what already occupies that destination, which artifact the build would replace, and which output forms the effective compiler currently supports.

**Screen everything the bundle will carry.** Establish the complete input inventory from the effective manual and account for every derived file with the compiler's output report. Inspect every non-derived input in that inventory that bears on execution or disclosure. Judge disclosure under [[principle:sensitive-material]]; when material it excludes cannot be left out of the inventory, stop the build rather than expect the compiler to drop it.

After the build, take the identity of the bytes now at the destination as [[guide:artifact-identity]] defines it. The artifact at its output and that identity are this task's boundary: copying the bundle elsewhere, installing or replacing it in an agent, and publishing or releasing it are outside this skill's outcome, and this task performs none of them.
