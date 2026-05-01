# [Project Name] — GitHub Copilot Configuration

> [!IMPORTANT]
> **SETUP REQUIRED** — This is a template. Complete these steps before your team starts:
>
> 1. **Replace `[Project Name]`** in the heading above with your actual project name
> 2. **Replace the `Stack:` line** with your actual tech stack
> 3. **Fill in `## Conventions`** at the bottom with project-specific coding rules
> 4. **Auto-generate instructions fast**: Type `/init` in Copilot Chat — it analyzes your workspace and generates tailored instructions automatically. Paste the output into the `## Conventions` section.
> 5. **Add recommended slash commands** (`.vscode/settings.json`):
>    ```json
>    "chat.promptFilesRecommendations": {
>      "start-issue": true,
>      "debug": true
>    }
>    ```
>    This surfaces `/start-issue` and `/debug` as suggested actions every time chat opens.

> For the full beginner guide, start at [`learn/00-introduction.md`](https://srisatyalokesh.github.io/copilot-best-practices-for-teams/)

## What This Project Is
[One sentence: what does this project do?]

Stack: [e.g., Node.js + Express + PostgreSQL + Redis]

## Key Documentation
- **[Team Copilot Guide](../docs/team-copilot-guide.md)**: How we use Copilot as a team — start here
- **[Docs Architecture](../docs/docs-architecture.md)**: Where every doc lives

## Our Issue Workflow
Every work item is an **Issue** going through 5 phases:
`/start-issue` → `/discuss` + `/research` → `/plan` → `/execute` → `/verify`

- `/start-issue` confirms your **primary branch**, offers to stay on the current branch or create a fresh branch from the latest primary, then hands off to `/discuss`.
- All feature branches are cut from the **primary branch** (never directly from `main` unless `main` IS the primary branch).

## Where to Find Things
- **Codebase Index**: `docs/codebase/` (Architecture, Stack, Conventions, etc.)
- **Flow docs**: `docs/flows/[flow-name]-flow.md`
- **API docs**: `docs/apis/[domain]/[endpoint].api.md`
- **Issue docs**: `docs/issues/issue-xxx-name.md`
- **Templates**: `docs/templates/`

## For AI Agents
1. Before starting work, read relevant codebase docs in `docs/codebase/` to understand patterns and stack.
2. Read the API doc from `docs/apis/` before touching endpoint code.
3. Read the flow doc from `docs/flows/` for business context.
4. Read the Issue doc from `docs/issues/` for what's planned in this session.
5. **Documentation Sync**: When adding, modifying, or deleting core components, architectural patterns, or dependencies, you MUST update the corresponding files in `docs/codebase/`.
6. After code changes affecting an API → run `/update-api-doc`.
7. After finishing work → update Issue doc progress tracker.

## Conventions (fill in per project — or run `/init` to auto-generate)
- [Your project-specific coding rules go here]

<!-- PRIMARY BRANCH CONFIG — auto-written by /start-issue on first run -->
<!-- Primary branch: main -->

<!-- GIT PROVIDER CONFIG — auto-written by /discuss on first run -->
<!-- Git provider: github -->
