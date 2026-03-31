---
Description: Enforces your mandatory Test-Driven Development rule (Red Phase → Green Phase) in a single chained command.
---

Use the subagent tool with the chain parameter to execute this workflow:

1. First, use the `/test-engineer` agent to read `tasks.yaml` for task: `$@` and generate failing tests in the `tests/` directory.
2. Then, use the `/verifier` agent to run the test suite and capture the failing output (use `{previous}` placeholder).
3. Finally, use the `/implementer` agent to write the minimal `src/` code required to pass the failures identified in the previous step (use `{previous}` placeholder).

Execute this as a chain, passing output between steps via {previous}.
