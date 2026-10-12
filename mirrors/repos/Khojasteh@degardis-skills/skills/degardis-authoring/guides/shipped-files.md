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

Static screening does not prove a helper works. During creation or revision, every added or behaviorally changed script or functional asset that the outcome relies on needs an authorized, isolated representative check appropriate to its role: execute a script against a safe fixture, parse/render a template, or otherwise exercise the interface the child agent will use. Verify both the expected result and relevant failure behavior.

Running a script, its tests, or other code the source supplies executes the requester's code, an effect a request for work on the source does not grant by itself, so run it only with that permission from the requester or standing instructions, confined so that nothing outside temporary locations changes, including caches a runtime writes beside the code. A review or packaging task does not execute code from outside the supplied source merely to inspect it. If runtime behavior matters and no permitted run can observe it, return that behavior as unverified, with no claim resting on it, such as a passing test, or hand the question to behavioral evaluation under its own contract.

Authoring also establishes that the child agent can tell when and how to run, open, or follow each shipped file from the final bundle.

## Script tests

A script is shipped because a wrong result is costly, so the source keeps tests that pin its contract: the result for representative inputs, and each kind of failure with its exit status. The child agent never runs them, so they stay in the source, outside the content the manifest selects; in the bundle they would be code no reader reaches.

When creation or revision adds a script, or changes the behavior of one that has no tests, write tests for the contract the change relies on as part of the change. Where tests exist, they record the contract as it stands. Where running them is permitted, run them before the first edit, so a failure the change did not cause is recorded as a starting fact rather than charged to the change or quietly fixed. Update each test that pins behavior the change deliberately alters, and give every changed behavior a case that fails against the starting script and passes against the changed one: a case that passes against both does not test the change. On the final state every test passes, except a starting failure the change did not cause, which is reported.

A review reads a script's tests with the script: they show which parts of its contract the source pins, and a promised behavior without a case is unverified however plausible the code reads.
