---
name: implementation-strategy
description: Decide how to implement or review runtime and API changes in openai-agents-python. Use when a task changes or reviews exported APIs, runtime behavior, serialized state, tests, or docs and you need to choose the compatibility boundary, the smallest coherent implementation, whether shims or migrations are warranted, and when unreleased interfaces can be rewritten directly.
---

# Implementation Strategy

## Overview

Use this skill before editing or reviewing code when the task changes runtime behavior, an externally visible interface, or data that must remain usable across releases, processes, or machines. The goal is to keep implementations and review requests focused while protecting behavior and data formats the project has committed to support.

## Quick start

1. Identify the surface you are changing or reviewing: released public API, unreleased branch-local API, internal helper, persisted schema, wire protocol, CLI/config/env surface, or docs/examples only.
2. Determine the latest release tag to use as the compatibility baseline from `origin` first, and only fall back to local tags when remote tags are unavailable:
   ```bash
   BASE_TAG="$(.agents/skills/final-release-review/scripts/find_latest_release_tag.sh origin 'v*' 2>/dev/null || git tag -l 'v*' --sort=-v:refname | head -n1)"
   echo "$BASE_TAG"
   ```
3. Write an implementation scope contract before coding: the required behavior, compatibility requirements, intentionally unsupported cases and their failure behavior, and an already-supported alternative for those cases or that none exists.
4. Identify the nearest existing implementation pipeline and the functions, types, or modules that are the source of truth for each affected concern. Prefer adapting the required input into that pipeline over creating parallel schema, metadata, validation, naming, or execution machinery.
5. Judge breaking-change risk against the latest release tag, not against unreleased branch churn or post-tag changes already on `main`. If the command fell back to local tags, treat the result as potentially stale and say so.
6. Apply the scope and simplicity rules below, including the complexity reset triggers, before choosing the implementation or review recommendation.
7. Add a compatibility layer only when the old interface or behavior shipped in the latest release and must remain usable, an explicitly supported durable data format requires it, or the user explicitly asks for a migration path.

## Scope and simplicity rules

- Make the smallest coherent change that fully satisfies the current task and preserves the behavior identified in the compatibility requirements.
- Prefer existing patterns and direct implementations. Add a new abstraction, general-purpose helper, configuration knob, dependency, compatibility layer, feature flag, or parallel code path only when a concrete current requirement or supported contract needs it.
- Do not equate accepting a broad Python or third-party protocol type with supporting every representable implementation shape. State exactly which call shapes and behaviors are supported.
- Prefer adapting the required case into the existing source-of-truth path. Do not create a second resolver or contract for schema, documentation, validation, identity, or invocation when the existing path can consume a normalized adapter.
- Require every new piece of state, classification, branching, or metadata to have one source of truth and to satisfy one stated requirement. A cache of inferred facts that can disagree with the runtime object is a strong signal to simplify.
- Trace only the code paths being changed and the contracts they rely on. Expand the investigation or implementation only when concrete evidence or validation exposes another required path.
- Keep root-cause fixes within the requested boundary. Leave unrelated refactors, cleanup, feature work, and pre-existing failures out of the patch; report them separately when they materially affect the result.
- Add focused tests for the required behavior, behavior matching the nearest existing path, and one representative case for each intentionally unsupported category. Do not turn a matrix of language-feature permutations into a product contract merely because those permutations can be constructed.

## Implementation scope contract

An implementation scope contract is a short, updateable engineering decision record, not a new public API promise. Record these four items in the plan or working notes before implementation, and update them before widening or narrowing the implementation:

1. **Required behavior:** The smallest user-visible scenario that must work.
2. **Compatibility requirements:** Behavior from the latest release or an explicitly supported durable boundary that must remain unchanged, plus any user-approved migration or deprecation requirement for behavior that will change.
3. **Intentionally unsupported cases:** Specific nearby inputs or call shapes the implementation will reject instead of inferring or emulating, including where and how rejection occurs.
4. **Supported alternative:** An already-supported wrapper, explicit override, adapter, configuration, or lower-level API users can choose for an intentionally unsupported case. State `none` when no such alternative exists.

If the intentionally unsupported cases cannot be stated clearly, do not start by adding a general resolver. First define a narrower behavior contract. If no adequate supported alternative exists, add one only when the task requires it; do not invent one speculatively.

