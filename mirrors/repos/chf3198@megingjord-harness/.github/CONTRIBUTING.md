# Contributing to devenv-ops

This is a private development workbench. Contributions are by invitation only.

## Workflow

1. Branch from `main`: `git checkout -b feat/<topic>` or `skill/<name>`
2. Keep files ≤100 lines (lint-enforced)
3. Run `npm run lint` and `npm test` before committing
4. Merge to main via PR (or `--no-ff` for local work)
5. Deploy the affected runtime: `npm run deploy:apply`, `npm run deploy:codex:apply`, or `npm run deploy:both:apply`

## Role Baton

All non-trivial work follows the baton sequence:
Manager → Collaborator → Admin → Consultant.
Each role emits a named handoff artifact before the next begins.

## Conventions

- JSON for structured data, Markdown for prose
- Imperative commit messages: `type(scope): description`
- Never edit deployed runtimes directly — all changes flow through this repo
