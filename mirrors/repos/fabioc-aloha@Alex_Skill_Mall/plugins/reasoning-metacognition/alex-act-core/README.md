# alex-act-core

The Alex ACT baseline plugin. Ships the reusable framework skills and slash-command prompts that every Alex ACT heir needs regardless of domain.

- **Skills**: 33
- **Prompts**: 12
- **Version**: 0.2.0
- **Upstream**: <https://github.com/fabioc-aloha/Alex_ACT_Core>

## Install

```shell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
copilot plugin install alex-act-core@alex-mall
```

Core belongs at **user scope** so the discipline applies in every workspace. See the constellation's plugin-integration contract for the scope model.

## A note on instructions

Core authors 34 always-on instructions, and a plugin install does **not** deliver them. `plugin.json` has no `instructions` component field; Claude Code and Open Plugin Spec v1.0 draw the same boundary. Core closes this at install time: `install-constellation` Step 6 copies seven of them to `~/.copilot/instructions/`, which both the Copilot CLI and VS Code Chat read. That step is consent-gated, prefixed, receipt-backed, and reversible.

Run `/install-constellation` after installing, or the discipline layer stays inactive.

## Converters

The six document converters need `pandoc` on PATH. `md-to-html` and `md-to-word` additionally need `mermaid-cli` when the source contains Mermaid blocks.

## License

MIT. Maintained by Alex_ACT_Steward.
