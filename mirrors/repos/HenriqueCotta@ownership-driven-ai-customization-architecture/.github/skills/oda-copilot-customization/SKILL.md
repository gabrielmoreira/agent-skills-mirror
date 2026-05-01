---
name: oda-copilot-customization
description: Apply, review, improve, or maintain a repository's Copilot customization with the Ownership-Driven AI Customization Architecture and the latest official GitHub Copilot docs. Use when shaping or auditing a repository's customization map, governance files, supporting docs, and safeguards for drift, health, weak controls, outdated assumptions, or when deciding how a specific customization problem should be handled.
---

# ODA Copilot Customization

Use this skill to keep a repository's Copilot customization healthy, current, and professionally reasoned.

The goal is not merely to remove the nearest inconsistency.
The goal is a healthy customization map that respects local repository rules, ODA, the latest official Copilot docs, and the repository's desired level of control without overengineering.

## Requested Outcome And Scope

Let the user's request define what this pass is for.

Requested outcomes:

- surface in-scope problems, drift, or worthwhile improvements
- think through a specific problem or decision before changing anything
- resolve the requested scope and any follow-through needed to keep the result coherent

Scope:

- keep the scope as narrow as the request honestly allows
- expand scope only when a real dependency, coupled issue, or verification need would make the narrower pass misleading, incomplete, or unsafe

Let the request shape the work:

- Stay in analysis when the user wants understanding, evaluation, or discussion.
- Make changes only within the requested scope and what directly depends on it.
- For broad requests, organize the work and the output in the clearest way for that request.

Treat each use of this skill as one pass.
Surface what remains directly instead of managing further passes inside the skill.

This skill must be resilient to change.
The platform, its documentation, its support boundaries, and the best implementation path can all change over time.
Do not overfit the review to the current wording of a page, the current product menu, or the current shape of the platform.
Use stable architectural principles to drive the review, then verify what the current platform can and cannot do in practice.

## Required Sources

1. ODA sources:
   - use the current upstream ODA repository directly as the authoritative source
   - repository: `https://github.com/HenriqueCotta/ownership-driven-ai-customization-architecture`
   - do not rely on local mirrors, archived copies, MVP snapshots, or deleted experiments as an authority for ODA
   - if the upstream ODA repository cannot be checked, treat the review as verification-blocked instead of pretending the architecture review is current
2. Official GitHub Copilot docs:
   - discover the currently relevant official docs and official change surfaces that may affect the healthiest design at review time
   - do not assume today's doc taxonomy, feature names, or mechanism list will remain stable
   - when behavior, availability, or implementation priority may have changed recently, also check the latest official product-update, release-note, changelog, or equivalent official change surface that clarifies the current behavior
   - do not treat one static docs page as sufficient proof of the current best implementation path if newer official material indicates the platform behavior changed
   - stop broadening the search once the remaining uncertainty would no longer change the decision
3. Local repository sources of truth, bridges, mirrors, and safeguards:
   - the current customization source of truth
   - any compatibility bridge
   - maintainer-facing mirrors of customization behavior
   - automated safeguards that validate or protect the customization map

## Current Verified Context

Use the current working context and already verified findings when they still cover the decision.

- Reuse previously verified live-source findings when they still cover the current scope.
- Re-check live sources only when a changeable external fact could alter the chosen path, when a new surface becomes relevant, when prior verification was insufficient, or when a fresh sweep is explicitly requested.
- Prefer targeted revalidation of the uncertain point over restarting broad source discovery.
- In long-running chats, do not treat earlier findings as invalid only because time passed; re-check when the decision depends on something that may have changed or when the prior verification no longer covers the current scope.

## Separate Durable Guidance From Live Variables

After checking the sources relevant to the current scope, the current verified context, and the current repository's goals:

- derive what should be treated as durable for this review
  - use this for the principles, boundaries, and decision logic that should continue guiding the architecture even if the platform changes
- derive what must be treated as live and revalidated
  - use this for anything whose current state could change the decision and therefore may need revalidation in the current pass

Do not assume either list in advance.
Derive both from the current sources you actually verified.

## How To Decide

Use this for each in-scope issue that still needs an active decision in the current pass.

Use only as much ceremony as the issue warrants.

1. Confirm there is a real problem worth changing now.
   - Keep the issue grounded in plain terms and current impact.
   - If the current state is still healthy enough, allow no change instead of forcing movement.
2. Gather only the facts that could change the decision.
   - Reuse verified findings from the current context when they still cover the decision.
   - Check authoritative sources and repository reality only for the uncertain or newly relevant point.
   - Stop once the remaining uncertainty would no longer change the available path.
