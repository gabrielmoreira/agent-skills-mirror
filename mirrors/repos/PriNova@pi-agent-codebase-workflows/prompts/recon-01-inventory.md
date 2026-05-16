---
description: "Codebase reconstruction pass 1: repository inventory"
argument-hint: "[focus]"
---
Use `/skill:codebase-recon` Pass 1 — Repository Inventory.

Focus, if provided: $ARGUMENTS

Use focus to scope this pass to a module/package/app/service/path in large repos or monorepos. If focus is provided, write scoped artifacts under `docs/agent/scopes/by-path/<focus>/` for path focus or `docs/agent/scopes/by-domain/<slug>/` for domain focus, and update `docs/agent/SCOPES.md`.

Write/update `docs/agent/REPO_INVENTORY.md`, or scoped `REPO_INVENTORY.md` when focus is provided. Do not edit source code.