## Complexity reset triggers

Stop extending the current implementation, discard assumptions introduced by the current patch, and redesign from the original requirement when any of these signals appears:

- Review fixes repeatedly add cases formed by combining the same independent dimensions, such as wrappers, descriptors, generic specialization, binding modes, context injection, sync/async classification, or provider variants.
- The patch begins to interpret a host language or third-party reflection protocol rather than implement the requested SDK behavior.
- Schema generation, documentation, validation, naming, and invocation depend on separately inferred representations that can drift apart.
- A narrow feature requires new state objects, cached modes, recursive resolution, or changes across otherwise unrelated subsystems.
- Most new tests enumerate permutations of implementation mechanics rather than the promised user-facing contract.
- The implementation keeps growing after each review cycle while the original required scenario remains small.

When a trigger fires:

1. Stop addressing comments one by one.
2. Group all findings by root cause and identify the unsupported dimensions they expose.
3. Re-read the original request and list the behavior from the latest release that must remain compatible.
4. Compare the complete diff with the merge base of the intended target branch, or with the latest release tag when it is the compatibility baseline, not only with the previous review revision.
5. Delete or directly replace branch-local machinery that is not required. Unreleased code and its tests are not sunk costs.
6. Narrow the supported contract and reject intentionally unsupported cases before side effects occur. Point to an already-supported alternative when one exists.
7. Rebuild the regression suite around the required behavior, behavior matching the nearest existing implementation path, and one representative test for each intentionally unsupported category instead of every possible composition.

Do not wait for the user or reviewer to request this reset when the signals are already present.

## Compatibility boundary rules

- Released public API or documented external behavior: preserve compatibility or provide an explicit migration path.
- Persisted schema, serialized state, wire protocol, CLI flags, environment variables, and externally consumed config: treat as compatibility-sensitive when they are part of the latest release or when the repo explicitly intends to preserve them across commits, processes, or machines.
- Python-specific durable surfaces such as `RunState`, session persistence, exported dataclass constructor order, and documented model/provider configuration should be treated as compatibility-sensitive when they were part of the latest release tag or are explicitly supported as a shared durability boundary.
- Interface changes introduced only on the current branch: not a compatibility target. Rewrite them directly.
- Interface changes present on `main` but added after the latest release tag: not a semver breaking change by themselves. Rewrite them directly unless they already define a released or explicitly supported durable external state boundary.
- Internal helpers, private types, same-branch tests, fixtures, and examples: update them directly instead of adding adapters.
- Unreleased persisted schema versions on `main` may be renumbered or squashed before release when intermediate snapshots are intentionally unsupported. When you do that, update the support set and tests together so the boundary is explicit.

## Default implementation stance

- Prefer deletion or direct replacement over aliases, overloads, shims, feature flags, and dual-write logic when the old shape is unreleased.
- Prefer clearly listed unsupported cases over a partial generalization. An actionable error plus an existing wrapper or override is often safer than incomplete protocol emulation.
- Treat a branch-local implementation as disposable. Test coverage proves behavior; it does not make the current architecture worth preserving.
- If review feedback claims a change is breaking, verify it against the latest release tag and actual external impact before accepting the feedback.
- If a change alters behavior or a data format shipped in the latest release, call that out explicitly in the ExecPlan, release notes context, and user-facing summary.

## Applying this skill during review

- Establish the requested outcome and compatibility boundary before judging whether the implementation is too narrow or too broad.
- Treat complexity as an actionable finding only when specific added machinery is not needed by the current task, a released contract, supported durable state, or a verified runtime or platform risk. Name that machinery and recommend the smallest safe removal or replacement.
- Do not request abstractions, configuration, dependencies, compatibility work, or extensibility for hypothetical future consumers.
- Classify related comments together before implementing them. If each comment finds a new combination of the same dimensions, treat the abstraction itself as the finding.
- Ask whether each disputed case belongs to the implementation scope contract. A reproducible edge case is not automatically a required supported case.
- Evaluate convergence: a good fix reduces ambiguity and the number of behavior combinations the implementation must infer; a fix that adds inferred combinations without a stated requirement is moving in the wrong direction.
- Review the complete branch diff from the merge base of the intended target branch, or from the latest release tag when it is the compatibility baseline. Do not let small incremental fixes hide a large accumulated design.
- Keep unrelated cleanup and pre-existing problems out of blocking findings. Report them separately only when they are useful to the maintainer.
- Require a broader refactor only when concrete evidence shows that the focused change would otherwise be incorrect, unsafe, incompatible, or materially harder to maintain.

