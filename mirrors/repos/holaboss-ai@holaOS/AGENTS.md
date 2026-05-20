# Repository Guidelines

## User Requirements
- Always use Context7 MCP for library/API documentation, code generation, setup steps, and configuration guidance without requiring an explicit user prompt.

## Commit & Pull Request Guidelines
Commit history follows Conventional Commits (`feat:`, `fix:`, `migrate:`, `chore:`, etc.) and must use a detailed, structured message format.

Commit message format:
1. First line: `<type>: <imperative summary>` scoped to one cohesive concern.
2. Blank line.
3. Bullet list describing what changed and why (APIs, models, migrations, deletions, wiring changes, behavior changes).
4. Include validation coverage in the body when relevant (tests/lint/commands run).

Example pattern:
```text
feat: add cronjobs API and expand proactive analyst bootstrap context

- add a new FastAPI cronjobs service with health and CRUD/list endpoints
- add typed cronjobs client helpers and API-key handling
- update proactive analyst bootstrap context to include profile cronjobs
- add/adjust tests for API, client, and prompt behavior
```

PRs should describe context, validation commands (e.g., `make check`, `npm run runtime:test`), linked issues, and screenshots/log excerpts for API or UI-affecting work. Highlight any Supabase branch or migration impacts and note required environment tweaks.


As you work through an implementation task, maintain a running <task_name>-implementation-notes.html file under docs/implementation_notes/ that captures anything I should know about how the implementation diverges from or interprets the spec, including:

- Design decisions: choices you made where the spec was ambiguous
- Deviations: places where you intentionally departed from the spec, and why
- Tradeoffs:  alternatives you considered and why you picked what you did
- Open questions: anything you'd want me to confirm or revise