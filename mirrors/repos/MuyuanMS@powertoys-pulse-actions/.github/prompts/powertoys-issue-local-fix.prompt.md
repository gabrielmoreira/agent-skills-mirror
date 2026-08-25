Start implementing a local fix for microsoft/PowerToys issue <IssueNumber>: <IssueTitle>
https://github.com/microsoft/PowerToys/issues/<IssueNumber>

Read the current public dashboard artifact:
https://raw.githubusercontent.com/MuyuanMS/powertoys-pulse-actions/main/data/items/<IssueNumber>.json

Use the public PowerToys design-to-PR skill:
https://github.com/MuyuanMS/powertoys-pulse-actions/blob/main/.github/skills/powertoys-design-to-pr/SKILL.md

If the artifact does not contain a current approved implementation-grade design, stop implementation and use the issue-to-design skill first:
https://github.com/MuyuanMS/powertoys-pulse-actions/blob/main/.github/skills/powertoys-issue-to-design/SKILL.md

Resume existing fork issues, branches, PRs, or worktrees instead of duplicating work. Implement the approved design in an isolated worktree and personal fork, build and test the affected module, then iterate GitHub Copilot review until a fresh review returns zero new comments and zero unresolved Copilot threads remain.

Do not open an upstream PR, post upstream comments, assign the issue, or take any other action on microsoft/PowerToys without explicit written approval. Return the completed fork PR, validation evidence, and proposed upstream PR details for human approval.
