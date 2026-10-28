# Test Plan: Goldfish Review Loop Skill

Frontmatter and link checks run in `pytest tests/unit` (see [TESTING.md](../../TESTING.md)).

## Protocol Verification Checklist

When evaluating or exploring `egm-review-loop` interactively in chat, verify:

-   **Step 1 (Intake & Config):** Validates required inputs and resolves standard paths.
-   **Step 2.1 (Target Resolution):** Unconditionally re-scans line numbers before auditing.
-   **Step 2.2 (Review Swarm):** Spawns subagents (or sequentially iterates personas in degraded mode) across requested standards.
-   **Step 2.3 & 2.4 (Resolve Handoff & Turn Boundary):** Hands findings to `egm-resolve` and respects human decision gates.