3. Keep any unresolved uncertainty in play if it could still change the decision.
   - If key facts still cannot be verified well enough, narrow scope, defer structural change, or treat the review as verification-blocked instead of pretending certainty.
4. Put the decision where it belongs and update the parts that truly depend on it.
   - Include the source of truth and any mirrors, safeguards, or downstream surfaces that are part of that contract.
5. Decide whether this should stay one decision or be split first.
   - Split when bundling would hide trade-offs, mix unrelated risks, or force a worse compromise.
6. Compare only the few paths that could realistically be the best answer here.
   - Include keeping the current pattern when that is still the healthiest choice.
7. Choose the healthiest move whose scope is proportionate to the problem, even when it is not the smallest change.
   - Do not prefer a smaller change if it would preserve the wrong structure, leave material risk behind, or make the next correction harder.
8. Reassess before committing if the comparison exposes a different problem, missing fact, or wider blast radius than first understood.

Decision rules:

- Prefer the healthiest map over the first syntactically valid fix.
- Let durable architectural guidance and currently verified platform reality shape the decision together.
- Match the depth and scope of the response to the real size of the problem, without overengineering or dropping useful controls.
- When the issue is mixed or the real cost sits outside the local diff, decide for the full problem instead of the most convenient local explanation.
- Prefer no change when the current pattern remains the healthiest choice. Otherwise, prefer removal, redesign, or migration over preserving inertia.

## Workflow

1. Determine the requested outcome and scope from the user's request and the current context. Default to the least expansive interpretation that still honestly satisfies the request.
2. Reuse verified findings from the current context and check the upstream ODA sources, official Copilot material, and repository reality only where they could still change the decision. Re-open broad source discovery only when the scope changes materially, a new external surface becomes relevant, prior verification is insufficient, or a fresh sweep is requested.
3. Inspect the in-scope source of truth, bridges, mirrors, and safeguards that define or protect the customization behavior under review.
4. Produce findings first and organize them in the clearest way for the current review scope. Make materiality easy to understand, and in broad audits let the material issues lead without hiding smaller ones that cluster into drift, affect the current scope, are cheap to fix, or were explicitly requested.
5. For each in-scope issue that still needs an active decision, apply `How To Decide` at the depth the issue warrants.
6. Make changes only when they are part of the requested outcome and can actually be completed in the current context. When changing behavior, use the healthiest changes whose scope is proportionate to the problem, and update mirrors or safeguards only when they are part of the real contract.
7. Finish once the requested outcome and scope are satisfied for the current pass. If important issues remain unresolved after this pass, surface them directly instead of managing another pass inside the skill. If any of them are blocked, say what is blocking them.

## Common Failure Modes To Catch

Use this as a list of frequent pitfalls, not as a complete checklist.

- guidance tied to a boundary that does not map to one stable owner
- guidance placed more broadly than the boundary that truly owns it
- a customization layer carrying a kind of responsibility that belongs elsewhere
- stale references to older customization layouts, platform assumptions, or outdated checks
- controls, mirrors, or safeguards that no longer provide practical value for the current repository's goals
- missing controls, mirrors, or safeguards that would materially improve health or reliability without avoidable complexity

## Output

- Findings first, ordered in the way that best fits the current review scope
- Keep the write-up direct by default. Expand only when risk, uncertainty, or the user's request makes extra detail useful.
- Match the output to the requested outcome and scope instead of defaulting to a full audit narrative.
- For each in-scope issue that still mattered to the result: the chosen path and why it won
- Material uncertainty, blocked issues, or wider-impact considerations when they changed the result
- Applied fixes or recommended fix plan
- Whether any scoped issues remain unresolved after the review pass, and which of them are blocked if that matters
- Residual local choices, open questions, or repository-specific preferences when they still matter

## Guardrails

- Use the current upstream ODA repository as the architectural authority. Do not substitute local copies, stale mirrors, MVP repositories, or assumed old filenames for it.
- Treat the upstream ODA repository as defining architecture and decision rules, not local prose style.
- Use current official GitHub material for platform behavior and support details. Do not treat one static page or today's mechanism list as timeless when newer official evidence could change the decision.
- Do not create new customization structures or move responsibility into the wrong layer only because a change has downstream consequences.
- Do not silently turn analysis or discussion into implementation.
- Do not widen a scoped request into a broader cleanup or another pass without a real scope reason or an explicit user request.
- Do not stop at the first plausible fix when a healthier architecture alternative exists.
- Do not present repository-local trade-offs as ODA or Copilot requirements.
- Do not restart broad source discovery for every follow-up change in the same working context.
