# Changelog

This changelog summarizes significant changes to the installable skill.

## [1.1.0](https://github.com/Khojasteh/degardis-skills/releases/download/skills-2026-10-07/coder.zip) - 2026-10-07

Coder 1.1 keeps more decisions with the requester and makes what the agent hands over easier to rely on. Plans now put the requester's choices to them before the design is settled, a statement that something is acceptable authorizes it without requesting it, and documents, plans, and handoffs say what holds rather than how they came to be. Documentation work also chooses a document type by what its reader is doing.

- Plan work puts the choices that belong to the requester to them together, before settling the design, and offers to leave open each one the design can be settled without, for the plan to carry where it governs. A choice that surfaces during design is put as soon as it blocks the design, otherwise before the plan is delivered, and when the requester can't answer first, the plan lists the choices never put to them. How deeply a modernization retires the legacy model is now asked like any other choice.
- An allowance, such as accepting breaking changes, a new dependency, or downtime, authorizes that thing without asking for it. The agent decides as it would without the allowance, counts what the allowed thing costs those who bear it, and takes it only where it serves the requested outcome better than every choice that does without it.
- A new Self-standing artifacts principle applies before writing code, documentation, a plan, a commit message, a handoff, or anything else used without the process that produced it. The artifact states what holds, states a boundary only where a reader would otherwise cross it, and leaves options considered, refused, or ruled out to records whose purpose is that history. Reports now name required work left undone, so options declined along the way no longer read as unfinished work.
- A question about whether, where, or how the work continues is answered from the observed state, and the agent starts nothing the question names until the requester chooses it. A requested handoff, or a redirection that leaves an outcome unfinished, now reaches the handoff guidance.
- A Document types guide covers fifteen types grouped by what their reader is doing: using, upgrading, operating, or contributing to the software. Release notes and a changelog, a runbook and a playbook, and a contributing guide, architecture overview, and decision record now stand apart because their readers differ.
- Command-line help and other interface text now follow the human-facing API documentation guidance, so they state what a command, option, or control accepts, does, and reports.
- .NET XML documentation puts every example of use in `<example>`, with its code in `<code>`, and keeps `<remarks>` for supplementary explanation.
- The JavaScript guidance now applies to TypeScript code, since everything it carries holds once the types are erased.

## [1.0.0](https://github.com/Khojasteh/degardis-skills/releases/download/skills-2026-10-03/coder.zip) - 2026-10-03

Coder 1.0 gives an agent one evidence-led workflow for software work across a product or codebase. It keeps the requested outcome and authorized boundaries visible from investigation and design through change, verification, and reporting, while using the project's own contracts and tools to decide what completion requires.

- Covers ten distinct outcomes: assessing a codebase, planning work, investigating problems, reviewing risk, explaining or documenting software, creating a product, implementing or withdrawing functionality, and verifying a result.
- Grounds decisions in the project's requirements, contracts, consumers, configuration, tooling, and current state instead of relying on ecosystem convention alone.
- Reconciles affected implementation, tests, documentation, interfaces, data, dependencies, security, operations, and other project surfaces without treating every change as requiring every possible check.
- Adds contextual guidance for a broad range of languages, frameworks, runtimes, documentation systems, and test tools so relevant technology rules reach the task that needs them.
