# grill-me

- **Relationship:** confirmed adaptation from
  [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me),
  `skills/productivity/grill-me`.
- **Evidence:** the user confirmed `mattpocock/skills` as the source on 2026-10-15. The
  [catalog relocation](https://github.com/PaulRBerg/agent-skills/commit/30be06f8ffb2494a9de8b68aaf789458a722b009)
  preserves the initial local entrypoint. A matching copy in another repository does not override the confirmed source.
- **Upstream revision:** unknown. The imported revision and last reconciled base remain unverified.

## Mapping and Local Behavior

The mapping is upstream `skills/productivity/grill-me/SKILL.md` to local `skills/grill-me/SKILL.md`. As checked on
2026-10-15, that upstream entrypoint is an alias for
[grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling). Compare the implementation in
`skills/productivity/grilling/SKILL.md` when assessing current changes. Preserve the local standalone entrypoint instead
of copying the alias. `skills/grill-me/agents/openai.yaml` is local catalog metadata.

Preserve the running decision record, structured question and report formats, explicit accepted unknowns, coordination
exemption, and catalog metadata.

## Safe Update Boundary

Recover the historical upstream base before a three-way merge. The confirmed repository does not establish the imported
revision. Use the explicit source/base fallback in `rebase-skill` when recovery fails.
