# frontend-design

- **Relationship:** design inspiration followed by an independent rewrite. It is not a direct fork.
- **Source considered:** [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design),
  `skills/frontend-design/SKILL.md`.
- **Evidence:** the original request on 2026-07-21 named that source. The creation session then transitioned to an
  independent rewrite with no copied upstream prose. The
  [implementation](https://github.com/PaulRBerg/agent-skills/commit/f9eb05fd20c13c8db52b900c98738234d717a625) records
  the local result.
- **Upstream revision:** no reconciled upstream revision or mechanical merge base is established.

## Mapping and Local Behavior

The source entrypoint is conceptual inspiration for `skills/frontend-design/SKILL.md`, not a merge mapping.
`references/svg-design.md` and `agents/openai.yaml` are local files with no established upstream mapping.

Preserve subject-specific art direction, shared Chromium verification, local styling guidance, and SVG guidance.

## Safe Update Boundary

Use external changes as design input only. Do not mechanically merge the external skill or label this record as a fork
baseline. Any content update must preserve the independent local implementation and follow its authorized scope.
