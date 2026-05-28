---
description: "Platform awareness for VS Code tool system: deferred tools require tool_search, external ingest provides context in remote workspaces, skill SKILL.md descriptions surface in the slash picker"
applyTo: "**"
lastReviewed: 2026-05-27
---

# Tool Awareness

## Deferred Tools (VS Code 1.118+)

Many tools are **deferred** (lazy-loaded). They appear in `availableDeferredTools` but cannot be called directly. Load via `tool_search` first with a natural-language capability description.

### Rules

1. **Search before calling.** Calling a deferred tool without loading via `tool_search` fails silently.
2. **Search once per tool.** After load, the tool stays available for the session.
3. **Use broad queries.** One broad search beats multiple narrow ones.
4. **No results means unavailable.** Don't retry with synonyms.

For common deferred tool categories and search-query patterns, see [tool-awareness-categories.instructions.md](tool-awareness-categories.instructions.md) (scoped, loads on tool/MCP/GitHub work).

## External Ingest (VS Code 1.119+)

In remote or virtual-filesystem workspaces (GitHub.dev, VS Code Remote, Codespaces), the editor provides codebase context automatically. `semantic_search` and file operations work transparently — no agent action needed.

## VS Code 1.122 conveniences

| Capability | What it changes for me |
|---|---|
| `/models` slash command | Opens the model picker from chat input. Useful when the user asks to switch models mid-task without leaving chat. |
| BYOK air-gapped | Bring Your Own Key models work without GitHub authentication. Heirs in regulated/enterprise contexts can run Copilot Chat fully offline; the BYOK token counter (introduced 1.120) keeps working. |
| Local agent host default-on (Insiders only) | Watchpoint: when this reaches Stable, deferred-tool resolution may shift. No action until first observed behavior change. |

## Skill Picker Surfacing (VS Code 1.118+)

In 1.118+, `.github/skills/<name>/SKILL.md` files with a non-empty `description` in their frontmatter ALSO surface in the chat slash-command picker (alongside `.github/prompts/*.prompt.md`). Controlled by the experimental setting `github.copilot.chat.skillTool.enabled` (default on).

### Consequence for the brain

When a prompt and a skill share a base name (`/meditate` prompt + `meditation` skill), the picker shows both. This is not a brain defect — the verb-prompt / noun-skill pairing is intentional (prompts are workflow entry points, skills are knowledge bodies). The picker noise is a side effect of the platform surface postdating the brain's design.

### Lever, not stripping

If picker noise is the problem, the lever is the user-level setting:

```jsonc
// settings.json (user scope)
"github.copilot.chat.skillTool.enabled": false
```

**Never strip the SKILL.md `description` to declutter the picker.** The `description` field has three consumers and the picker is the least important of them:

1. **Agent skill discovery (primary)** — every session loads SKILL.md descriptions into the `<skills>` block; this is how the parent agent decides whether to invoke the skill
2. **Brain QA enforcement** — where a brain-qa script exists (Supervisor ships one as `scripts/brain-qa.cjs`), it hard-fails on missing/empty description
3. **Chat picker tooltip** — the surface visible to humans

Stripping (1) and (2) to fix (3) is a Type III error (right cost, wrong problem). The setting is the right scope.

## Would Revise If

Revise if VS Code changes the deferred-tool mechanism (e.g. `tool_search` semantics change, deferred tools become directly callable, or external-ingest changes scope in remote workspaces), or if the "search before calling" rule produces no observed failures over a quarter (the rule is no longer load-bearing because the platform changed).

**Skill picker section falsifier**: revise by 2026-08-24 (90 days) or sooner if any of the following fires: (a) VS Code renames or removes `github.copilot.chat.skillTool.enabled`; (b) setting the flag to `false` does not reduce skill-name entries in the slash picker; (c) the brain restructures SKILL.md frontmatter such that `description` ceases to be the agent-discovery signal. First observed contradiction wins.
