---
title: Skill version selection
applicability:
- When the work depends on a skill's version
---

For a new source, take the initial version from the requester, standing instructions, or a versioning convention one of them names. If none exists and the effective initializer supplied a value, it may remain as an explicit authoring default; that establishes only the literal value, not release semantics. If no acceptable default exists and a final version is required to close the requested artifact, ask the authority over the skill for the value or convention after completing independent work.

A source edit does not create a versioning requirement, and general authority to revise bundle content does not authorize changing the version field. Preserve the exact existing version unless the requester, standing instructions, or an established packaging/release requirement makes version work part of the task.

When a version change is required, take the relationship between versions from the project's established convention. Do not infer Semantic Versioning, calendar versioning, compatibility promises, or increment meaning from the shape of the current string, the size of the diff, or what another project does. If the governing convention is absent, the exact new version or convention is a project decision for its authority rather than an authoring default.

Selecting a version and applying it are separate effects. A request that only reviews or packages source unchanged may establish or report the version but does not authorize editing it. If an authoritative required version differs from the source, report the mismatch and leave packaging blocked until the change is authorized. Apply an authorized version change before final compiler evidence so the closed source and anything packaged from it carry the same identity.
