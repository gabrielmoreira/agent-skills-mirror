---
description: "Codebase reconstruction pass 7: change guide"
argument-hint: "[focus]"
---
Use `/skill:codebase-recon` Pass 7 — Change Guide.

Focus, if provided: $ARGUMENTS

Use focus to scope this pass to a module/package/app/service/path in large repos or monorepos. If focus is provided, write scoped artifacts under `docs/agent/scopes/by-path/<focus>/` for path focus or `docs/agent/scopes/by-domain/<slug>/` for domain focus, and update `docs/agent/SCOPES.md`.

Read architecture/data/invariants/dependency docs, including matching scoped docs when focus is provided. Write/update `docs/agent/CHANGE_GUIDE.md`, or scoped `CHANGE_GUIDE.md` when focus is provided. Do not edit source code.
