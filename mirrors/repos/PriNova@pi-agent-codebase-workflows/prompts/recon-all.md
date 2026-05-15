---
description: "Run all codebase reconstruction passes when repo size and complexity allow"
argument-hint: "[focus]"
---
Use the `codebase-recon` skill in all-in-one mode.

Focus, if provided: $ARGUMENTS

Use focus to scope all passes to a module/package/app/service/path in large repos or monorepos. Produce scoped observations that can later be consolidated with other scoped artifacts.

First assess whether the repository is small/simple enough for reliable sequential reconstruction. If yes, run passes 1–10, writing artifacts under `docs/agent/` and keeping `AGENTS.md` at project root.

If the repo proves too large or complex, complete the current pass and tell the user which numbered pass to run next.
