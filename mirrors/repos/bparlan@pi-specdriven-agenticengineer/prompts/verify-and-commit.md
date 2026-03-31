---
Description: A closed-loop quality gate that runs tests, linters, and type-checks, automatically attempting to fix failures before committing.
---

Use the subagent tool with the chain parameter to execute this workflow:

1. First, use the `/verifier` agent to execute the quality gates: (e.g., Jest/Vitest/TSC for TypeScript, Pytest/Mypy for Python, etc.)
2. Then, use the `/implementer` agent to apply minimal fixes if the previous step produced error outputs (use `{previous}` placeholder).
3. **Auto-Repair Loop Constraint:** If failures persist, repeat the `/verifier /implementer` loop for a maximum of 3 retries. If it still fails, execute a hard stop and escalate for manual intervention.
4. Finally, if all gates pass green, use the `/verifier` agent to update `tasks.yaml` to `status: completed` and execute the Git commit using your strict `feat(<spec-id>): <description> (<task-id>)` formatting.

Execute this as a chain, passing output between steps via {previous}.
