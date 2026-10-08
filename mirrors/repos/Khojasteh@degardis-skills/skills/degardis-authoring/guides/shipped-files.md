---
title: Shipped scripts and assets
applicability:
- When the work depends on a file a skill ships
- When the work depends on whether a skill should ship a file
x-claim-provenance:
- claim: "An agent runs a bundled script in a non-interactive shell, so a script that waits for interactive input hangs the run."
  source: "https://agentskills.io/skill-creation/using-scripts"
  scope: "Agent Skills format guidance, read 2026-09-29"
- claim: "Agent hosts may truncate long command output."
  source: "https://agentskills.io/skill-creation/using-scripts"
  scope: "Agent Skills format guidance, read 2026-09-29"
---

A script or asset is shipped to be run, opened, copied, or followed, not compiled into a construct. Compiler structure and composition therefore establish neither what the file does nor whether it works.

## File or prose

Ship a script where the child agent would otherwise write the same logic on each run and a wrong version is costly: an operation that is fragile or must follow an exact sequence, a format parsed or validated exactly, or a check whose result must not vary. A tested script is more reliable than code the child agent generates anew. Count context savings only when the host keeps the script body out of the child agent's context. Where an existing tool already does the work with a few arguments, a command with a pinned version serves instead; where the step turns on context or judgment, keep it in prose, since a script fixes what the child agent should still weigh.

Ship an asset when the child agent uses the content as a file, copying, filling, or checking against it; how many runs need it does not matter. Reference material the child agent only reads, such as a table or a short template, belongs on the page when most runs read it, since an asset every run opens adds a load and saves none; move it to an asset when only some runs need it or its size would crowd the page.

## Script design

The child agent runs a script without a terminal it can answer and chooses its next step from what the script prints. Take every input from arguments, the environment, or standard input, since a prompt stalls the run. Describe usage in help output. Print results in a structured form on standard output and diagnostics on standard error, and keep output bounded, with a way to ask for more, since a host may cut long output short. On failure, say what was wrong, what was expected, and what to try, with a distinct exit status for each kind of failure. Make a repeated run safe, reject ambiguous input rather than guess, and give a state-changing operation a preview. Where the language allows, declare the script's dependencies inside it so that one command runs it.

## Screening

Inspect every shipped file with a method appropriate to its type. Read executable and instruction-bearing text end to end. For structured or binary assets, establish the actual type, provenance when relevant, expected consumers, embedded/external references, and any behavior the format can trigger; do not pretend a binary file was screened merely because its name or extension looked familiar. Judge what each file consumes, where it can reach, what it writes or contacts, whether it loads remote material, and whether its contents are authorized for the bundle.

An asset referenced as instructions is guidance the skill delivers, regardless of directory or extension, and is judged like any other page. A file that cannot be inspected enough for the requested judgment remains an explicit coverage gap.

## Functional verification

Static screening does not prove a helper works. During creation or revision, every added or behaviorally changed script or functional asset that the outcome relies on needs an authorized, isolated representative check appropriate to its role: execute a script against a safe fixture, parse/render a template, or otherwise exercise the interface the child agent will use. Verify both the expected result and relevant failure behavior, without using real sensitive material as a convenient fixture.

A read-only review or packaging task does not execute third-party code merely to inspect it. If runtime behavior matters and no authorized observation exists, return that behavior as unverified or hand the question to behavioral evaluation under its own contract.

Authoring also establishes that the child agent can tell when and how to run, open, or follow each shipped file from the final bundle.
