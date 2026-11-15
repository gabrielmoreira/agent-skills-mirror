---
title: Component architecture
applicability:
- When a judgment of existing software depends on how responsibilities, dependencies, and boundaries are arranged across its components
x-claim-provenance:
- claim: High-level box-and-arrow models of an existing system are almost always inaccurate with respect to its source, so they are checked against a source model extracted from the code.
  source: https://cs.ubc.ca/~murphy/papers/rm/fse95.html
- claim: Static analysis tools that ignore reflection or handle it only partially miss behavior and produce unsound results.
  source: https://arxiv.org/abs/1706.04567
- claim: Architectural erosion is caused by violations of the architecture and drift by insensitivity to it, and both make a system increasingly resistant to change.
  source: https://webhome.csc.uvic.ca/~hausi/480/papers/perry.pdf
- claim: Architecture rules such as layer dependencies and freedom from cycles can be expressed and enforced as automated tests.
  source: https://www.archunit.org/userguide/html/000_Index.html
- claim: A dependency cycle between packages forces them to be released together, so that they in effect become one large package.
  source: http://www.objectmentor.com/resources/articles/granularity.pdf
- claim: Classes in a package should be closed together against the same kinds of changes, and the granule of reuse is the granule of release.
  source: http://www.objectmentor.com/resources/articles/granularity.pdf
- claim: Dependencies between packages should run in the direction of stability, each package depending only on packages more stable than itself.
  source: http://www.objectmentor.com/resources/articles/stability.pdf
- claim: Programs that change together across module or subsystem boundaries in the release history reveal logical coupling not evident in the source code, and indicate that the decomposition should be reconsidered.
  source: https://plg.uwaterloo.ca/~migod/846/papers/gall-coupling.pdf
- claim: Failure or resource exhaustion in one part of a system cascades to other consumers unless its elements are isolated into separate pools.
  source: https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead
- claim: Services that share a database are coupled at development time through schema changes and at run time through interference such as lock contention.
  source: https://microservices.io/patterns/data/shared-database.html
- claim: Architecture evaluation requires a statement of quality attribute requirements, and scenarios make vague qualities such as modifiability concrete enough to evaluate.
  source: https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf
  scope: CMU/SEI-2000-TR-004, August 2000
- claim: In Fowler's experience a one-step replacement of a serious system usually fails, and gradual modernization grown around the legacy system reduces risk.
  source: https://martinfowler.com/bliki/StranglerFigApplication.html
  scope: Article dated 22 August 2024
---

Recover the part of the architecture the judgment spans before judging it. Its components are the units the project builds, deploys, or declares as owners, such as packages, modules, services, and processes; directory names and diagrams are candidates until manifests, build and deployment declarations, or entry points confirm them. Take the dependencies between components from what binds them: build and package declarations, imports, runtime calls, messages and events, shared storage, and the mechanisms that bind without a textual reference, such as configuration, injection, reflection, and convention. Record in re-readable working state, for each component, the facts it owns, the data it writes, and the process, deployment, trust, and failure boundaries it sits behind. Component internals may be sampled, but a claim about the arrangement, such as that no cycle exists or that only one component writes a store, holds only over the components and binding mechanisms actually inspected.

Judge it against the architecture the project adopted, not against a style. Adopted rules come from the requester, accepted architecture decisions not yet superseded, maintained architecture documentation, and rules the build or tests enforce, such as module visibility, dependency constraints, or architecture tests. A named style such as layered, hexagonal, or microservices is the project's rule only where that evidence adopts it. The rule is then the dependency or ownership constraints the adopting evidence states or, where it names the style without stating them, the defining constraints of the style's originating description; the folder layouts, layer counts, and naming conventions that commonly accompany a style are not part of the rule unless that evidence adopts them too. State the constraints the judgment applies, and keep what neither source settles as an open question rather than a criterion. Where the code departs from an adopted rule, it fails that rule, which settles a question of conformance; whether the departure is a defect worth acting on is the cost question below, and which side is wrong is settled as [[principle:software-evidence]] settles any disagreement between sources: the code being newer, or the document being formal, decides nothing. Where the project adopted no rule, judge only by the costs below.

Then ask where a real change or behavior path pays for the arrangement. These questions locate candidates; they are not requirements, and the set is not exhaustive:

- **Ownership:** does each policy, fact, and state transition have one owning component, or do several components enforce, store, or mutate it, so that each change must reach all of them and they can disagree?
- **Dependency direction:** do dependencies run the way the adopted rules or the components' relative stability require, or do cycles, back-channels, or a stable component depending on a volatile one force components to build, release, or change together?
- **Change amplification:** how many components does a typical change touch? History that repeatedly edits the same set of components together signals that their boundary may split one concern.
- **Boundary placement:** do process, deployment, data, trust, and failure boundaries sit where the behavior needs them, or does a failure, slow call, or shared store in one component reach others that should be isolated from it?
- **Granularity:** do the components match how the parts vary and are released, or is one concern spread across components that always change and deploy together, or unrelated concerns held in one that blocks independent change?

A candidate becomes a finding under [[principle:finding-evidence]] in its cost terms: name the change, measured workload, or failure scenario that meets the arrangement, and what it pays here against what it would pay without it. Take that change from history, requirements, or the project's stated plans, never from hypothetical growth, and let a quality such as scalability or availability enter only where a stated requirement or scenario, a target, a recorded incident, or a measurement establishes it.

Recommend the smallest structural move that removes an established cost, such as moving a responsibility to the component that owns its knowledge, breaking one cycle, or giving a fact one writer. Propose replacing the architecture or adopting a style only when evidence shows that smaller moves cannot remove the cost, and then state what the migration must preserve.
