---
description: "Codebase reconstruction pass 5: bug-risk and subtle-failure analysis"
argument-hint: "[focus]"
---
Use `/skill:codebase-recon` Pass 5 — Bug-Risk and Subtle-Failure Analysis.

Focus, if provided: $ARGUMENTS

Use focus to scope this pass to a module/package/app/service/path in large repos or monorepos. If focus is provided, write scoped artifacts under `docs/agent/scopes/by-path/<focus>/` for path focus or `docs/agent/scopes/by-domain/<slug>/` for domain focus, and update `docs/agent/SCOPES.md`.

Read architecture/data/invariants/dependency docs, including matching scoped docs when focus is provided. Write/update `docs/agent/RISK_REGISTER.md`, or scoped `RISK_REGISTER.md` when focus is provided. Do not edit source code.
