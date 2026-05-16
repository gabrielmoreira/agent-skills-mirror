---
description: "Codebase reconstruction pass 4: dependency rules and drift"
argument-hint: "[focus]"
---
Use `/skill:codebase-recon` Pass 4 — Dependency Rules and Drift Detection.

Focus, if provided: $ARGUMENTS

Use focus to scope this pass to a module/package/app/service/path in large repos or monorepos. If focus is provided, write scoped artifacts under `docs/agent/scopes/by-path/<focus>/` for path focus or `docs/agent/scopes/by-domain/<slug>/` for domain focus, and update `docs/agent/SCOPES.md`.

Read prior reconstruction docs, including matching scoped prior docs when focus is provided. Write/update `docs/agent/DEPENDENCY_RULES.md` and `docs/agent/DESIGN_ISSUES.md`, or scoped `DEPENDENCY_RULES.md` and `DESIGN_ISSUES.md` when focus is provided. Do not edit source code.
