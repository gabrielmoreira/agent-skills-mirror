# agents-brain

**Relationship:** two component adaptations. The whole skill is not an established external fork.

## Writing Great Skills Component

- **Source:**
  [mattpocock/skills](https://github.com/mattpocock/skills/tree/697d4ce9742da558fd1ba6697c8e9775e2e302dd/skills/productivity/writing-great-skills),
  `skills/productivity/writing-great-skills/SKILL.md` and `GLOSSARY.md`.
- **Evidence:**
  [introduced under create-skill](https://github.com/PaulRBerg/agent-skills/commit/e8455e33433c4f3e63737aa005ef1848a5eefb5e),
  then
  [merged into agents-brain](https://github.com/PaulRBerg/agent-skills/commit/0e89cedb6692523e33107afc568a97ea334ebd33).
- **Mapping:** both source documents contribute to `skills/agents-brain/references/writing-great-skills.md`.
- **Upstream revision and last reconciled base:** unknown. The linked pre-rename revision is retrievable evidence, not a
  proven local import base or an adopted baseline.
- **Successor:** the
  [2026-07-23 restructure](https://github.com/mattpocock/skills/commit/1fc6573e0e300118ce342fb9365521c9c34eefd4) moved
  the source to
  [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents). It merged
  `GLOSSARY.md` into `SKILL.md` and split skill-specific mechanics into `SKILL-MECHANICS.md`. The original path no
  longer resolves at the current default-branch tip.

## STE Authoring Component

- **Source:**
  [danyuchn/asd-ste100-skill v0.4.0](https://github.com/danyuchn/asd-ste100-skill/tree/32511c6992ecb5f1971e46a2943f2e6adceedafe),
  `SKILL.md` and `references/writing-rules.md`.
- **Evidence:**
  [local introduction](https://github.com/PaulRBerg/agent-skills/commit/aec720494c7bc56dbd7b837033ea13b21bab6526). The
  local reference retains source attribution and the MIT notice.
- **Mapping:** both source files contribute to `skills/agents-brain/references/asd-ste100.md`.
- **Known source pin:** `32511c6992ecb5f1971e46a2943f2e6adceedafe`. This identifies the adapted component source, not a
  whole-skill rebase base.

## Local Behavior and Safe Update Boundary

Limit component updates to their mapped references. Preserve protected technical content, obligation strength,
completion review, attribution, and self-contained reference boundaries. Preserve the distinction between an STE-based
profile and official dictionary compliance. Do not replace the `agents-brain` entrypoint or other workflows with either
source skill. For the unpinned component, recover the base or approve a two-way reconciliation before merging.
