---
title: Document types
applicability:
- When a document's type, or what that type owes its reader, is being chosen or judged
x-claim-provenance:
- claim: A README tells people what the project does, why it is useful, how to get started, where to get help, and who maintains and contributes to it; longer documentation belongs elsewhere.
  source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
  scope: retrieved 2026-10-05
- claim: A README carries install, usage, contributing, and license sections, and a reader slightly familiar with the project should refresh their memory without paging down.
  source: https://github.com/RichardLitt/standard-readme/blob/main/spec.md
  scope: retrieved 2026-10-05
- claim: Contributing guidelines explain how to file a bug report, suggest a feature, set up the environment and run tests, and state the contributions wanted and how to get in touch.
  source: https://opensource.guide/starting-a-project/
  scope: retrieved 2026-10-05
- claim: Contributing guidelines give steps for good issues and pull requests, links to further material, and community and behavioral expectations.
  source: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
  scope: retrieved 2026-10-05
- claim: A tutorial is a learning-oriented lesson with a goal shown up front, concrete steps, and visible results early and often, without explanation or choices, and must work reliably.
  source: https://diataxis.fr/tutorials/
  scope: retrieved 2026-10-05
- claim: A how-to guide serves a competent user with a goal through a titled sequence of actions, including conditional steps, without teaching or exhaustive coverage.
  source: https://diataxis.fr/how-to-guides/
  scope: retrieved 2026-10-05
- claim: Reference describes the machinery for consultation, structured like the product, in consistent patterns, with examples that illustrate rather than instruct, and without instruction, explanation, or opinion.
  source: https://diataxis.fr/reference/
  scope: retrieved 2026-10-05
- claim: Explanation gives background, design reasons, alternatives, and connections within a bounded subject, without instruction or reference detail.
  source: https://diataxis.fr/explanation/
  scope: retrieved 2026-10-05
- claim: Release notes serve users about to install or upgrade a release; each note gives the kind of change, flags user action required, names the affected interface or feature, and links documentation; test, build, and fixes for unreleased bugs get none.
  source: https://github.com/kubernetes/community/blob/master/contributors/guide/release-notes.md
  scope: retrieved 2026-10-05
- claim: A changelog is a curated, newest-first list of notable changes per version for humans, with ISO dates, an Unreleased section, changes grouped as Added, Changed, Deprecated, Removed, Fixed, and Security, yanked releases marked, and no commit-log dumps.
  source: https://keepachangelog.com/en/1.1.0/
  scope: version 1.1.0, retrieved 2026-10-05
- claim: A breaking change is documented with the version that introduced it, previous behavior, new behavior, whether it is binary, source, or behavioral, the reason, the recommended action, and the affected APIs.
  source: https://github.com/dotnet/docs/blob/main/.github/ISSUE_TEMPLATE/02-breaking-change.yml
  scope: retrieved 2026-10-05
- claim: A runbook is a step-by-step procedure to a stated outcome, listing tools, special permissions, error handling, escalation, and owner, validated by someone else running it and updated as the process changes.
  source: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_use_runbooks.html
  scope: retrieved 2026-10-05
- claim: A playbook guides the investigation of an incident, with tools and permissions, a communication plan, escalation when no root cause is found, and a pointer to the runbook that resolves a found cause.
  source: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/ops_ready_to_support_use_playbooks.html
  scope: retrieved 2026-10-05
- claim: A playbook entry for an alert states its severity and impact and gives debugging suggestions and actions to mitigate and resolve it.
  source: https://sre.google/workbook/on-call/
  scope: retrieved 2026-10-05
- claim: An architecture document gives a codemap of coarse modules and their relations, architectural invariants, boundaries, and cross-cutting concerns, names files and types instead of linking them, and leaves per-module detail elsewhere.
  source: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
  scope: retrieved 2026-10-05
- claim: An architecture decision record has a title, context, decision, status, and consequences, and a changed decision gets a new record while the old one is marked superseded.
  source: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
  scope: retrieved 2026-10-05
- claim: A security policy states the supported versions and how to report a vulnerability.
  source: https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
  scope: retrieved 2026-10-05
---

