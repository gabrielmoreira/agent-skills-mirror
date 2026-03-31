---
Description: It combines Phase 1 (Spec Generation) and Phase 2 (Task Derivation). The Planner agent automatically consumes the finalized spec to generate the static YAML tasks, ensuring no context drift occurs between documentation and planning.
---

Use the subagent tool with the chain parameter to execute this workflow:

1. First, use the `/spec-engineer` agent to analyze the raw idea: `$@` and generate the strict `specs/template.md` formatted document.
2. Then, use the `/planner` agent to decompose the specification from the previous step (use `{previous}` placeholder) into atomic tasks.
3. **Constraint:** The planner must output strictly to `.pi/runs/<spec-id>/tasks.yaml` and is forbidden from writing code.

Execute this as a chain, passing output between steps via {previous}.
