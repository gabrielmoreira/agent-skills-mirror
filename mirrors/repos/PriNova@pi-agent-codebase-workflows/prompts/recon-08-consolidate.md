---
description: "Codebase reconstruction pass 8: consolidate semantic artifacts"
argument-hint: "[focus]"
---
Use `/skill:codebase-recon` Pass 8 — Consolidation.

Focus, if provided: $ARGUMENTS

Use focus to scope this pass to a module/package/app/service/path in large repos or monorepos. If `docs/agent/SCOPES.md` exists, use it to select relevant scoped docs and update scope status/currentness as needed.

Consolidate root `AGENTS.md` plus reconstruction docs. Reconcile contradictions without silently deleting disagreement evidence: resolve from source where possible, assign/clarify ownership for shared contracts where evidence supports it, or record unresolved disagreement as drift risk / `Known Unknown` with citations. Keep detailed scope-specific facts in scoped artifacts and summarize only stable repo-level guidance in top-level docs. De-duplicate repeated facts after preserving strongest evidence and materially different scope-specific observations. Do not edit source code.
