# SwiftlyS2-Toolkit

A general-purpose toolkit for **SwiftlyS2 C#/.NET plugin development** in VS Code with GitHub Copilot.

This toolkit provides a publicly reusable workflow, rule set, template collection, and reference navigation system. It does **not** bind itself to any specific workspace — workspace-specific mappings and private rules should be placed in your own `copilot-instructions.md` and `knowledge-base.md`.

## What's Included

```
agents/                         ← Custom agent modes for Copilot Chat
  SwiftlyS2-Edit-Fast.agent.md
  SwiftlyS2-Edit.agent.md
  SwiftlyS2-Plan-Implementation.agent.md
  SwiftlyS2-Plan-Semantics.agent.md
  SwiftlyS2-Plan-Validation.agent.md
  SwiftlyS2-Plan.agent.md
  SwiftlyS2-Review.agent.md

prompts/                        ← Reusable prompt files
  SwiftlyS2-Toolkit-Audit.prompt.md
  SwiftlyS2-Toolkit-Edit.prompt.md
  SwiftlyS2-Toolkit-Plan.prompt.md

skills/SwiftlyS2-Toolkit/       ← Main skill entry and all assets
  SKILL.md                      ← Skill entry point
  assets/                       ← Templates, checklists, guides, patterns
  references/                   ← Reference indexes and doc maps
```

## Installation

Copy the contents of this repository into the `.github/` folder of your workspace:

```
your-workspace/
└── .github/
    ├── agents/          ← from agents/
    ├── prompts/         ← from prompts/
    └── skills/          ← from skills/
```

Or clone directly:

```bash
# Clone into a temp folder, then copy into your .github/
git clone https://github.com/2oaJ/SwiftlyS2-Toolkit temp-toolkit
cp -r temp-toolkit/agents   your-workspace/.github/
cp -r temp-toolkit/prompts  your-workspace/.github/
cp -r temp-toolkit/skills   your-workspace/.github/
rm -rf temp-toolkit
```

## Agents Overview

| Agent | Purpose |
|---|---|
| `SwiftlyS2-Edit` | Full development agent with review closure loop |
| `SwiftlyS2-Edit-Fast` | Fast execution agent for small/medium tasks |
| `SwiftlyS2-Plan` | Pure planning agent (does not edit code) |
| `SwiftlyS2-Plan-Implementation` | Subagent: file/method-level implementation plan |
| `SwiftlyS2-Plan-Semantics` | Subagent: player-visible semantics and architecture |
| `SwiftlyS2-Plan-Validation` | Subagent: TDD, validation matrices, regression paths |
| `SwiftlyS2-Review` | Review subagent for blocking objections |

## Public Reference Sources

This toolkit references only public sources by default:

1. [SwiftlyS2 Official Docs](https://swiftlys2.net/docs/)
2. [sw2-mdwiki](https://github.com/himenekocn/sw2-mdwiki)
3. [SwiftlyS2 Official Repository](https://github.com/swiftly-solution/swiftlys2)

## License

MIT