## Pre-handoff effectiveness check

Before declaring the design complete, answer all of these with concrete evidence:

- Can the required behavior be described without naming internal helper types or reflection mechanics?
- Does the implementation reuse the nearest existing pipeline rather than maintain a parallel interpretation?
- Can every new abstraction, state field, and branch be mapped to the implementation scope contract or a verified compatibility or security requirement?
- Is each intentionally unsupported neighboring case rejected before side effects occur, with an already-supported alternative identified when one exists?
- Do tests cover the required behavior, behavior matching the nearest released implementation path, and one representative case per intentionally unsupported category without making every constructible permutation supported?
- After reviewing the complete diff from the merge base of the intended target branch, would removing any new machinery leave the required behavior intact? If yes, remove it.
- If the latest review comments were applied as a batch, does the new design shrink the future review surface rather than create more combinations?

If any answer is no, continue the strategy review before adding more implementation.

## SDK-specific decision rules

- When unsupported OpenAI API or provider-adapter behavior already has a released default path, avoid turning it into a default hard error unless the latest release boundary justifies that break. Prefer an opt-in strict mode such as `strict_feature_validation=True`, while keeping the default path compatible through warning, ignoring unsupported data, or a clearly non-empty placeholder.
- For OpenAI API feature gaps, evaluate streaming and non-streaming paths together. Custom tool calls, multi-choice Chat Completions chunks, non-text tool outputs, and similar provider payload differences must not be strict in one path and permissive or malformed in the other.
- When a change creates new public SDK behavior, do not expose it only through hard-coded module globals. Prefer an explicit public configuration object or parameter, preserve the existing default behavior when compatibility-sensitive, and make opt-in SDK defaults explicit.
- For SDK-owned public configuration, accept existing typed objects and equivalent dictionaries at the public input boundary while preserving the internal typed representation. Respect the owning model's validation and extra-field policy instead of recreating arbitrary third-party schema semantics.
- Keep model-specific settings inside the existing `model_settings` parameter. Preserve released constructor arguments, typed-object behavior, and provider request payloads when adding dictionary support.
- Append new optional fields or constructor parameters to public dataclasses and constructors. Do not insert them before existing public fields unless you also provide a compatibility layer and regression coverage for the old positional call shape.
- Treat threshold and quota values as part of the API design when they affect runtime behavior. Distinguish OpenAI platform quota-derived values from defensive SDK defaults; if the value is not anchored in a documented platform limit, avoid making it an unconditional default-on behavior.
- Define `None` semantics deliberately for public configuration. For example, use separate meanings for "feature disabled or no SDK limit", "use SDK default limits", and "disable only this specific limit" rather than relying on implicit truthiness checks.

## When to stop and confirm

- The change would alter behavior shipped in the latest release tag.
- The change would modify durable external data, protocol formats, or serialized state.
- The correct solution would materially expand beyond the requested outcome or require unrelated architectural work.
- A complexity reset trigger fires and the narrower replacement would change an already released contract rather than branch-local code.
- The user explicitly asked for backward compatibility, deprecation, or migration support.

## Output expectations

When this skill materially affects the implementation approach, state the decision briefly in your reasoning or handoff, for example:

- `Compatibility boundary: latest release tag v0.x.y; branch-local interface rewrite, no shim needed.`
- `Compatibility boundary: released RunState schema; preserve compatibility and add migration coverage.`
- `Scope decision: direct change using existing patterns; no new abstraction or adjacent cleanup needed.`
- `Implementation scope contract: support X; preserve Y; reject Z before side effects; use supported alternative W, or none exists.`
- `Complexity reset: repeated edge-case combinations show the approach is too broad; redesign from the original requirement instead of adding another branch.`
- `Review decision: the added compatibility path has no released or supported consumer; replace it with the direct implementation.`
