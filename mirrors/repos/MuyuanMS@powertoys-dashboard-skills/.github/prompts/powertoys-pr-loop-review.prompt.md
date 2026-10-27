Loop-review microsoft/PowerToys PR <PRNumber>: <PRTitle>
https://github.com/microsoft/PowerToys/pull/<PRNumber>

Use the public PowerToys PR review skill:
https://github.com/MuyuanMS/powertoys-pulse-actions/blob/main/.github/skills/powertoys-pr-review/SKILL.md

Follow its compact worker contract. Resume existing work, pin the live upstream
head, and use an isolated worktree and writable personal fork. Use at most
three total cloud review requests across preserved sessions/lanes, with valid
localized fixes between rounds. A grounded architectural flaw ends new rounds
early. Then validate and draft supported findings; do not require a fourth or
zero-comment pass for cap/architectural drafts. Only a clean result needs the
fresh zero-comment/thread and exact-upstream validation gates.

Run both the context/process review and code review. If you are the PR author, use the skill's self-check mode on your own branch. Otherwise, do not modify the author's branch; prepare fixes and review evidence in your own fork.

Do not post comments, reviews, labels, approvals, or other actions to
microsoft/PowerToys without explicit written approval. Return supported
author-facing drafts and private exact-head grounding/validation or saved wait
state. Prefer validated minimal inline suggestions when safe; do not expose
operator diagnostics as PR defects.
