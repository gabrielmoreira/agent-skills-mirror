---
name: add-community-skill
description: >
  Adding a Community Agent Skill: a Markdown attack-workflow file that users
  import from the catalog, which then competes in the Intent Router and is
  injected into the agent's system prompt. No Python, no rebuild - but it must
  name only real tools and stay classifiable.
  Trigger: adding or editing a .md workflow under agentic/community-skills/;
  authoring an importable attack skill (not a hardcoded one); editing the
  community-skills catalog or its README.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [agentic]
  auto_invoke:
    - "Adding a Community Agent Skill (importable .md attack workflow)"
---

## When to Use

- Shipping a battle-tested attack workflow as an importable `.md`, without
  hardcoding it into Python.

For a hardcoded, first-class skill (9-layer wiring, badge, per-project toggle),
use `builtin-agent-skill` instead. For a reference/theory doc rather than a
workflow, that is a Community Chat Skill (different flow).

---

## Critical Rules

- **NEVER invent tool names.** Every step must name a tool the agent actually
  has: `query_graph`, `kali_shell`, `execute_curl`, `execute_code`,
  `execute_playwright`, `execute_nuclei`, `execute_hydra`, `metasploit_console`.
  A step naming a non-existent tool is dead on arrival.
- **NEVER rebuild the agent for this.** `./agentic/community-skills` is
  volume-mounted **read-only** into the container
  ([docker-compose.yml:895](../../docker-compose.yml#L895)); the `GET /community-skills`
  endpoint auto-discovers by globbing the directory. Drop the file and it is live
  on the next call. (This is the exception to "agentic/ changes need a rebuild" -
  that applies to baked Python, not the mounted skills dirs.)
- **NEVER write a description that overlaps a built-in skill.** Imported skills
  compete with built-ins in the Intent Router; a generic or overlapping opening
  paragraph means the classifier never selects it. Make the first paragraph and
  the description distinct.
- **Commands must be copy-pasteable** in fenced blocks - no pseudo-code. The
  markdown content is injected verbatim into the system prompt.
- **Remember it is per-user, not global.** Users import via Global Settings >
  Agent Skills; already-imported users do NOT auto-pick-up new skills (they
  re-import; duplicates are skipped by name).

---

## Commands

```bash
# No build. Drop the file and confirm discovery:
ls agentic/community-skills/            # your new <skill>.md lives here
# GET /community-skills globs this dir; the row lands in the Postgres UserAttackSkill
# table only after a user clicks "Import from Community".
```

If [agentic/community-skills/README.md](../../agentic/community-skills/README.md)
has a skills table, add a row (check the file first; do not invent structure).

## Resources

- [docs/readmes/coding_agent_prompts/PROMPT.ADD_COMMUNITY_AGENT_SKILL.md](../../docs/readmes/coding_agent_prompts/PROMPT.ADD_COMMUNITY_AGENT_SKILL.md) - full authoring flow, classification tips, troubleshooting
- Related skill: `builtin-agent-skill`
