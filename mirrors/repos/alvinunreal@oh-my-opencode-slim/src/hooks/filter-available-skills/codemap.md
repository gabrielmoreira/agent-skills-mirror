# src/hooks/filter-available-skills/

## Responsibility

- Filter `<available_skills>` payload fragments in outgoing messages so they only include skills permitted for the active agent.

## Design

- Factory `createFilterAvailableSkillsHook(_ctx, config)` is defined in `index.ts` and implements `experimental.chat.messages.transform`.
- `getCurrentAgent(messages)` scans backward for the latest user message and defaults to `orchestrator`.
- `filterAvailableSkillsText(text, permissionRules)` is the pure transformation function used per message part.
- Permissions flow:
  - `getAgentOverride(config, agentName)` from `cli/config` resolves override arrays.
  - `getSkillPermissionsForAgent` from `cli/skills` resolves canonical rules (`allow`, `ask`, `deny` wildcard).
  - `isSkillAllowed` checks exact skill rule first, then `'*'` wildcard fallback.
- `<available_skills>...</available_skills>` and nested `<skill>...</skill>` blocks are matched with regex extraction.

## Flow

1. In transform output, determine `agentName` via `getCurrentAgent`.
2. Load `permissionRules = getSkillPermissionsForAgent(agentName, configuredSkills)`.
3. For each `text` part containing `<available_skills>`, run regex replacement:
   - parse `<skill>` entries,
   - keep only allowed names,
   - fallback to `<available_skills>\nNo skills available.\n</available_skills>` when none match.
4. Write transformed `part.text` back to `output.messages` in place.

## Integration

- Hook is wired in `src/hooks/index.ts` and consumed by plugin hook registration.
- Executed in the message path prior to model call, so users do not see changed prompt text in UI, but the model receives constrained capabilities.
- Depends on `cli/skills` and `config` modules, and `PluginInput` only for registration compatibility.
