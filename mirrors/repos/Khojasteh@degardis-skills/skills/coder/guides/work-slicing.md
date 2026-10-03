---
title: Work slicing
applicability:
- When the accepted outcome is larger than one independently verifiable unit of work or one bounded analysis pass
---

Partition by the fewest units that can reach a useful checkpoint on their own: a vertical behavior, a migration stage, a component boundary, or a named surface with its evidence. File counts, arbitrary time boxes, and architectural layers that defer all integration and behavioral evidence are not slices. A single-criterion change is one slice unless that criterion itself cannot be delivered safely in one step.

Each implementation slice states its outcome, authorized surface, prerequisites, input decisions, evidence, done signal, and the next slice that consumes it. Assign every acceptance criterion to exactly one slice; a slice is complete only when its assigned criteria hold, and no slice exists without a criterion that needs it. Keep intermediate states buildable and safe when practical. Take each unit through the work's stages at the depth its outcome needs; stop a unit whose required decision, authority, or evidence is missing while completing the independent authorized units, and recheck later units when an earlier one changes an input they consumed. Run the narrowest check sensitive to a slice before later changes compound it, then reserve a broader check for integration risk across the combined work. Preserve one owner for integration and any cross-slice contract. Put a shared declaration or compatibility bridge in the earliest slice that needs it and keep it valid until its named retirement condition.

For an analysis surface too large for one pass, order the partitioned parts by blast radius: trust boundaries, persisted state and migrations, published contracts, and shared foundations precede leaf code whose failure stays local. Delegation is a separate decision governed by its principles; slicing alone does not justify another agent.
