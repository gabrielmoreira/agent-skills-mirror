Loop-review microsoft/PowerToys PR <PRNumber>: <PRTitle>
https://github.com/microsoft/PowerToys/pull/<PRNumber>

Use the public PowerToys PR review skill:
https://github.com/MuyuanMS/powertoys-pulse-actions/blob/main/.github/skills/powertoys-pr-review/SKILL.md

Follow that skill end to end instead of doing a one-pass review. Resume existing work if present, keep all code changes in an isolated worktree and personal fork, sync the fork's main branch, and iterate GitHub Copilot review until a freshly requested review returns zero new comments, zero unresolved Copilot threads remain, and the affected build succeeds.

Run both the context/process review and code review. If you are the PR author, use the skill's self-check mode on your own branch. Otherwise, do not modify the author's branch; prepare fixes and review evidence in your own fork.

Do not post comments, reviews, labels, approvals, or other actions to microsoft/PowerToys without explicit written approval. Return the converged findings, build evidence, and apply-ready inline suggestions for human approval.
