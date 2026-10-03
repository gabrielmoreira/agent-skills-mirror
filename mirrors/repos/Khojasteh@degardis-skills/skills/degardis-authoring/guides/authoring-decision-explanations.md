---
title: Authoring decision explanations
applicability:
- Before explaining why a skill instruction or construct arrangement is chosen
---

Explain the decision the reader asked about: the failure prevented, the similar-looking cases needing different actions, the evidence that distinguishes them, and the resulting action and completion state. Facts can be stated directly; a choice, precaution, threshold, or order needs that model so an unfamiliar case can be decided. Use the guidance below as the reasoning to explain, not as a request to perform source work.

## Claims and judgments

Distinguish intended behavior from established fact: descriptions, goals, cues, and selected behaviors declare intention. A field claim is any proposition about the subject or execution environment that must hold for an instruction to work, including a default or fallback expressed as an imperative. Explain who can establish it, or how an agent obtains a runtime input before dependent action; authorized narrowing can remove the dependent behavior, while a required unsettled premise blocks it. [[guide:domain-evidence]] and [[guide:claim-provenance]] supply the applicable authority, freshness, and retained-evidence reasoning.

Explain a contribution's basis according to its role: facts need competent evidence, requirements need authority over the action, protection needs a hazard and safer action with applicability and override evidence, and other guidance needs a situation, action, benefit, and evidence favoring it. A partly supported point stays unresolved; a point with no basis, consumer, or distinct decision is removed. [[guide:using-an-example]] governs worked examples. An example illustrates a rule, while a list that decides a class needs an authority fixing its members or a general rule for an in-scope unlisted case; otherwise the boundary must be narrowed under authority or reported as a gap.

Keep four judgments distinct: compiler integrity, obligation coverage and static rehearsal, meaning, and composition. A warning is a finding barring a compiler-integrity claim until resolved or explicitly accepted beside that claim, even after a successful exit; it does not itself bar reading or judging pages the compiler still composes. Explain the strict closing check separately from whether the child agent can derive the decisions.

Use whole rules to explain a defect: a gap lacks a supported, timely owner or executable branch; a contradiction requires compatible conditions and authority for two live instructions that cannot both be performed; ambiguity leaves action-changing readings undecided on the reader's path; an ownership defect lacks one suitable owner on every consuming path. A fallback excluding the primary action's trigger is compatible, and a candidate is ruled out only by the reading available on its generated path.

## Ownership and reach

A point is the smallest contribution whose removal changes a reader's decision or understanding. Explain ownership by the consumer's work: applications of one idea in different work can be distinct points, but two statements deciding the same case for the same reader are duplicate owners. A unit follows the work its reader comes to it for. Generalizing it must retain its decision logic or reach an authority supplying it; a slogan cannot replace derivable action. Use [[guide:construct-ownership]] for construct kinds, [[guide:obligation-ledger]] for required outcomes and their owners, [[guide:construct-agreements]] for interactions, and [[guide:path-rehearsal]] for what the generated path actually derives.

A skill's outcome is expressed in request language. Explain how its description supplies positive selection evidence shared by its tasks, how the host interface carries that outcome, and how the response accounts for unsupported parts. [[guide:skill-stance]] explains any stance after selection. A task goal names its entire finished state; its approach orders decisions specific to that outcome, keeps stages serving it together, and makes each branch's discriminator and result executable. Definitions precede dependent guidance in the compiler's actual composition order. Use [[guide:task-cues]] for routing, [[guide:handoff-conditions]] for work discovered after routing, and [[guide:facet-design]] for optional specialization.

[[guide:child-discipline-explanations]] supplies the reasoning for what working discipline the child skill must teach.

For a change, explain which evidence justifies its arrangement and how the previous decisions survive it: [[guide:behavioral-preservation]], [[guide:restructuring-on-evidence]], and [[guide:whole-construct-rewrite]]. [[guide:names-and-headings]], [[guide:wording-and-references]], and [[guide:guide-design]] supply presentation decisions, and [[guide:version-selection]] supplies version decisions.
