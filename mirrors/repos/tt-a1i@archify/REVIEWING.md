# Reviewing Archify changes

Use this guide for initial and revised PR reviews. Judge the user value, implementation and ongoing maintenance cost, and impact on existing behavior. [Contributing](CONTRIBUTING.md#choose-evidence-by-impact) describes contribution and evidence requirements.

## Check readiness before detailed review

Apply [Choose the right path](CONTRIBUTING.md#choose-the-right-path) first. When prior scope agreement is required but missing, thank the contributor, point to the relevant issue or proposal form, and close or defer the PR without detailed code review until the direction is agreed. Purely mechanical documentation corrections may proceed directly.

Check the [AI disclosure and accountability requirements](CONTRIBUTING.md#ai-assistance-and-contributor-responsibility). Disclosure is context for review, not a quality score. Ask about specific unexplained decisions or unsupported claims; never infer a violation solely from writing style.

For missing evidence, describe the material gaps together and request the smallest comparison that resolves them. Resume review when the contributor supplies it; reuse valid existing evidence. Maintainers review and sample the submitted evidence rather than routinely reconstructing every contribution's test run. An issue link alone does not establish scope agreement or review readiness.

For existing PRs, reuse earlier maintainer decisions and evidence; request discussion only for unresolved direction, rather than requiring a new issue as paperwork.

## Understand the problem and approach

Record the current target base and candidate head. Read the linked issue or agreed scope and check the current-base behavior where feasible. Separate the reported problem from the proposed implementation.

Identify who benefits and whether the approach is worth maintaining. Consider whether existing capabilities or a smaller change would solve the problem. For a new default, schema field, or acceptance policy, clarify the value and compatibility tradeoff early. Reuse decisions already made in the issue or authorized task.

If required scope agreement is missing, use the readiness procedure above before investing in implementation review. Reuse existing agreements rather than creating another planning exercise.

## Match investigation to impact

Check the author's [impact classification](CONTRIBUTING.md#choose-evidence-by-impact) against the changed paths and callers. Shared helpers, templates, and authoring instructions may affect more modes than the title suggests.

Choose checks that resolve the important uncertainties, including relevant historical failures and authored constraints. Broaden the investigation when findings or coverage gaps warrant it. Repository-only policy changes need consistency checks, not layout screenshots.

Use existing tests, receipts, and browser tools. For behavior comparisons, use fixed inputs on the recorded base and candidate:

- Account for changed and preserved topology, meaningful labels, explicit geometry, and relevant failure behavior.
- For affected visible behavior, inspect the intended differences and unexplained changes under comparable browser conditions. A pixel difference identifies a change; it does not judge its quality.
- When a fix also changes a validator or golden baseline, evaluate that acceptance change explicitly. Fresh generated output proves consistency with the candidate, not compatibility with the base.
- Separate locally reproduced results, author/CI evidence, reused evidence, and unknowns. Keep browser checks and perceptual review distinct.

Evidence should be sufficient for the affected contract. Avoid rebuilding an unchanged artifact or replaying unaffected checks merely to restate existing results.

For generation-comparison pilot PRs, use the [real repository benchmark review procedure](benchmarks/real-repo-generation/README.md#6-submit-and-review-one-report): inspect the paired outcomes and sample the source/session evidence before requesting reruns. A missing real-world benefit is an unverified claim; synthetic repair success does not establish it.

## Give actionable feedback

Lead with whether the approach is worthwhile, then explain findings and a clear disposition:

- **Blocking defect:** trigger, impact, supporting evidence, and the behavior that must be corrected.
- **Required evidence or scope decision:** the unresolved claim, why it matters to acceptance, and the smallest check or decision that would settle it. An unverified risk is not a reproduced defect.
- **Suggestion:** a worthwhile improvement outside the acceptance conditions; personal preference alone does not block.
- **Ready:** the agreed behavior is delivered, relevant evidence is sufficient, and no acceptance blocker remains.

Consolidate scope and compatibility concerns in the first substantive review where possible. Explain any later blocker with newly found evidence, an overlooked acceptance requirement, or a new diff. Record unrelated issues separately instead of growing the PR's scope.

Assess bot findings against the current diff and existing evidence before forwarding them. Explain duplicate or inapplicable findings; use the same standard of evidence as for your own feedback.

## Re-review and finish

Compare against the last reviewed head, resolve outstanding findings, and inspect added changes. Check intervening base changes for effects on the earlier assessment. Expand review when those changes invalidate scope or evidence; do not treat an old pass as proof of new behavior.

Finish when the agreed outcome is delivered, relevant evidence is sufficient, and no acceptance blockers remain. Report non-blocking limitations. A review conclusion does not itself authorize a GitHub approval or merge; follow the authorized action and [final integration requirements](CONTRIBUTING.md#final-integration-and-follow-up).
