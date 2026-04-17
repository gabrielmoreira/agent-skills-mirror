# SwiftlyS2-Toolkit

`SwiftlyS2-Toolkit` is a Copilot-based agent toolkit for SwiftlyS2 plugin development. Our goal is simple: with just one sentence, the agent can write high-performance, high-quality SwiftlyS2 plugin code. If you are using another kind of agent CLI, you can still use the skills and prompts in this toolkit.

- Chinese Version: [`README.md`](./README.md)
- Skill: [`SKILL.md`](./SKILL.md)

## Features

- **Prompt constraints**: carefully designed prompts help keep generated code aligned with SwiftlyS2 plugin best practices and performance expectations
- **Code quality**: the generated code is tested carefully so it stays high-performance and high-quality
- **Ease of use**: just one sentence is enough to generate SwiftlyS2 plugin code that matches the expected standard, which greatly improves development efficiency
- **Custom agents**: `edit`, `plan`, and `review` agents are provided to support different stages of development
- **Skill index**: agents can easily find official docs, community resources, and code examples related to SwiftlyS2, helping ensure the generated code follows the latest practices
- **Experience sources**: the toolkit combines official documentation with refined experience extracted from many original plugins (10+ small original plugins, 10+ medium original plugins, 3+ large original plugins)
- **Stability**: after a long period of testing and iteration, plugin code generated with this toolkit serves thousands of players every day and is less likely to run into server crashes or performance problems

## What is inside

- `SKILL.md`: the main entry and usage boundary
- `prompts/`: `plan`, `audit`, and `edit` workflow prompts
- `references/`: public knowledge indexes and official documentation navigation
- `assets/`: templates, checklists, and workflow assets

## Where to start

### `plan`

Use it when you want the agent to think through an implementation plan first, for example:

- Method-level implementation plans
- Breaking down changes before implementation
- Migration / refactoring / behavior-alignment plans

### `audit`

Use it when you want the agent to review plugin code first, for example:

- Architecture, threading, lifecycle, performance, and behavioral drift audits
- Tasks that need diagnosis before implementation

### `edit`

Use it when the goal is clear and you want the agent to start working directly, for example:

- Direct code changes
- A locate / modify / verify loop completed in a single conversation

## Knowledge base index

### `references/swiftlys2-plugin-playbook.md`

Leans toward engineering experience, useful for quickly judging:

- What kind of plugin this task resembles
- Where lifecycle and thread boundaries sit
- How to handle Hook / Schema / NetMessages / Menu / Worker subsystems

### `references/swiftlys2-kb-index.md`

Leans toward public knowledge navigation, useful for quickly finding:

- Official documentation entry points
- sw2-mdwiki entry points
- Official repository structure entry points

### `references/swiftlys2-official-docs-map.md`

Leans toward a trimmed navigation map of the official docs, useful for quickly seeing:

- The structure of the Development / Guides sections
- The key API Reference entry points
- Which pages are worth deeper lookup

### `references/swiftlys2-asset-inventory.md`

Leans toward a toolkit asset inventory, useful for quickly understanding:

- Which reusable entry points exist
- Which items are core assets

### `assets/README.md`

- Official topic → local assets → general usage navigation

## Trusted sources

To keep the public documentation consistent, we anchor it on a small set of trusted sources:

- SwiftlyS2 official documentation: `https://swiftlys2.net/docs/`
- sw2-mdwiki: `https://github.com/himenekocn/sw2-mdwiki`
- SwiftlyS2 official repository: `https://github.com/swiftly-solution/swiftlys2`

If you have your own local reference repositories, workspace project mappings, historical reference projects, or customized implementation experience, place them in:

- `../../copilot-instructions.md`
- `../../knowledge-base.md`

It is recommended to deploy the sw2-mdwiki project into the local workspace as a local reference repository; retrieval will be much faster and it will stay easier to keep the toolkit consistent.

## Reusable assets

- `assets/development/*`: templates and checklists aligned with the SwiftlyS2 official Development documentation
- `assets/guides/*`: templates and explanations aligned with the Guides documentation
- `assets/patterns/background-workers/worker-template.cs.md`: background worker skeleton
- `assets/workflows/planning/*`: method-level plan templates
- `assets/workflows/audit/*`: audit report templates

## Contributing

- Pull requests are welcome, and issue reports / usage feedback are welcome too

## Thanks

- The SwiftlyS2 team
- The sw2-mdwiki project
