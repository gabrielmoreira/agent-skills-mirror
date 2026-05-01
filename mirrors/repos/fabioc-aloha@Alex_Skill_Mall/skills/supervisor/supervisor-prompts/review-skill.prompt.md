---
description: "Supervisor: Review a submission to Alex_ACT_Edition using the four-gate process"
mode: agent
lastReviewed: 2026-04-30
---

# /review-skill

Run the [skill-review](../skills/skill-review/SKILL.md) skill on the submission identified in the user's request (a PR number, a file path, or an inbox item).

Steps:

1. Locate the submission (read the PR, file, or inbox item)
2. Run the trimmed [act-pass](../instructions/act-pass.instructions.md)
3. Apply the four gates from skill-review's SKILL.md (Spec, Quality, Scope, Safety)
4. Produce the verdict using the output template in SKILL.md
5. Save the verdict to `feedback/inbox/<submission-id>.review.md`
6. Append a row to `decisions/curation-log.md`

If the verdict is **Accept**, also note whether the submission should ship in the next release (add a `ship-in-next-release: true` line to the verdict frontmatter).

If the verdict is **Reject** and the rejection sets a precedent (a class of submission we expect to see again), draft an ADR in `decisions/`.
