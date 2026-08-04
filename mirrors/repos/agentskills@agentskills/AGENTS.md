# Agent Instructions

## Project perspective

Agent Skills is a small, portable, client-neutral format. Keep the format small:
new requirements impose costs on every implementation and should address
demonstrated interoperability needs, not hypothetical completeness.

Use progressive disclosure in this repository too. Keep details in their natural
source instead of repeating commands, configuration, or policy here.

## Authority and boundaries

`docs/specification.mdx` is authoritative for format requirements.
Explanatory documentation, examples, tests, and implementations do not add
requirements to the format. Preserve the distinction between the format and
choices made by skill authors, clients, models, or implementations.

When these surfaces disagree, surface the discrepancy and resolve it at the
appropriate authority rather than treating existing implementation behavior as
normative.

Do not treat `skills-ref/` as a general contribution surface. It is a
demonstration artifact, not a production SDK or a source of additional format
requirements. Modify it only when the task explicitly scopes work there;
specification or documentation changes do not by themselves put it in scope.

## Documentation

The documentation under `docs/` is a Mintlify site. Treat rendered behavior and
published routes—not source text alone—as part of documentation correctness.

When adding client logos, consider their perceived size in both the logo
carousel and client showcase. Square or visually dense logos can appear
disproportionately dominant, while wide or sparse logos can appear too small;
use the existing `scale` examples in `docs/snippets/clients.jsx` as context and
exercise visual judgment.

## Contributions

`CONTRIBUTING.md` owns current contribution scope, routing, and AI-assistance
disclosure policy. Read and follow it before beginning work intended for
upstream submission or participating in an issue, Discussion, or pull request.
