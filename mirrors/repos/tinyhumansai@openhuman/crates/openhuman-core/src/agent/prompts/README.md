# Agent prompt adapters

`agent::prompts` owns the bundled identity assets and OpenHuman-specific
adapters used by agent prompt composition. The portable prompt section API,
tier assembly, and dialect rendering belong to TinyAgents and TinyTools.
OpenHuman selects product content and preserves host policy and provider
message boundaries.

## Public surface

- `types::*`: `PromptContext`, `PromptTool`, `ToolCallFormat`, `UserIdentity`,
  `ConnectedIntegration`, `SubagentRenderOptions`, and the 20K
  `BOOTSTRAP_MAX_CHARS` content cap. Prompt tiers and marker parsing are
  re-exported from TinyAgents for source compatibility.
- `agents_md::*`: thin adapters around TinyAgents' layered `AGENTS.md` loader.
  The adapter applies OpenHuman's path-root policy; the sibling tests cover
  symlink and FIFO rejection, bounded reads, and layer selection.
- `SystemPromptBuilder`, `TieredPrompt`, and `GLOBAL_STYLE_SUFFIX`:
  compatibility exports of the product selector in
  [`crate::prompts::composition`](../../prompts/composition.rs). It selects
  OpenHuman content, appends the grounding and workspace style rules, and
  delegates prompt tier composition to TinyAgents' `PromptComposer`. Stable and
  Context parts remain merged into the first system message; Volatile parts
  remain in a second message.
- `sections::*`: OpenHuman-owned prompt content renderers. The portable section
  contract and tier assembly are implemented by the owner crate.
- `render_subagent_system_prompt*`: OpenHuman's narrow subagent prompt adapter.
  TinyTools renders the protocol for its selected tool-call dialect.
- Other named exports include workspace file sync/injection helpers,
  connected identities, and renderer helpers used by product agents.

## Bundled assets

`IDENTITY.md`, `ROLE.md`, `SOUL.md`, and [`STYLE.md`](./STYLE.md) are the
bundled prompt assets. `sync_workspace_file` seeds a workspace copy, refreshes
an unmodified copy when bundled content changes, and preserves user edits.
The product prompt
composition reads the workspace `STYLE.md`, falling back to the bundled copy
when the file cannot be read. [`USER.md`](./USER.md) is exposed as an MCP
resource and is not read by this module.

Built-in archetype prompts generally live in
`agent_registry/agents/<name>/prompt.rs`; flow prompts live with their flow
agents. `PromptSource::Dynamic` functions provide product content, and the
OpenHuman adapter adds the shared AGENTS.md, grounding, and style content.

The session host builds a prompt once for a session. Stable and Context
content forms the first system message, and Volatile content forms the second.
Resumed sessions reuse persisted system messages verbatim, preserving their
provider cache prefix.
