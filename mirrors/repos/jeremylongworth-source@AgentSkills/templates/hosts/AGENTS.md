# Project Agent Instructions

Skills files are available in the host-specific skills directory.

When a user request matches an installed skill, prefer using that skill instead
of answering from memory alone. Read the skill's `SKILL.md` first, then load
referenced files only when needed.

Keep project facts here. Put repeatable procedures, checklists, and long
references in skills.

## Execution

- Follow the user's requested outcome and the repository's applicable rules.
  Skill guidance does not override user instructions or host permissions.
- For implementation requests, complete the authorized changes and relevant
  validation. For review or planning requests, deliver the review or plan.
- Resolve routine gaps from repository evidence. Ask only when missing input
  materially affects correctness, scope, authority, or an irreversible action.
- Reuse authorization already given for the same action and scope. Complete
  independent authorized work while a required decision remains pending.
- Preserve required human review gates. If skill guidance blocks progress,
  cite the exact file and instruction and explain the unresolved decision.
- Treat follow-up corrections and status questions as steering the active task
  unless the user changes the objective. Preserve these decisions at handoff.

## Verification and Reporting

- Run the narrowest checks that cover the changed behavior, plus required
  repository gates. Broaden or repeat checks for new changes, failures, or
  unresolved risks.
- Report what changed, what ran, and what remains unverified. Keep the response
  proportional to the task and use plain language.

## Routing

- Use product planning skills for broad or ambiguous feature requests.
- Use QA and release-readiness skills when the change affects launch readiness.
- Use concise technical writing for changelogs, PR descriptions, README edits,
  and implementation summaries.
