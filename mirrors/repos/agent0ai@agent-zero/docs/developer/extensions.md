# Extensions

Extensions are an advanced way to change how Agent Zero behaves.

If you are new, start with plugins instead. Plugins are easier to create, test,
disable, and remove.

Architecture details, extension points, and source-linked explanations now live
in [DeepWiki for Agent Zero](https://deepwiki.com/agent0ai/agent-zero). This
local page stays short on purpose.

## Start Here

| Goal | Start here |
| --- | --- |
| Add a small user-facing feature | [Create a Small Plugin](../guides/create-plugin.md) |
| Change agent behavior for a project | [Projects](../guides/projects.md) |
| Create a specialized agent style | [Agent Profiles](../guides/agent-profiles.md) |
| Study extension internals | [DeepWiki](https://deepwiki.com/agent0ai/agent-zero) |

## When Extensions Make Sense

Use an extension only when a normal plugin, project instruction, skill, or agent
profile is not enough.

Good extension candidates:

- adding behavior at a specific lifecycle point;
- shaping prompts in a reusable way;
- integrating tightly with core tools;
- preparing framework-owned state before a task starts.

Avoid extensions for simple UI changes, one-off scripts, or work that should be
easy to remove. A plugin is usually the cleaner home for that.

## Maintenance Rule

Keep extension changes small and easy to explain. If a reader needs the full
architecture to understand why the extension exists, link to the relevant
DeepWiki page instead of copying the architecture into this repository.

## Related

- [Create a Small Plugin](../guides/create-plugin.md)
- [Agent Profiles](../guides/agent-profiles.md)
- [DeepWiki for Agent Zero](https://deepwiki.com/agent0ai/agent-zero)
