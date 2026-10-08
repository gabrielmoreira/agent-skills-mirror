# Changelog

This changelog summarizes significant changes to the installable skill.

## [2.1.0](https://github.com/Khojasteh/degardis-skills/releases/download/skills-2026-10-07/degardis-authoring.zip) - 2026-10-07

Degardis Authoring 2.1 sharpens what each request gets. A review now judges only Degardis source, a fix is revised or planned only when the requester asked for one, and a plan puts the decisions the requester owes to them before it is designed. When the skill installs the compiler, it takes the latest stable release through the environment's own interpreter. Skills it authors can now carry a principle that keeps the documents, changes, and handoffs their agent writes to what currently holds, so a later reader doesn't mistake a rejected option for a rule, and this skill follows that principle in its own work.

- The description now names what the skill does: write, review, plan, revise, and build Degardis skill source, explain the format, compiler, and authoring choices, and describe or test any skill, with or without its source.
- A review requires the skill's Degardis source. A built bundle, an installed skill, or a skill authored another way is reported as unsupported for review and left unchanged; describing it is still in scope. A review closes the obligation ledger, construct agreements, and path rehearsal only when each applies, and a failed rehearsal case closes as recorded evidence, so a review-only request completes with its findings.
- A review or evaluation hands a finding on only when the requester asked to fix it: to revision when the change is authorized and the host permits it, or to planning when the host prohibits it. A statement that changes are acceptable no longer routes work to revision. A revision hands an acceptance question that only running the skill can settle to evaluation when authority and the host permit it.
- Plan work puts every decision the requester owes, including the version, to them once framing reveals it and before designing, offering to leave open those the design can be settled without. A decision that surfaces during design is put as soon as it blocks the design, otherwise before delivery, and the plan ends with the decisions still open.
- When public-package installation is authorized, the agent installs the latest stable Degardis release unless a version or source is specified, first checks the environment's runtime and tooling against the package's installation instructions, and reports a blocker rather than falling back to an older release. It installs through the target environment's own interpreter, then records and compares the installed version. When the compiler supplies no manual for a source's format, the agent finds an authoritative reference within its reach or leaves the format contract unresolved.
- A blind trial gives the fresh agent what a real performer of the tested request would have, so cases about a built bundle, a brief, or a missing source keep their starting state. A Degardis source given as a fixture carries only the defects its case tests.
- A new Self-standing artifacts principle, the library's sixteenth, has an agent write anything used without the process that produced it as what holds, leaving earlier versions and rejected options to records whose purpose is that history. Skills authored with Degardis Authoring can select it, and this skill carries it itself. Reader-first reporting names required work left undone, Resumable stopping answers a question about continuing instead of acting on it and also applies when another session or agent takes over, and Decision provenance keeps one decision register.
- Shipped-file guidance counts a script's context savings only where the host keeps its body out of the agent's context, and the length rule keeps a clause only for a case it decides.

## [2.0.0](https://github.com/Khojasteh/degardis-skills/releases/download/skills-2026-10-03/degardis-authoring.zip) - 2026-10-03

Degardis Authoring 2.0 moves the existing authoring guidance to Degardis source format 2. The revised compiler and source structure let an agent load less material for each task while carrying governing rules to the pages where they are needed, making the skill more efficient and reliable.

- Migrates the source from format-1 workflows and entries to format-2 tasks, principles, knowledge, and guides.
- Reduces task context by composing the guidance required for the active task instead of loading unrelated authoring material.
- Strengthens safeguards by carrying governing rules into the generated pages before the decisions they control, reducing the risk that an agent misses or receives them too late.
- Narrows the skill to authoring: installing, replacing, publishing, or releasing bundles is no longer part of it.

## [1.0.0](https://github.com/Khojasteh/degardis-skills/releases/download/skills-2026-07-29/degardis-authoring.zip) - 2026-07-29

- Initial release.
