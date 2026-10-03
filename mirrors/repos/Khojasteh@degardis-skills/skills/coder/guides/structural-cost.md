---
title: Structural cost
applicability:
- When a decision depends on the cost a code structure imposes
---

Name the structural defect and the cost it imposes on a reader, the next change, or execution. A style preference with no demonstrated cost is not a restructuring outcome.

Establish structural cost from what a real change must do: how many independently located edits it requires, how much unstated knowledge a maintainer must carry, and which behavior path the readable code obscures. Weigh that cost by how often the affected surface changes; stable code can carry a real cost that is still lower priority. Similar syntax is not necessarily duplicated knowledge, and direct code is not necessarily a unit with unrelated responsibilities.

Use code-smell names as diagnostic signals, not compliance targets or findings. Feature envy, repeated policy, scattered mutation or control flow, misleading names, interleaved phases, tiny fragments, pass-through layers, deep indirection, excessive injection, and unrelated responsibilities accumulating in one owner are common, non-exhaustive signals. Retain one only after tracing it to a concrete comprehension, navigation, change-coupling, testability, compatibility, or execution cost; the absence of a familiar smell name does not refute a demonstrated cost.

Treat duplication as shared knowledge only when the sections express the same rule, invariant, or decision and should evolve together. If the concepts may diverge independently, retain the duplication rather than force them through flags or conditionals. Put genuinely shared knowledge at its narrowest stable owner.
