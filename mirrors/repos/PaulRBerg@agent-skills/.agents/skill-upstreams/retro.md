# retro

- **Relationship:** confirmed adaptation of
  [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/retro),
  `skills/engineering/retro`.
- **Evidence:** the original request on 2026-10-05 named that source and required local history handling. The
  [catalog addition](https://github.com/PaulRBerg/agent-skills/commit/92df3f3ec2882bc72a0876c31cd4024bf9dc98a6) records
  the resulting skill.
- **Reconciled upstream commit:** `a7d038f6bf7f01b516408e95e2fb56e0b338fa6f` (upstream tree
  `335c1862a43da9d629abafdb79ca0c0de118be08`). No previous base is known. The scheduled run on 2026-10-15 used the
  default-branch tip with no requested ref.
- **Base evidence:** on upstream `main`, commit `0243b6ec4ca02f5a188506d0c0342e3617a7dee1` (2026-09-15) set the mapped
  content. Commit `a7d038f` (2026-09-24) moved it from `skills/in-progress/retro` to `skills/engineering/retro` without
  content changes. The tree stayed identical through `main` tip `49dd158d1076134a641b33efb035946536778336` (2026-10-09).
  Thus the 2026-10-05 import could only see this content on `main`. The local entrypoint keeps the deterministic-check
  rule from `0243b6e` and the `Information access` category. The README source path exists only from `a7d038f`.
- **Upstream changes since base:** none on `main` as of 2026-10-15. Branch `retro-lazy-writing-for-agents`
  (`d3dbdff9aa2752abd1cc11fe2255bbd9bcb5b3cb`) changes the `writing-for-agents` step. It is not on the default branch
  and is not reconciled.

## Mapping and Local Behavior

| Upstream path                                 | Local path                        | Relationship                         |
| --------------------------------------------- | --------------------------------- | ------------------------------------ |
| `skills/engineering/retro/SKILL.md`           | `skills/retro/SKILL.md`           | Mapped entrypoint, rewritten locally |
| `skills/engineering/retro/agents/openai.yaml` | `skills/retro/agents/openai.yaml` | Local catalog metadata               |

Preserve these local customizations in `skills/retro/SKILL.md`:

- Catalog frontmatter: `argument-hint`, `compatibility`, `coordination: exempt`, and the `agents-introspection`
  dependency.
- The coordination-exemption declaration and the rule against a second invocation through a skill tool.
- The success criteria, the `[session-or-focus]` input, and the report-only default with explicit apply authority.
- Past transcript access only through `agents-introspection`, with one batched recurrence check for all candidates.
- Task-selected history scope. Do not replace it with a fixed count of recent transcripts.
- Separate handling of environment-state candidates, and inspection of the current mechanism before a proposal.
- The `Skills` category, and the placement rules that replace the upstream `Implementation vs Review` and `Files`
  sections.
- The report contract: status headings, section order, a severity-ordered candidate table, and the stop rule.

`skills/retro/agents/openai.yaml` keeps only `policy.allow_implicit_invocation: false`.

## Excluded Upstream Content

- The `writing-for-agents` step and its references: that skill is not in this catalog. Local prose follows repository
  authoring rules.
- The upstream `interface` fields in `agents/openai.yaml`: local catalog metadata owns these fields.
- The fixed 1,000-line threshold for `CODING_STANDARDS.md`: the local placement rules move content when review guidance
  becomes long.

## Safe Update Boundary

Compare base to upstream for both mapped files. Merge only incoming upstream changes into the local entrypoint. Preserve
local metadata, history delegation, and the exclusions above.
