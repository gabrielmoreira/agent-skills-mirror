---
title: Bounded delegation
applicability:
- When the requested outcome may need another agent to perform a coordinator-defined part of the work
- Before another agent instance is obtained or briefed to perform a coordinator-defined part of the work
---

Use another agent only when it preserves coverage that independently resumable units cannot, avoids outcome-relevant elapsed-time harm, or supplies genuinely independent attention. Mere divisibility or duplicating work you could do yourself is not a reason; independently resumable work needs a handoff, not delegation.

Before obtaining an instance, establish that the requester or standing instructions authorize it. If neither already grants it and the host does not forbid it, ask the requester. Finish the brief first. A reachable instance is not authorized, and an unbriefed worker starts before its boundary, authority, guidance, capability, and return contract exist.

Delegate only a slice that is all three:

- **Bounded:** it names what it covers and excludes in checkable terms.
- **Authorized:** the worker may read and change everything the slice needs, and knows what it may not do.
- **Disjoint:** no two live slices mutate the same material, and the coordinator does not touch a live unit's mutation surface or treat its partial state as settled. A unit stays live until its stop is observed.

Replication is different from shared mutation. Multiple observers may inspect one fixed surface only when the question genuinely varies by observer, all units are read-only, each judges independently without seeing the others' conclusions, and synthesis occurs once after every observer has returned or observably stopped.

## Briefing a unit

Write the brief for a worker with no access to your reasoning. It states the unit's surface, allowed material, authority, established facts it may rely on, claims it must test, return fields and useful bounds, evidence standard, done signal, next safe checkpoint, coordinator verification of relied-on claims, and the incomplete disposition when completion cannot be supported. A delegate must not reconstruct missing guidance from a transcript or unmentioned source.

Bound returns by what acceptance consumes, not arbitrary length. If deciding evidence will not fit, cite where the coordinator can inspect it and return the supported conclusion; if evidence cannot be made inspectable, return the named incomplete disposition.

Before obtaining the instance, establish which instruction sources the host will make effective and which the delegate can read. How the unit receives its guidance depends on what its work needs:

- **Whole source:** a unit that is itself a request an instruction source routes to one of its workflows and tracks to that workflow's finished state, and whose stages, decisions, and progress must outlast what the delegate can hold in mind, needs that routing and tracking, which selected provisions would strip. Route the unit's request through that source yourself, read the workflow it reaches, and reconcile that workflow and the capabilities it requires with the brief; if they cannot govern the unit together, select provisions or redesign the slice. Naming the source authorizes the delegate to follow its routing and reading rules for the unit's request, including provisions they bring in only as the work proceeds, and grants none of the source's reach, authority, effects, or delegation beyond the brief.
- **Selected provisions:** any other unit would pay for routing and records its work never consumes. The coordinator selects the governing provisions and puts them in the brief, naming a source only when that whole source governs. What a named source requires to be read with it is part of it: name each such requirement that applies to the unit, or select its provisions instead.

Either way, name each source by the exact content the coordinator relied on, fixed or verified unchanged. State that the brief and named sources are the unit's complete guidance, that it opens no other instruction source, and that it starts no unit of its own. Include unavoidable host guidance only if the coordinator can inspect and reconcile it; otherwise the required delegation contract cannot be formed.

If the brief would need guidance this run has not established, exceed what the delegate can hold, or fail to create a bounded authorized arrangement, redesign the slice into the least demanding arrangement that preserves the needed independence. If none works, keep the work with the coordinator only if it can still close there; otherwise mark the missing delegated evidence uncovered.

Classify supplied statements as governing requirements, established claims with provenance, or hypotheses to test; anything else is context. Settled decisions are governing requirements, and choosing between instructions that conflict is a decision too; name the decisions left to the delegate, so that one it meets outside them comes back in the return instead of being made. Instruct the delegate to return contrary authorized evidence rather than force observations to fit.

Choose capability from host-established evidence that it meets the unit's evidence standard and defect risk, within requester/host resource constraints. Do not infer relative cost, strength, or need to match the coordinator without evidence. Where a claim depends on configuration, establish what actually ran from host evidence, not the delegate's self-report.

Do not delegate the judgment that decides the overall outcome. Gathering, checking, and enumerating can divide; synthesis remains with the coordinator.
