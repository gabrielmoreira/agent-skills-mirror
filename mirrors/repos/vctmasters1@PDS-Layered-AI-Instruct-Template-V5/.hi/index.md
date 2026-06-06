# Index — Master Section Index

**Scope**: Project-wide
**Last Updated**: 2026-06-05

> This file is the **master index** of every instruction file and tool across the `.hi/` hierarchy.
> It enables fast lookup: find the authoritative source for any topic without reading every file.
>
> **Start here**: [`.hi/instruct.md` → ⛔ Mandatory Reading Contract](instruct.md#-stop--mandatory-reading-contract-non-negotiable) is the single forcing master (incl. its [Scope & Coexistence](instruct.md#scope-authority--coexistence-read-this-carefully) clause). This index is a navigation aid under it.
>
> **Maintenance**: Update this file whenever any `.hi/instruct.md`, prompt, agent, or convention file is created, modified, or retired.
> Run `/hip-update-index` in Copilot Chat to rebuild automatically.
> In this template repository, some indexed files intentionally contain placeholders until `/hip-onboard` (or manual onboarding) fills project-specific values.

---

## How to Use

1. Search this index for keywords related to your topic
2. Follow the link to the exact file
3. Read that section — it is the **single source of truth**
4. Do not restate or copy the content elsewhere; cross-reference it

**If a topic is not in this index**, it has not been formally defined. Flag the gap, add it to the appropriate `.hi/instruct.md`, then rerun `/hip-update-index`.

> **Note on link granularity**: Entries link to the **file**, not the section anchor. Section headings drift faster than file paths, so file-level links stay valid through more edits. Within each linked file, use its own Contents table to jump to a section.

---

## Index

### Meta & System

| Topic | File | Description |
|-------|------|-------------|
| Gateway / entry point | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Pointer file; quick navigation into the `.hi/` hierarchy |
| System meta-rules | [`.hi/instruct.md`](instruct.md) | How the depth-priority hierarchy works; Routing Gateway; tiers; governed workflows; runtime |
| Project root authority | [`.hi/.hi-instruct.md`](.hi-instruct.md) | Project-specific rules, architecture, conventions, and tooling after adoption |
| Discovery anchor (agents) | [`AGENTS.md`](../AGENTS.md) | Entry point for AI coding agents; points at the `.hi/` hierarchy |
| Claude Code pointer | [`CLAUDE.md`](../CLAUDE.md) | Pointer file directing Claude Code to the `.hi/` hierarchy |

### Tier 1 Prompts (User-Facing)

| Command | File | Description |
|---------|------|-------------|
| `/hip-onboard` | [`.hi/prompts/tier-1/hip-onboard.prompt.md`](prompts/tier-1/hip-onboard.prompt.md) | Initialize or update project metadata; run first to fill placeholders, re-run to add modules |
| `/hip-import-execute` | [`.hi/prompts/tier-1/hip-import-execute.prompt.md`](prompts/tier-1/hip-import-execute.prompt.md) | Import/merge external projects with full Phase 0-6 orchestration; mandatory for any import/clone/merge |
| `/hip-new-module` | [`.hi/prompts/tier-1/hip-new-module.prompt.md`](prompts/tier-1/hip-new-module.prompt.md) | Scaffold a new module and register it |
| `/hip-archive` | [`.hi/prompts/tier-1/hip-archive.prompt.md`](prompts/tier-1/hip-archive.prompt.md) | Safely archive a file or directory following the never-delete convention |
| `/hip-update-index` | [`.hi/prompts/tier-1/hip-update-index.prompt.md`](prompts/tier-1/hip-update-index.prompt.md) | Rebuild `.hi/index.md` from current state |
| `/hip-validate` | [`.hi/prompts/tier-1/hip-validate.prompt.md`](prompts/tier-1/hip-validate.prompt.md) | Run the Hierarchical-Instruct drift validator; report findings (no edits) |
| `/hip-env-check` | [`.hi/prompts/tier-1/hip-env-check.prompt.md`](prompts/tier-1/hip-env-check.prompt.md) | Audit host-vs-container isolation; report only, never installs |
| `/hip-foresight` | [`.hi/prompts/tier-1/hip-foresight.prompt.md`](prompts/tier-1/hip-foresight.prompt.md) | Run foresight gap/risk analysis on the current task before acting (read-only) |
| `/hip-reflect` | [`.hi/prompts/tier-1/hip-reflect.prompt.md`](prompts/tier-1/hip-reflect.prompt.md) | Post-task reflection; identify instruction gaps and propose `.hi/` improvements |
| `/hip-git` | [`.hi/prompts/tier-1/hip-git.prompt.md`](prompts/tier-1/hip-git.prompt.md) | Query git state (`branch \| commit \| pr \| status`); read-only unless asked |
| `/hip-deploy-mode` | [`.hi/prompts/tier-1/hip-deploy-mode.prompt.md`](prompts/tier-1/hip-deploy-mode.prompt.md) | Inspect or switch the active `DEPLOY_MODE` scope (never mutates the shell) |
| `/hip-observe` | [`.hi/prompts/tier-1/hip-observe.prompt.md`](prompts/tier-1/hip-observe.prompt.md) | Display runtime observability: metrics, logs, cheat sheets (read-only) |
| `/hip-metrics` | [`.hi/prompts/tier-1/hip-metrics.prompt.md`](prompts/tier-1/hip-metrics.prompt.md) | Print a token/budget/approval/anomaly digest over a window |
| `/hip-route` | [`.hi/prompts/tier-1/hip-route.prompt.md`](prompts/tier-1/hip-route.prompt.md) | Routing Gateway: resolve scope and route a task to the authoritative agent |
| `/hip-doctor` | [`.hi/prompts/tier-1/hip-doctor.prompt.md`](prompts/tier-1/hip-doctor.prompt.md) | Diagnose system/runtime state and report issues |
| `/hip-check-yourself` | [`.hi/prompts/tier-1/hip-check-yourself.prompt.md`](prompts/tier-1/hip-check-yourself.prompt.md) | Audit AI instruction alignment; re-read rules and reset to baseline if drifted |
| `/hip-ports-check` | [`.hi/prompts/tier-1/hip-ports-check.prompt.md`](prompts/tier-1/hip-ports-check.prompt.md) | Validate the port registry against project code; detect collisions and drift |
| `/hip-plugin-discover` | [`.hi/prompts/tier-1/hip-plugin-discover.prompt.md`](prompts/tier-1/hip-plugin-discover.prompt.md) | Enumerate optional plugins; summarize manifests (read-only) |
| `/hip-add-custom-rule` | [`.hi/prompts/tier-1/hip-add-custom-rule.prompt.md`](prompts/tier-1/hip-add-custom-rule.prompt.md) | Add a custom project rule to the appropriate `.hi/` file |
| `/hip-autonomous-start` | [`.hi/prompts/tier-1/hip-autonomous-start.prompt.md`](prompts/tier-1/hip-autonomous-start.prompt.md) | **Opt-in** — start a bounded autonomous run; refuses unless explicitly enabled |

### Tier 2 Prompts (Internal Subsystem)

| Command | File | Description |
|---------|------|-------------|
| `/hip-adapt-infrastructure` | [`.hi/prompts/tier-2/hip-adapt-infrastructure.prompt.md`](prompts/tier-2/hip-adapt-infrastructure.prompt.md) | Adapt imported prompts/agents/skills to the routing paradigm |
| `/hip-audit-registries` | [`.hi/prompts/tier-2/hip-audit-registries.prompt.md`](prompts/tier-2/hip-audit-registries.prompt.md) | Reconcile naming registries with the codebase |
| `/hip-dispatch-test` | [`.hi/prompts/tier-2/hip-dispatch-test.prompt.md`](prompts/tier-2/hip-dispatch-test.prompt.md) | Internal test dispatch for orchestration |
| `/hip-hide-example-code` | [`.hi/prompts/tier-2/hip-hide-example-code.prompt.md`](prompts/tier-2/hip-hide-example-code.prompt.md) | Mask/relocate example code during adoption |
| `/hip-phase-2-fixer` | [`.hi/prompts/tier-2/hip-phase-2-fixer.prompt.md`](prompts/tier-2/hip-phase-2-fixer.prompt.md) | Phase 2 infrastructure fixer (import pipeline) |
| `/hip-phase-2-post-learner` | [`.hi/prompts/tier-2/hip-phase-2-post-learner.prompt.md`](prompts/tier-2/hip-phase-2-post-learner.prompt.md) | Post-phase learning capture (import pipeline) |
| `/hip-suggest-tiers` | [`.hi/prompts/tier-2/hip-suggest-tiers.prompt.md`](prompts/tier-2/hip-suggest-tiers.prompt.md) | Suggest tier-1/tier-2 classification for artifacts |
| `/hip-test-verification` | [`.hi/prompts/tier-2/hip-test-verification.prompt.md`](prompts/tier-2/hip-test-verification.prompt.md) | Internal test verification |

### Tier 1 Agents (User-Facing Orchestration)

| Agent | File | Description |
|-------|------|-------------|
| Router | [`.hi/agents/tier-1/hia-router.agent.md`](agents/tier-1/hia-router.agent.md) | Routing Gateway: resolves scope and routes to the next-hop agent |
| Super | [`.hi/agents/tier-1/hia-super.agent.md`](agents/tier-1/hia-super.agent.md) | Domain supervisor for complex, multi-phase work |
| Curator | [`.hi/agents/tier-1/hia-curator.agent.md`](agents/tier-1/hia-curator.agent.md) | Syncs `.hi/instruct.md`, convention files, and `.hi/index.md` with reality |
| Imports | [`.hi/agents/tier-1/hia-imports.agent.md`](agents/tier-1/hia-imports.agent.md) | Orchestrates import/merge workflows |
| Infrastructure | [`.hi/agents/tier-1/hia-infrastructure.agent.md`](agents/tier-1/hia-infrastructure.agent.md) | Adapts imported infrastructure to the routing paradigm |

### Tier 2 Agents — Workers

| Agent | File | Description |
|-------|------|-------------|
| Scaffolder | [`.hi/agents/tier-2/workers/hia-scaffolder.agent.md`](agents/tier-2/workers/hia-scaffolder.agent.md) | Produces a structured plan only (no implementation) |
| Generator | [`.hi/agents/tier-2/workers/hia-generator.agent.md`](agents/tier-2/workers/hia-generator.agent.md) | Implements an approved scaffold within scope conventions |
| Validator | [`.hi/agents/tier-2/workers/hia-validator.agent.md`](agents/tier-2/workers/hia-validator.agent.md) | Enforces declared conventions and governance (read-only) |
| Tester | [`.hi/agents/tier-2/workers/hia-tester.agent.md`](agents/tier-2/workers/hia-tester.agent.md) | Writes tests after validation passes |
| Reviewer | [`.hi/agents/tier-2/workers/hia-reviewer.agent.md`](agents/tier-2/workers/hia-reviewer.agent.md) | Final instruction-drift gate before finalize |

### Tier 2 Agents — Observers

| Agent | File | Description |
|-------|------|-------------|
| Explorer | [`.hi/agents/tier-2/observers/hia-explorer.agent.md`](agents/tier-2/observers/hia-explorer.agent.md) | Read-only codebase exploration |
| Compliance | [`.hi/agents/tier-2/observers/hia-compliance.agent.md`](agents/tier-2/observers/hia-compliance.agent.md) | Read-only modularity reviewer; catches monolithic drift, proposes refactors |
| Learner | [`.hi/agents/tier-2/observers/hia-learner.agent.md`](agents/tier-2/observers/hia-learner.agent.md) | Distills completed tasks into `.hi/knowledge/`; proposes edits via Curator |
| Observer | [`.hi/agents/tier-2/observers/hia-observer.agent.md`](agents/tier-2/observers/hia-observer.agent.md) | Read-only observability aggregator over `.hi/logs/metrics-*.jsonl` |

### Tier 2 Agents — Specialists

| Agent | File | Description |
|-------|------|-------------|
| Naming | [`.hi/agents/tier-2/specialists/hia-naming.agent.md`](agents/tier-2/specialists/hia-naming.agent.md) | Authoritative naming service; consult before creating or renaming any artifact |
| Ports | [`.hi/agents/tier-2/specialists/hia-ports.agent.md`](agents/tier-2/specialists/hia-ports.agent.md) | Port registry curator; detects collisions, range violations, drift |
| Environment | [`.hi/agents/tier-2/specialists/hia-environment.agent.md`](agents/tier-2/specialists/hia-environment.agent.md) | Host-vs-containment guard; never installs silently |
| Deployment | [`.hi/agents/tier-2/specialists/hia-deployment.agent.md`](agents/tier-2/specialists/hia-deployment.agent.md) | Reviews `.hi/deployment/<mode>/.hi/instruct.md` against reality |
| Workflow | [`.hi/agents/tier-2/specialists/hia-workflow.agent.md`](agents/tier-2/specialists/hia-workflow.agent.md) | Reviews CI workflows against recent code changes |
| Prompt | [`.hi/agents/tier-2/specialists/hia-prompt.agent.md`](agents/tier-2/specialists/hia-prompt.agent.md) | Reviews slash-command prompts against recent code changes |
| Todo | [`.hi/agents/tier-2/specialists/hia-todo.agent.md`](agents/tier-2/specialists/hia-todo.agent.md) | Curates TODO lists and inline `TODO/FIXME`; deduplicates and ages |
| Version Control | [`.hi/agents/tier-2/specialists/hia-versioncontrol.agent.md`](agents/tier-2/specialists/hia-versioncontrol.agent.md) | Version-control specialist; branch/commit/PR hygiene |
| Cleanup | [`.hi/agents/tier-2/specialists/hia-cleanup.agent.md`](agents/tier-2/specialists/hia-cleanup.agent.md) | Detects orphaned/stale files; archives per never-delete rule (no auto-delete) |

### Skills

| Skill | File | Description |
|-------|------|-------------|
| Project Navigation | [`.hi/skills/project-navigation/SKILL.md`](skills/project-navigation/SKILL.md) | How to navigate this project's Hierarchical-Instruct hierarchy |
| Archiving | [`.hi/skills/archiving/SKILL.md`](skills/archiving/SKILL.md) | Deterministic, never-delete archival into the `.archive/` of an item's parent folder |

### Discovery & Registry

| Topic | File | Description |
|-------|------|-------------|
| Discovery / Registry overview | [`.hi/registry/README.md`](registry/README.md) | Filesystem-as-source discovery; registry format; how to run |
| Discovery engine | [`.hi/registry/discovery_engine.py`](registry/discovery_engine.py) | Scans `.hi/` and generates the artifact registry |
| Watch mode | [`.hi/registry/watch_mode.py`](registry/watch_mode.py) | Re-runs discovery automatically on file changes (dev; watchdog optional) |
| Master registry | [`.hi/registry/master-registry.json`](registry/master-registry.json) | Generated list of discoverable prompts/agents/skills/workflows |

### Engine & Runtime

| Topic | File | Description |
|-------|------|-------------|
| Engine overview | [`.hi/engine/README.md`](engine/README.md) | Runtime engine: instruction resolver, foresight, heartbeat, tool validator, dispatcher |
| Effective instructions resolver | [`.hi/engine/get_effective_instructions.py`](engine/get_effective_instructions.py) | Canonical depth-priority resolver — deepest `.hi/instruct.md` wins, project-bounded by default (CLI: `--path`, `--workspace`, `--explain`) |
| Resolution explainer (audit) | [`.hi/engine/get_effective_instructions.py`](engine/get_effective_instructions.py) | `--explain` report: governing layers + topic override map, so "deepest wins" is auditable in code review |
| Resolver conformance gate | [`.hi/engine/check_resolution_conformance.py`](engine/check_resolution_conformance.py) | Asserts the live repo satisfies depth-priority (deepest wins, no ancestor bleed); runs in CI |
| MCP server (resolver + tools) | [`.hi/mcp/python/hia_mcp/server.py`](mcp/python/hia_mcp/server.py) | Exposes `resolve_instructions` and governed tools to any MCP-aware client; mirrors the resolver's bounded contract |
| Foresight engine | [`.hi/engine/foresight_engine.py`](engine/foresight_engine.py) | Pre-task gap/risk analysis (observable variant: `foresight_engine_observable.py`) |
| Heartbeat engine | [`.hi/engine/heartbeat_engine_observable.py`](engine/heartbeat_engine_observable.py) | Periodic re-read of scope authority + guardrails |
| Tool validator | [`.hi/engine/validate_tools.py`](engine/validate_tools.py) | Validates governed-tool JSON checklists against schema |
| Audit + alignment | [`.hi/engine/audit_logger.py`](engine/audit_logger.py) | Action logging; see also `audit_alignment.py` |
| Metrics | [`.hi/engine/show_metrics.py`](engine/show_metrics.py) | Token/budget/approval/anomaly digest source; aggregates local-vs-cloud compute from `metrics-*.jsonl` |
| Metric-wiring gate | [`.hi/engine/check_metric_wiring.py`](engine/check_metric_wiring.py) | Coherence gate: asserts the emit → attribute → observe chain (record-metric + compute provenance) stays intact; CI-enforced |
| Port validator | [`.hi/engine/port_validator.py`](engine/port_validator.py) | Validates the port registry against project code |
| Custom rules | [`.hi/engine/add_custom_rule.py`](engine/add_custom_rule.py) | Adds/validates custom project rules (`custom_rules_validator.py`) |
| Import pipeline | [`.hi/engine/import_analyzer.py`](engine/import_analyzer.py) | Phase 0-6 import/merge executors (`phase1_executor.py`, `phase2_executor.py`, `merge_validator.py`, etc.) |
| Local dispatcher | [`.hi/engine/dispatcher_local.py`](engine/dispatcher_local.py) | Local model/agent dispatch |
| Memory hygiene | [`.hi/engine/memory_hygiene.py`](engine/memory_hygiene.py) | Knowledge-base cleanup |
| Archive tool | [`.hi/engine/archive.py`](engine/archive.py) | Deterministic never-delete archival into the `.archive/` of an item's parent (used by `/hip-archive` and the cleanup agent) |
| Engine tests | [`.hi/engine/tests/`](engine/tests/) | Unit tests for resolver and tool validator |

### Agentic Runtime Support

| Topic | File | Description |
|-------|------|-------------|
| Per-agent context manifest | [`.hi/agents/context.md`](agents/context.md) | Load sequence and per-agent context manifest |
| Agent runtime contract | [`.hi/agents/runtime.md`](agents/runtime.md) | Heartbeat, governed tools, runtime behavior contract |
| Governed tool checklists | [`.hi/agents/tools/README.md`](agents/tools/README.md) | 24 governed-tool JSON checklists + schema (`_schema.json`) |
| Agent state | `.hi/agents/state/` | Per-agent runtime state; gitignored |
| Heartbeat protocol | [`.hi/heartbeat.md`](heartbeat.md) | Periodic re-read protocol for long-running work |
| Agent configuration | [`.hi/agent-config.yaml`](agent-config.yaml) | Agent network configuration |
| Levels / authority model | [`.hi/levels.md`](levels.md) | Depth-priority authority levels |
| Pause switch | [`.hi/PAUSE.example`](PAUSE.example) | Drop a `.hi/PAUSE` file to halt autonomous runs |
| Foresight outputs | `.hi/foresight/` | Runtime output; gitignored |
| Knowledge base | [`.hi/knowledge/`](knowledge/) | Accumulated runtime knowledge + cheat-sheets |
| Audit logs | `.hi/logs/` | Agent change/metric logs; gitignored |

### Naming & Convention Registries

| Topic | File | Description |
|-------|------|-------------|
| Coding prefixes | [`.hi/coding-prefixes.md`](coding-prefixes.md) | Reserved identifier prefixes across the codebase |
| API conventions | [`.hi/api-conventions.md`](api-conventions.md) | Endpoint naming, request/response conventions |
| Database schema registry | [`.hi/database-schema.md`](database-schema.md) | Table/column naming and schema conventions |
| Error codes | [`.hi/error-codes.md`](error-codes.md) | Canonical error-code registry |
| Config variables | [`.hi/config-vars.md`](config-vars.md) | Environment/config variable registry |
| Port registry | [`.hi/ports.md`](ports.md) | Allocated ports and ranges; collision rules |
| Version control rules | [`.hi/version-control.md`](version-control.md) | Branch/commit/PR conventions |
| Archive protocol | [`.hi/archive-protocol.md`](archive-protocol.md) | Never-delete archive procedure detail |
| Topics map | [`.hi/topics.md`](topics.md) | Cross-cutting topic index |

### Autonomous Layer (Opt-In)

| Topic | File | Description |
|-------|------|-------------|
| Orchestrator | [`.hi/autonomous/orchestrator.md`](autonomous/orchestrator.md) | Bounded autonomous orchestration over the existing agent network |
| Safety guardrails | [`.hi/autonomous/safety-guardrails.md`](autonomous/safety-guardrails.md) | Hard ceilings, prohibited edits, halt conditions |
| Task queue | [`.hi/autonomous/task-queue.md`](autonomous/task-queue.md) | Queue model and lifecycle |
| Configuration | [`.hi/autonomous/autonomy-config.yaml`](autonomous/autonomy-config.yaml) | Master switch (`enabled`), approval mode, limits |
| Reference implementation | [`.hi/autonomous/reference-implementation/README.md`](autonomous/reference-implementation/README.md) | Example runner and workflow |
| Worked example | [`.hi/autonomous/workflow-examples/feature-implementation.md`](autonomous/workflow-examples/feature-implementation.md) | End-to-end feature-implementation walkthrough |

### MCP Server

| Topic | File | Description |
|-------|------|-------------|
| MCP overview | [`.hi/mcp/README.md`](mcp/README.md) | Model Context Protocol server exposing the `.hi/` instruction system |
| Python server | [`.hi/mcp/python/hia_mcp/server.py`](mcp/python/hia_mcp/server.py) | Python MCP server implementation |
| Node server | [`.hi/mcp/node/server.mjs`](mcp/node/server.mjs) | Node MCP server twin |

### Plugins

| Topic | File | Description |
|-------|------|-------------|
| Plugins overview | [`.hi/plugins/README.md`](plugins/README.md) | Optional plugin system; discovery via `/hip-plugin-discover` |
| Model dispatch | [`.hi/plugins/model-dispatch/README.md`](plugins/model-dispatch/README.md) | Local/cloud LLM dispatch with tier strategy and adapters |
| Local-AI self-awareness | [`.hi/agents/tier-1/hia-router.agent.md`](agents/tier-1/hia-router.agent.md#local-ai-self-awareness) | Router detects local AI, proposes/self-implements a tier list (`suggest_tiers.py --apply`), and heals+notifies on tier loss (`plan_healing`); entry `/hip-route --models` |
| Tier-dispatch extension | [`.hi/extensions/hia-dispatch/README.md`](extensions/hia-dispatch/README.md) | VS Code extension: `@hia` chat participant routes simple work to a local LLM and lets the selected Copilot chat model take the reins; resolves tiers via `dispatcher.py resolve` (Option A) |

### Evals

| Topic | File | Description |
|-------|------|-------------|
| Evals overview | [`.hi/evals/README.md`](evals/README.md) | Evaluation harness for instruction resolution, naming gate, routing |
| Eval runner | [`.hi/evals/runner.py`](evals/runner.py) | Runs `.eval.yaml` cases |
| Eval schema | [`.hi/evals/schema.md`](evals/schema.md) | Eval case file format |

### Governance

| Topic | File | Description |
|-------|------|-------------|
| Governance overview | [`.hi/governance/README.md`](governance/README.md) | Project-level governance rules consumed by the Router |
| Example rule | [`.hi/governance/example-no-pii-in-logs.md`](governance/example-no-pii-in-logs.md) | Sample governance constraint |

### Stack Examples

| Topic | File | Description |
|-------|------|-------------|
| Stack examples overview | [`.hi/stack-examples/README.md`](stack-examples/README.md) | Per-stack adoption notes |
| Python / FastAPI | [`.hi/stack-examples/python-fastapi.md`](stack-examples/python-fastapi.md) | FastAPI adoption example |
| TypeScript / React | [`.hi/stack-examples/typescript-react.md`](stack-examples/typescript-react.md) | TS/React adoption example |
| Embedded C | [`.hi/stack-examples/embedded-c.md`](stack-examples/embedded-c.md) | Embedded C adoption example |

### Example Modules (Demonstration)

| Topic | File | Description |
|-------|------|-------------|
| Examples overview | [`.hi/examples/README.md`](examples/README.md) | Demonstration modules showing the system in practice |
| auth-api | [`.hi/examples/auth-api/.hi/instruct.md`](examples/auth-api/.hi/instruct.md) | Full TypeScript auth API with layered `.hi/` rules |
| data-layer | [`.hi/examples/data-layer/.hi/instruct.md`](examples/data-layer/.hi/instruct.md) | Data-layer example module |
| ui-component | [`.hi/examples/ui-component/.hi/instruct.md`](examples/ui-component/.hi/instruct.md) | UI-component example module |
| Scaffold template | [`.hi/example-module/.hi/instruct.md`](example-module/.hi/instruct.md) | Blank module scaffold to copy when creating a new module |

### Tooling & Scripts

| Topic | File | Description |
|-------|------|-------------|
| Scripts overview | [`.hi/scripts/README.md`](scripts/README.md) | Validator, hook installer, dev-specs cleaner |
| Instruction validator | [`.hi/scripts/validate-instructions.ps1`](scripts/validate-instructions.ps1) | Drift validator used by CI and `/hip-validate` |
| Frontmatter schemas | [`.hi/schemas/README.md`](schemas/README.md) | JSON schemas for agent/prompt YAML frontmatter |
| Debug utilities | [`.hi/debug/README.md`](debug/README.md) | Local debugging helpers (model load, dispatch test, import) |
| TODO registry | [`.hi/todo/README.md`](todo/README.md) | Curated TODO list location |

### Git Hooks

| Topic | File | Description |
|-------|------|-------------|
| Post-merge hook | [`.hi/hooks/post-merge`](hooks/post-merge) | Regenerates discovery registries after merge/checkout |
| Install (POSIX) | [`.hi/hooks/install-hooks.sh`](hooks/install-hooks.sh) | Sets `core.hooksPath = .hi/hooks` |
| Install (Windows) | [`.hi/hooks/install-hooks.ps1`](hooks/install-hooks.ps1) | Sets `core.hooksPath = .hi/hooks` |

### Deployment Modes

| Topic | File | Description |
|-------|------|-------------|
| Deployment convention | [`.hi/deployment/README.md`](deployment/README.md) | `DEPLOY_MODE`-keyed depth-priority scopes; required-section list per mode |
| Mode: dev-local | [`.hi/deployment/dev-local/.hi/instruct.md`](deployment/dev-local/.hi/instruct.md) | Local-only HTTP, fast setup |
| Mode: dev-lan | [`.hi/deployment/dev-lan/.hi/instruct.md`](deployment/dev-lan/.hi/instruct.md) | LAN-shared, self-signed HTTPS |
| Mode: prod-railway | [`.hi/deployment/prod-railway/.hi/instruct.md`](deployment/prod-railway/.hi/instruct.md) | Managed cloud, Railway-managed TLS |
| Mode: prod-self-serve | [`.hi/deployment/prod-self-serve/.hi/instruct.md`](deployment/prod-self-serve/.hi/instruct.md) | Self-hosted public, DDNS + Let's Encrypt |

### Project Specs

| Topic | File | Description |
|-------|------|-------------|
| Development & target platform | [`.hi/dev-specs.md`](../.hi/dev-specs.md) | Project mode, OS, shell, languages, frameworks, infra, testing |

### Conventions

| Topic | File | Description |
|-------|------|-------------|
| Directory & file naming | [`.hi/conventions.md`](conventions.md) | kebab-case directories; dot-prefix for archive dirs; file naming |
| AI instruction file naming | [`.hi/conventions.md`](conventions.md) | One instruction file type: `instruct.md` |
| `.dev-docs` convention | [`.hi/conventions.md`](conventions.md) | Dev-documentation subdirectory structure and rules |
| TOC requirement | [`.hi/conventions.md`](conventions.md) | Files with 5+ sections need a Contents table |
| Cross-reference convention | [`.hi/conventions.md`](conventions.md) | Exact format for referencing source-of-truth sections |
| No-duplication rule | [`.hi/conventions.md`](conventions.md) | Instructions live in exactly one place |
| Versioning | [`.hi/conventions.md`](conventions.md) | Semver, instruction dating, `Last Updated` auto-update |
| `.gitignore` decisions | [`.hi/conventions.md`](conventions.md) | What to commit vs. ignore; personal override pattern |

### Maintenance & Safety

| Topic | File | Description |
|-------|------|-------------|
| Never delete rule | [`.hi/maintenance.md`](maintenance.md) | Always archive instead of permanently deleting |
| Archive patterns | [`.hi/maintenance.md`](maintenance.md) | Archive into the `.archive/` of the item's parent folder; dated snapshots |
| Never reset databases | [`.hi/maintenance.md`](maintenance.md) | What requires explicit confirmation before running |
| Stale instruction files | [`.hi/maintenance.md`](maintenance.md) | How to deprecate outdated instruction files |
| What AI can do without asking | [`.hi/maintenance.md`](maintenance.md) | Pre-approved reversible actions vs. actions requiring confirmation |

### Credentials & Security

| Topic | File | Description |
|-------|------|-------------|
| Never commit credentials | [`.hi/credentials.md`](credentials.md) | Hard rule: no secrets in git, ever |
| `.env` file convention | [`.hi/credentials.md`](credentials.md) | Per-module `.env.example` (committed) + `.env` (gitignored) |
| `.gitignore` requirements | [`.hi/credentials.md`](credentials.md) | Mandatory gitignore patterns for all modules |
| Credential warehouse pattern | [`.hi/credentials.md`](credentials.md) | Where credentials live by environment |
| Rotating a leaked credential | [`.hi/credentials.md`](credentials.md) | Steps when a secret is accidentally committed |
| AI behavior rules | [`.hi/credentials.md`](credentials.md) | Never print secrets; always use env vars |

### Environment & Host Isolation

| Topic | File | Description |
|-------|------|-------------|
| Host-vs-container isolation | [`.hi/environment.md`](environment.md) | Never silently mutate the host; propose containment scaffolds |

---

## Root Pointer Files

| File | Purpose |
|------|---------|
| [`README.md`](../README.md) | Human-facing project overview |
| [`AGENTS.md`](../AGENTS.md) | AI-agent discovery anchor |
| [`CLAUDE.md`](../CLAUDE.md) | Claude Code pointer |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution guidelines |
| [`TEMPLATE-USAGE.md`](../TEMPLATE-USAGE.md) | How to adopt this template |
| [`setup.sh`](../setup.sh) / [`setup.ps1`](../setup.ps1) | One-shot setup: install hooks, scaffold `.env`, run validator |
