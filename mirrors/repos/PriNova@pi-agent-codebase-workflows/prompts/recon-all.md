---
description: "Run all codebase reconstruction passes when repo size and complexity allow"
argument-hint: "[focus]"
---
Use the `codebase-recon` skill in all-in-one mode.

Focus, if provided: $ARGUMENTS

Use focus to scope all passes to a module/package/app/service/path in large repos or monorepos. If focus is provided, write scoped artifacts under `docs/agent/scopes/by-path/<focus>/` for path focus or `docs/agent/scopes/by-domain/<slug>/` for domain focus, and update `docs/agent/SCOPES.md`.

First assess whether the repository is small/simple enough for reliable sequential reconstruction. If yes, run passes 1–10, writing top-level artifacts under `docs/agent/` when unscoped or scoped artifacts under `docs/agent/scopes/**` when focused, and keeping `AGENTS.md` at project root.

If the repo proves too large or complex, complete the current pass and tell the user which numbered pass to run next.
