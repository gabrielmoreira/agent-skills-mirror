# frontend-design

- **Relationship:** design inspiration followed by an independent rewrite. It is not a direct fork.
- **Source considered:** [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design),
  `skills/frontend-design/SKILL.md`.
- **Evidence:** the original request on 2026-07-21 named that source. The creation session then transitioned to an
  independent rewrite with no copied upstream prose. The
  [implementation](https://github.com/PaulRBerg/agent-skills/commit/f9eb05fd20c13c8db52b900c98738234d717a625) records
  the local result.
- **Upstream revision:** no reconciled upstream revision or mechanical merge base is established.
- **Guidance review marker:** reviewed
  [`dbd4588f9e1033efb41dad4bef2f7947c8993d44`](https://github.com/anthropics/skills/commit/dbd4588f9e1033efb41dad4bef2f7947c8993d44)
  on 2026-10-24, using
  [`skills/frontend-design/SKILL.md`](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md).
  Its latest path change is
  [`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`](https://github.com/anthropics/skills/commit/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f),
  dated 2026-09-03. This marker records a guidance-only review, not a merge base or a whole-skill import.

## Mapping and Local Behavior

The source entrypoint is conceptual inspiration for `skills/frontend-design/SKILL.md`, not a merge mapping.
`references/svg-design.md` and `agents/openai.yaml` are local files with no established upstream mapping.

Preserve subject-specific art direction, shared Chromium verification, local styling guidance, and SVG guidance.

## Guidance Review: 2026-10-24

The review used the source entrypoint at the marker above. It adapted selected ideas without merging upstream prose. The
local skill received a semantic review before this record was updated.

| Proposal                                                              | Decision                | Rationale and local result                                                                                                |
| --------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Readable body measure                                                 | Accepted                | Recommend fewer than 80 characters per line, with measure and line height adjusted to typeface and content.               |
| Deliberate alignment                                                  | Accepted                | Include alignment in the art direction. The agent chooses it without adding a user question.                              |
| One or two font families                                              | Adapted                 | Permit either count while preserving local font reuse and explicit typography roles.                                      |
| Repetitive decorative cards and motion                                | Adapted                 | Add them to the existing critique. Preserve cards, borders, and containers that communicate useful grouping or hierarchy. |
| Aesthetic examples                                                    | Adapted                 | Treat examples as prompts to question defaults, not absolute bans. The brief and functional need control the choice.      |
| Sparse motion and interaction feedback                                | Adapted                 | Keep motion optional. Use it where it explains hierarchy or feedback, and preserve reduced-motion support.                |
| Subject-specific identity, copy, CSS ownership, and rendered critique | Already present         | Preserve the existing workflow, clear interface copy, predictable selectors, accessibility, and browser verification.     |
| Confirm an inferred subject with the user                             | Excluded                | Keep reasonable assumptions. Ask only when the answer materially changes scope or identity.                               |
| Responsive mobile quality floor                                       | Excluded                | Local desktop-only defaults prevail. Preserve existing responsive behavior and add viewports only when required.          |
| Theme behavior                                                        | Local behavior retained | Keep one theme, system-appearance detection, and existing theme behavior. This review does not expand theme scope.        |
| Imagery and SVG                                                       | Local behavior retained | Keep imagery conditional on the brief and retain local SVG guidance. No mandatory imagery or media generation was added.  |
| Expanded palette and decoration blacklist                             | Excluded                | Keep a compact critique rather than importing every upstream example as a prohibition.                                    |

## Safe Update Boundary

Use external changes as design input only. Do not mechanically merge the external skill or label this record as a fork
baseline. Any content update must preserve the independent local implementation and follow its authorized scope.