Each type below serves one reader doing one kind of work, so a document that mixes two types serves neither reader well. Decide who reads the document and what they are doing when they open it; the type follows from that, and so does what it must contain.

## Using the software

- **README or landing page:** for someone deciding whether the project fits and how to begin. Say what it does and why that is useful, give the shortest verified path to a first success, such as installing it and one minimal use, and say where to get help, how to contribute, and under what license. Link to deeper task, concept, reference, and contribution material rather than holding it; a reader who already knows the project should find what they came for without scrolling far.
- **Tutorial:** for a newcomer learning by doing. Show the achievable goal up front, state the prerequisites, and lead through concrete steps whose result is visible and stated at each checkpoint, ending with where to go next. Leave out explanation, alternatives, and options, and include only steps verified to work as written, since a step that fails breaks the lesson.
- **How-to guide:** for a competent user with a specific goal. Title it by the task, state the prerequisites, give the actions in order with any conditional branches, and say how to confirm the result and recover from a likely failure. Leave out teaching and everything else the reader could do with the same feature.
- **Reference:** for someone consulting facts while working. Mirror the structure of what it describes, present every entry in the same pattern, and state behavior, options, defaults, limits, and warnings, with examples that illustrate rather than instruct. Leave out instructions, explanation, and opinion, and link to them instead.
- **Explanation:** for someone who wants to understand a subject away from a task. Give the background, design reasons, constraints, alternatives, and connections to related subjects, within a stated boundary. Leave out steps and reference detail, and link to them instead.

## Changing versions

These three carry change over time, each for a reader at a different moment.

- **Release notes:** for someone about to install or upgrade to one release. Put anything that requires their action first, then the user-visible changes grouped by kind, each naming the interface or feature it affects and linking its documentation, then known issues and limits. Leave out test and build changes and fixes for bugs no release shipped.
- **Changelog:** for users and developers following a project across versions. Keep any changes not yet released in an Unreleased section on top, then one curated entry per released version, newest first, each with its version, an ISO 8601 date, and a link; group changes as added, changed, deprecated, removed, fixed, and security, and mark a withdrawn release as yanked. Summarize notable changes in the reader's terms; never paste commit messages.
- **Migration or upgrade guide:** for someone moving existing work from one version or mechanism to another. State the versions it covers and who is affected, then for each breaking change the version that introduced it, the verified previous and new behavior, whether it breaks builds, binaries, or only behavior, the reason, the recommended action, and the affected interfaces. Give the steps in order, how to confirm the result, and how to back out where the change can be undone.

## Operating the software

- **Runbook:** for an operator carrying out a known procedure. State the outcome it reaches, its owner, the tools and special permissions it needs, and the steps in order, with error handling and escalation. Treat it as unproven until someone other than its author has followed it, and change it whenever the procedure changes.
- **Playbook:** for an on-call responder investigating an alert or incident. Name the alert or symptom it serves and its severity and impact, then give the diagnostic steps with the tools and permissions they need, who to keep informed, when and to whom to escalate, and the runbook that resolves each known cause.

## Contributing to the software

- **Contributing guide:** for a prospective contributor. Explain how to report a bug, propose a feature, set up the environment and run the tests, and prepare a change the project will accept, along with the contributions wanted, where to ask questions, and the conduct expected.
- **Architecture overview:** for a contributor finding their way around the code. Map the coarse modules and how they relate, so it answers where the thing that does X lives. Call out the invariants, which are often things that must never happen, the boundaries between layers, how data flows between modules, where the design expects extension, and cross-cutting concerns. Name important files, modules, and types instead of linking them, leave per-module detail to the code and its comments, and keep to what rarely changes.
- **Decision record:** for current and future maintainers who need to know why something is the way it is. Give a title, the context and forces in neutral terms, the decision in active voice, its status, and all of its consequences, not only the good ones. When the decision changes, write a new record and mark the old one superseded rather than editing it.
- **Security policy:** for someone who has found a vulnerability. State which versions receive security fixes and how to report a vulnerability.

For a type not listed here, establish what it promises its reader before drafting. If one request truly needs two types, write separate documents or clearly divided sections. Remove empty template sections and content outside the chosen type's outcome.
