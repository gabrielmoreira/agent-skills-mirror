# Alex ACT Brain Compiler

![Alex ACT Brain Compiler](assets/brain-compiler-banner.svg)

`alex-act-brain-compiler` assesses and authors Markdown brain artifacts for AI
agent projects and plugin sources. Its assessor inventories active brain
artifacts, validates their declared relationships, and reports static safety,
efficiency, and structural-importance signals. Its compiler produces
reviewable, optimized drafts from
an explicitly selected file or text the user explicitly supplies.

## Current Scope

Version `0.4.0` provides two distinct capabilities:

- **Assess Brain** inspects one explicit local repository, plugin, or
  skill-library root, including a `skills-visual` library. It
  discovers every active, non-archival Markdown brain file: instructions,
  skills, prompts, agents, bundled Markdown resources, root documentation, and
  research documentation. JSON manifests are read only to validate component
  paths, but scripts and other non-Markdown files are not inventory, cost,
  duplicate, or optimization candidates in v1. It reports a deterministic JSON
  capability graph to stdout, or to a caller-selected output file outside the
  target root. The report includes an explainable structural-importance score
  for each discovered skill; it is not usage telemetry or a usefulness claim.
- **Compile Brain** improves an explicit Markdown artifact or creates an
  instruction, skill, prompt, agent, or project-wide brain contract from
  user-provided text. It returns a reviewable draft before any file is written
  and never treats unselected conversation content as input.

Remote snapshots and Agent Plugins 1.0 packaging are intentionally not
implemented in this local source checkpoint. Mall distribution follows its
separate validation and human-review workflow.

## Adopt On Other Platforms

`compile-brain` follows the Agent Skills `SKILL.md` format and includes an
opt-in scaffold command for platform-specific installation. Preview before
writing:

```powershell
node scripts/scaffold-platform.cjs --platform claude-code --target C:\Development\my-project
```

Apply the displayed files only after review:

```powershell
node scripts/scaffold-platform.cjs --platform claude-code --target C:\Development\my-project --apply
```

| Platform | Scaffold value | Target location |
| --- | --- | --- |
| GitHub Copilot | `copilot` | `.github/skills/compile-brain/` and `.github/prompts/` |
| Agent Skills hosts | `agent-skills` | `.agents/skills/compile-brain/` |
| Claude Code | `claude-code` | `.claude/skills/compile-brain/` |
| Cursor | `cursor` | `.cursor/skills/compile-brain/` |
| Codex | `codex` | `AGENTS.md` |
| Gemini CLI | `gemini-cli` | `GEMINI.md` |
| ChatGPT | `chatgpt` | `CHATGPT-COMPILE-BRAIN.md` for manual paste into a Project or Custom GPT |

Use `--platform all` to create every adapter in a target repository. Existing
files are never overwritten unless `--force` is supplied with `--apply`.
ChatGPT has no repository discovery path; its generated file is deliberately a
manual adoption artifact, not an automatic integration.

## Documentation

Open `docs/index.html` for the browsable project shell. It
contains the current assessor contract, architecture, research boundary, and
the copied Steward runtime-compiler corpus.

## Run

```powershell
node scripts/assess-brain.cjs --root C:\Development\Alex_ACT_Steward
```

To save a report, provide a path outside the target:

```powershell
node scripts/assess-brain.cjs --root C:\Development\Alex_ACT_Steward --out C:\Temp\steward-assessment.json
```

## Compilation Contract

Use `/compile-brain` when the user asks to improve an existing skill,
instruction, prompt, or agent, or to create one from supplied text. The
compiler:

- accepts only an explicitly named file or exact text the user identifies;
- asks focused questions before drafting when the source leaves purpose,
  trigger, authority, outcome, success criteria, or boundaries unclear;
- preserves behavioral intent while improving structure, metadata, clarity,
  boundaries, and execution consistency;
- inventories behavioral invariants; validates scenarios and destination-relative
  links/resources; and presents a preservation receipt before any source change;
- applies a human-facing artifact gate: when a person outside the authoring team
  will read the artifact to form an impression or make a decision, it names the
  audience, holds back token reduction and imperative compression, and routes
  language review to a copy-review capability rather than folding it into the
  compiled draft;
- starts with a conservative first pass capped at 20% estimated reduction, then
  requires explicit user direction for any further compression;
- requires a fresh-context semantic review with explicit rationale above 35%
  cumulative reduction, and explicitly challenges the operational meaning of
  removed tables, examples, citations, or links above 50%;
- classifies the output as an instruction, skill, prompt, or agent;
- compiles project-wide architecture into a `BRAIN.md` contract with explicit
  hierarchy, routing, arbitration, execution, and verification;
- presents the complete draft and intended destination before writing; and
- writes a new file or overwrites a source only after separate user approval.

A brain contract is a portable supporting artifact. It becomes active only when
the user explicitly incorporates it into the applicable platform entrypoint.

## Assessment Safety Contract

- The target root is read-only.
- The assessor never executes target scripts, hooks, prompts, agents, MCP
  servers, or package managers.
- Output inside, above, or containing the target root is rejected.
- Reports use relative paths and hashes. They do not include source bodies,
  credentials, or user-home paths.
- Static findings distinguish declared, explicitly routed, and runnable states.
  An assessment does not prove host discovery or successful execution.
- The local research library lives in
  `docs/research/`. It is evidence, not an
  implementation dependency.

## Verification

```powershell
npm test
```

The test suite proves deterministic reporting, target immutability,
Markdown-only inventory, standard and visual skill-library classification,
local-link and component-path diagnostics, output-path rejection, and the
compiler's semantic-preservation gate.
