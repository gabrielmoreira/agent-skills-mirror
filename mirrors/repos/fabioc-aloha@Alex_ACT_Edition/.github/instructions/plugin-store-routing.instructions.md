---
type: instruction
lifecycle: stable
inheritance: inheritable
description: Plugin store routing — connect browse and install requests to the Mall, escalate to Supervisor for external needs
application: When the user mentions plugins, stores, browse, or wants capabilities beyond the Mall
applyTo: '**/*plugin*,**/*browse*,**/*store*,**/*agent*'
currency: 2026-05-01
lastReviewed: 2026-05-01
---

# Plugin Store Routing

Route plugin requests to the Mall. Heirs shop the Mall only. The Supervisor curates from external stores.

## When to Fire

| Trigger | Action |
| --- | --- |
| User says "find a skill", "browse skills" | Search the Mall via `/find-skill` |
| User says "install skill X" | Run `/install-from-mall` with the Skill Selection Protocol |
| `/install-from-mall` finds no match in Mall | Tell the user to run `/feedback` requesting the skill. The Supervisor evaluates external stores and promotes to the Mall. |
| User asks for agents, hooks, or MCP servers | These are not in the Mall yet. Run `/feedback` to request. The Supervisor browses plugin stores and installs to `local/`. |
| User explicitly asks to browse plugin stores | Explain the architecture: the Mall is the curated storefront; external stores are evaluated by the Supervisor. Offer to run `/feedback` instead. |

## Architecture

```text
Heirs → Mall (217 curated skills) → /find-skill, /install-from-mall
         ↑
   Supervisor promotes from external stores (production, official, community, playground)
         ↑
   /feedback requests from heirs drive what gets evaluated
```

Heirs never browse external stores directly. This prevents:
- Installing unreviewed skills with no frontmatter compliance
- Shadow-installing skills that duplicate Edition baseline
- Token waste from loading irrelevant skill catalogs

## What the Mall Has vs What Requires Supervisor

| Capability | Mall (heir can install) | Requires Supervisor |
| --- | --- | --- |
| Skills (SKILL.md) | 217 skills, all compliant | Additional skills from 800+ external plugins |
| Agents (.agent.md) | Not yet | Available in plugin stores |
| Hooks (hooks.json) | Not yet | Available in plugin stores |
| MCP servers (.mcp.json) | Not yet | Available in plugin stores |
