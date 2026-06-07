# Index — Master Section Index

**Scope**: Project-wide
**Last Updated**: 2026-06-04

> This file is the **master index** of all instruction sections across all `.ai/instruct.md` files in the project.
> It enables fast lookup: find the authoritative source for any topic without reading every file.
>
> **Maintenance**: Update this file whenever any `.ai/instruct.md` is created, modified, or retired.
> Run `/ai-update-index` in Copilot Chat to rebuild automatically.
> In this template repository, some indexed files intentionally contain placeholders until `/ai-onboard` (or manual onboarding) fills project-specific values.

---

## How to Use

1. Search this index for keywords related to your topic
2. Follow the link to the exact file
3. Read that section — it is the **single source of truth**
4. Do not restate or copy the content elsewhere; cross-reference it

**If a topic is not in this index**, it has not been formally defined. Flag the gap and add it to the appropriate `.ai/instruct.md`, then rerun `/ai-update-index`.

> **Note on link granularity**: Entries in the tables below link to the **file**, not to the specific section anchor. This is intentional — section headings drift faster than file paths, so file-level links stay valid through more edits. Within each linked file, use the file's own Contents table to jump to the section.

---

## Index

### Meta & System

| Section | File | Description |
|---------|------|-------------|
| The Depth-Priority Hierarchical Paradigm | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | How the `.ai/` hierarchy works; deeper = more authoritative |
| Global Shared Instructions | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Purpose of the `.ai/` directory |
| Governed Workflows — Import/Merge | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | **MANDATORY** pattern guard for project imports; prevents ad-hoc cloning/copying |
| Workflow Invocation Pattern | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Workflows are repeatable, on-demand operations (not one-time setup); when to use them |
| AI Prompt Files | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Slash-command prompt files in `.github/prompts/`; `/ai-` prefix convention |
| `/ai-onboard` | [`.github/prompts/ai-onboard.prompt.md`](../.github/prompts/ai-onboard.prompt.md) | **Workflow:** Initialize or update project metadata. Run first to fill template placeholders, re-run to add modules or refresh identity. |
| `/ai-import-execute` | [`.github/prompts/ai-import-execute.prompt.md`](../.github/prompts/ai-import-execute.prompt.md) | **Workflow:** Import/merge external projects with complete Phase 0-6 orchestration. Mandatory for any import, clone, or merge operation. Prevents ad-hoc file copying. |
| `/ai-update-index` | [`.github/prompts/ai-update-index.prompt.md`](../.github/prompts/ai-update-index.prompt.md) | **Workflow:** Rebuilds `.ai/index.md` from every instruction file after edits. |
| `/ai-archive` | [`.github/prompts/ai-archive.prompt.md`](../.github/prompts/ai-archive.prompt.md) | **Workflow:** Safely archive a file or directory following the convention. |
| `/ai-new-module` | [`.github/prompts/ai-new-module.prompt.md`](../.github/prompts/ai-new-module.prompt.md) | **Workflow:** Scaffold a new module and register it. |
| `/ai-validate` | [`.github/prompts/ai-validate.prompt.md`](../.github/prompts/ai-validate.prompt.md) | **Utility:** Run the AI-INSTRUCT drift validator and report findings (no edits) |
| `/ai-env-check` | [`.github/prompts/ai-env-check.prompt.md`](../.github/prompts/ai-env-check.prompt.md) | **Utility:** Audit host-vs-container isolation state and recommend containment (no edits) |
| `/ai-git` | [`.github/prompts/ai-git.prompt.md`](../.github/prompts/ai-git.prompt.md) | **Utility:** Query git state (subcommands: `branch | commit | pr | status`). Read-only unless user explicitly asks for commits. |
| `/ai-foresight` | [`.github/prompts/ai-foresight.prompt.md`](../.github/prompts/ai-foresight.prompt.md) | **Utility:** Run foresight gap/risk analysis on current task before acting (read-only) |
| `/ai-reflect` | [`.github/prompts/ai-reflect.prompt.md`](../.github/prompts/ai-reflect.prompt.md) | **Utility:** Post-task reflection; identify instruction gaps and propose improvements (read-only) |
| `/ai-observe` | [`.github/prompts/ai-observe.prompt.md`](../.github/prompts/ai-observe.prompt.md) | **Utility:** Display runtime observability: metrics, logs, cheat sheets (read-only) |
| `/ai-route` | [`.github/prompts/ai-route.prompt.md`](../.github/prompts/ai-route.prompt.md) | Route a task through the generic agent triad: Router → Supervisor → workers |
| `/ai-audit-registries` | [`.github/prompts/ai-audit-registries.prompt.md`](../.github/prompts/ai-audit-registries.prompt.md) | Reconcile the five naming registries with the codebase via naming Mode 4, then hand off to curator/cleanup |
| `/ai-plugin-discover` | [`.github/prompts/ai-plugin-discover.prompt.md`](../.github/prompts/ai-plugin-discover.prompt.md) | Enumerate plugins under `.ai/plugins/`, summarise manifests, optionally run discovery scripts (read-only) |
| `/ai-ports-check` | [`.github/prompts/ai-ports-check.prompt.md`](../.github/prompts/ai-ports-check.prompt.md) | Validate port registry against project code; detect collisions, drift, range violations, unregistered services |
| `/ai-check-yourself` | [`.github/prompts/ai-check-yourself.prompt.md`](../.github/prompts/ai-check-yourself.prompt.md) | Audit AI instruction alignment; re-read rules, conventions, scope; reset to baseline if AI has drifted |
| `/ai-observe` | [`.github/prompts/ai-observe.prompt.md`](../.github/prompts/ai-observe.prompt.md) | Display runtime observability: metrics, logs, cheat sheets; understand what the framework learned |
| `/ai-autonomous-start` | [`.github/prompts/ai-autonomous-start.prompt.md`](../.github/prompts/ai-autonomous-start.prompt.md) | **Opt-in** — start a bounded autonomous run via the orchestrator. Refuses unless `.ai/autonomous/autonomy-config.yaml` is enabled. |
| Autonomous Layer | [`.ai/autonomous/orchestrator.md`](autonomous/orchestrator.md) | Lightweight, opt-in orchestration layer composing existing agents under hard limits and HITL gates. Disabled by default. |
| Autonomous Safety Guardrails | [`.ai/autonomous/safety-guardrails.md`](autonomous/safety-guardrails.md) | Stop conditions, forbidden actions, sanitisation rules, heartbeat behaviour for autonomous runs |
| Autonomous Task Queue | [`.ai/autonomous/task-queue.md`](autonomous/task-queue.md) | JSONL goal queue schema, status lifecycle, and write rules |
| Autonomous Config | [`.ai/autonomous/autonomy-config.yaml`](autonomous/autonomy-config.yaml) | Master switch, limits, allowed-agent palette, approval mode |
| Adoption Tiers | [`.ai/levels.md`](levels.md) | Graduated adoption path (T1 scoped instructions → T2 pipeline → T3 observable → T4 autonomous). Pick the lowest tier that solves a concrete pain. |
| Behavioral Evals | [`.ai/evals/README.md`](evals/README.md) | Declarative YAML evals + stdlib runner for forward-looking checks on agent behavior |
| Eval Schema | [`.ai/evals/schema.md`](evals/schema.md) | Field reference for `*.eval.yaml` files |
| Agent Runtime Convention | [`.ai/agents/runtime.md`](agents/runtime.md) | `runtime: chat-only \| subagent-safe` field; routes around the `runSubagent` tool-passthrough gap |
| MCP Server | [`.ai/mcp/README.md`](mcp/README.md) | Tool-neutral MCP server (Python + Node) exposing the depth-priority resolver and governed tools |
| Custom Agents | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Custom agent definitions in `.github/agents/` |
| Skills | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Domain knowledge skill packs in `.github/skills/` |
| Git Hooks | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Hook scripts in `.github/hooks/` and how to install them |
| Code Comment Convention | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Comment on why not what; no docblocks unless asked |
| AI-INSTRUCT Maintenance Rule | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Update instruction files as part of every architectural change; run `/ai-update-index` after |
| `.github/` File Placement Rules | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Where to put prompts, agents, debug scripts, tmp files; `.vscode/` for shared editor settings |
| Automatic Date Maintenance | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | AI auto-fills `Last Updated` and `[PLACEHOLDER]` values when context is unambiguous |
| Read Project Specs First | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | AI must read `.github/dev-specs.md` at session start before suggesting commands or paths |
| MCP Server Configuration | [`.vscode/mcp.json`](../.vscode/mcp.json) | Model Context Protocol servers that extend AI capabilities (commented templates) |
| PR Template | [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) | AI-INSTRUCT-aware PR checklist (instruction discipline, safety, credentials) |
| Issue Templates | [`.github/ISSUE_TEMPLATE/`](../.github/ISSUE_TEMPLATE/) | Bug, feature, and instruction-drift report templates with scope-aware fields |
| Code Owners | [`.github/CODEOWNERS`](../.github/CODEOWNERS) | Ownership map; replace `@OWNER` placeholders during onboarding |
| Suggested GitHub Topics | [`.github/topics.md`](../.github/topics.md) | Recommended repo topics for discoverability |
| Cursor Compatibility | [`.cursor/rules/project.mdc`](../.cursor/rules/project.mdc) | Pointer rule so Cursor reads the same `.ai/` hierarchy |
| One-shot Setup Scripts | [`setup.sh`](../setup.sh) / [`setup.ps1`](../setup.ps1) | Install hooks, scaffold `.env`, run validator |

### Agentic Runtime

| Section | File | Description |
|---------|------|-------------|
| Runtime Config | [`.ai/agent-config.yaml`](agent-config.yaml) | Central config: heartbeat, log format, safety levels, self-improvement, foresight toggles |
| Heartbeat Procedure | [`.ai/heartbeat.md`](heartbeat.md) | What agents do every 6 steps: reload scope, check alignment, log check |
| Foresight Engine | [`.ai/engine/foresight_engine.py`](engine/foresight_engine.py) | Gap detection + risk forecasting; appends results to `.ai/knowledge/anticipated-gaps.md` |
| Instruction Resolver | [`.ai/engine/get_effective_instructions.py`](engine/get_effective_instructions.py) | Depth-priority instruction merger — walks ancestors, deepest wins |
| Tool: anticipate-gaps | [`.ai/agents/tools/anticipate-gaps.json`](agents/tools/anticipate-gaps.json) | Governed checklist for proactive gap analysis |
| Tool: apply-safe-change | [`.ai/agents/tools/apply-safe-change.json`](agents/tools/apply-safe-change.json) | Safety protocol: approval gate, archive-first check, audit log |
| Tool: log-action | [`.ai/agents/tools/log-action.json`](agents/tools/log-action.json) | Emit a structured audit entry to `.ai/logs/` |
| Tool: pause-check | [`.ai/agents/tools/pause-check.json`](agents/tools/pause-check.json) | Kill-switch sentinel detector; runs first at every invocation and heartbeat; halts the agent if `.ai/PAUSE` exists |
| Tool: record-metric | [`.ai/agents/tools/record-metric.json`](agents/tools/record-metric.json) | Append-only structured metrics writer; every agent emits one line per invocation to `.ai/logs/metrics-*.jsonl`; feeds the observer |
| Tool: retrieve-knowledge | [`.ai/agents/tools/retrieve-knowledge.json`](agents/tools/retrieve-knowledge.json) | Pluggable retrieval over `.ai/knowledge/`, `.ai/instruct.md`, and registries; lexical now, embedding-ready |
| Engine: alignment auditor | [`.ai/engine/audit_alignment.py`](engine/audit_alignment.py) | Audit AI instruction alignment; loads effective scope, reads key files, generates rules refresh summary (used by /ai-check-yourself) |
| Tool: Schema (governed-tool) | [`.ai/agents/tools/_schema.json`](agents/tools/_schema.json) | JSON Schema every governed-tool file must satisfy; enforced by [`validate_tools.py`](engine/validate_tools.py) and CI |
| Engine: tool-schema validator | [`.ai/engine/validate_tools.py`](engine/validate_tools.py) | Validates every `.ai/**/tools/*.json` against `_schema.json` |
| Engine: self-tests | [`.ai/engine/tests/`](engine/tests/) | pytest suite for the resolver and tool-schema validator |
| Kill-switch sentinel | [`.ai/PAUSE.example`](PAUSE.example) | Rename to `.ai/PAUSE` to halt all agents in the workspace; CI refuses merge while present |
| Tool: reflect-and-improve | [`.ai/agents/tools/reflect-and-improve.json`](agents/tools/reflect-and-improve.json) | Post-task reflection; propose `.ai/` instruction improvements |
| Tool: run-heartbeat | [`.ai/agents/tools/run-heartbeat.json`](agents/tools/run-heartbeat.json) | Periodic alignment check at every heartbeat interval |
| Tool: generate-gui-component | [`.ai/agents/tools/generate-gui-component.json`](agents/tools/generate-gui-component.json) | Ordered checklist for generating UI components with prefixed element IDs |
| Tool: generate-api-endpoint | [`.ai/agents/tools/generate-api-endpoint.json`](agents/tools/generate-api-endpoint.json) | Ordered checklist for generating API endpoints with semantic naming |
| Tool: generate-database-schema | [`.ai/agents/tools/generate-database-schema.json`](agents/tools/generate-database-schema.json) | Ordered checklist for generating database migrations with naming conventions |
| Tool: generate-error-code | [`.ai/agents/tools/generate-error-code.json`](agents/tools/generate-error-code.json) | Ordered checklist for generating error codes with semantic naming |
| Tool: generate-config-var | [`.ai/agents/tools/generate-config-var.json`](agents/tools/generate-config-var.json) | Ordered checklist for generating typed config variables with validation |
| Tool: route-to-scope | [`.ai/agents/tools/route-to-scope.json`](agents/tools/route-to-scope.json) | Resolves authoritative `.ai/instruct.md` scope and governance refs for a request (Router) |
| Tool: delegate-task | [`.ai/agents/tools/delegate-task.json`](agents/tools/delegate-task.json) | Supervisor → worker hand-off with scope, governance, and prior-stage context |
| Tool: review-output | [`.ai/agents/tools/review-output.json`](agents/tools/review-output.json) | Stage gate between worker hand-offs (advance / retry / escalate) |
| Tool: get-governance-rules | [`.ai/agents/tools/get-governance-rules.json`](agents/tools/get-governance-rules.json) | Pluggable hook returning external policy/regulation rules (separate from depth-priority) |
| Tool: consult-naming | [`.ai/agents/tools/consult-naming.json`](agents/tools/consult-naming.json) | Mandatory consultation with the naming agent before any artifact is created or renamed |
| Tool: archive-file | [`.ai/agents/tools/archive-file.json`](agents/tools/archive-file.json) | Single safe entry point for archive-first file moves, mirroring the original path under `.archive/` |
| Tool: append-todo | [`.ai/agents/tools/append-todo.json`](agents/tools/append-todo.json) | Sanctioned write path into `.github/todo/`; deduplicates by title; never checks items off |
| Tool: capture-knowledge | [`.ai/agents/tools/capture-knowledge.json`](agents/tools/capture-knowledge.json) | Append-only writer for `.ai/knowledge/`; auto-files a curator-handoff TODO when proposing instruction changes |
| Agent: router | [`.github/agents/pds-meta-router.agent.md`](../.github/agents/pds-meta-router.agent.md) | Generic gateway: resolves scope and routes to next-hop agent |
| Agent: supervisor | [`.github/agents/pds-pipe-super.agent.md`](../.github/agents/pds-pipe-super.agent.md) | Generic domain supervisor: orchestrates worker pipeline within one scope |
| Agent: scaffolder | [`.github/agents/pds-pipe-scaffolder.agent.md`](../.github/agents/pds-pipe-scaffolder.agent.md) | Generic worker: produces structured plan only (no implementation) |
| Agent: generator | [`.github/agents/pds-pipe-generator.agent.md`](../.github/agents/pds-pipe-generator.agent.md) | Generic worker: implements an approved scaffold within scope conventions |
| Agent: validator | [`.github/agents/pds-pipe-validator.agent.md`](../.github/agents/pds-pipe-validator.agent.md) | Generic worker: enforces declared project conventions and governance (read-only) |
| Agent: tester | [`.github/agents/pds-pipe-tester.agent.md`](../.github/agents/pds-pipe-tester.agent.md) | Generic worker: writes tests after validation passes |
| Agent: reviewer | [`.github/agents/pds-pipe-reviewer.agent.md`](../.github/agents/pds-pipe-reviewer.agent.md) | Generic worker: final instruction-drift gate before finalize |
| Agent: curator | [`.github/agents/pds-man-curator.agent.md`](../.github/agents/pds-man-curator.agent.md) | Continuously syncs `.ai/instruct.md`, convention files, and `.ai/index.md` with reality |
| Agent: cleanup | [`.github/agents/pds-pipe-cleanup.agent.md`](../.github/agents/pds-pipe-cleanup.agent.md) | Detects orphaned/stale/superseded files; archives per never-delete rule (no auto-delete) |
| Agent: learner | [`.github/agents/pds-meta-learner.agent.md`](../.github/agents/pds-meta-learner.agent.md) | Distills completed tasks into `.ai/knowledge/`; proposes instruction edits via Curator |
| Agent: todo-manager | [`.github/agents/pds-man-todo.agent.md`](../.github/agents/pds-man-todo.agent.md) | Curates `.github/todo/` plus inline `TODO/FIXME`; deduplicates, ages, and archives |
| Agent: workflow-manager | [`.github/agents/pds-man-workflow.agent.md`](../.github/agents/pds-man-workflow.agent.md) | Reviews `.github/workflows/` CI YAML against recent code changes; proposes update/add/retire/rename |
| Agent: prompt-manager | [`.github/agents/pds-man-prompt.agent.md`](../.github/agents/pds-man-prompt.agent.md) | Reviews `.github/prompts/` slash commands against recent code changes; proposes update/add/retire/rename |
| Agent: deployment-manager | [`.github/agents/pds-man-deployment.agent.md`](../.github/agents/pds-man-deployment.agent.md) | Reviews `.deployment/<mode>/.ai/instruct.md` files against codebase reality; proposes update/add/retire/rename per deployment mode |
| Agent: environment-manager | [`.github/agents/pds-man-environment.agent.md`](../.github/agents/pds-man-environment.agent.md) | Pre-flight host-vs-containment guard; classifies any host-mutating command per [`.ai/environment.md`](environment.md), proposes containment scaffolds, never installs silently |
| Agent: plugin-compliance | [`.github/agents/pds-meta-compliance.agent.md`](../.github/agents/pds-meta-compliance.agent.md) | Read-only modularity reviewer; catches monolithic drift (oversized files, cyclic / private-symbol imports, plugin-contract bypass, leaky abstractions, duplication, god-file growth) and proposes refactors |
| Agent: observer | [`.github/agents/pds-meta-observer.agent.md`](../.github/agents/pds-meta-observer.agent.md) | Read-only observability aggregator; reads `.ai/logs/metrics-*.jsonl`, surfaces token spikes, budget exceedances, silent-approval misses, failure streaks, growth watchlist |
| Prompt: /ai-metrics | [`.github/prompts/ai-metrics.prompt.md`](../.github/prompts/ai-metrics.prompt.md) | Slash command: invoke observer over a window (default 24h); prints token/budget/approval/anomaly digest |
| Deployment Convention | [`.deployment/README.md`](../.deployment/README.md) | `DEPLOY_MODE`-keyed depth-priority scopes; required-section list for every mode |
| Deployment Mode: dev-local | [`.deployment/dev-local/.ai/instruct.md`](../.deployment/dev-local/.ai/instruct.md) | Local-only HTTP, < 2 min setup |
| Deployment Mode: dev-lan | [`.deployment/dev-lan/.ai/instruct.md`](../.deployment/dev-lan/.ai/instruct.md) | LAN-shared, self-signed HTTPS via Caddy |
| Deployment Mode: prod-railway | [`.deployment/prod-railway/.ai/instruct.md`](../.deployment/prod-railway/.ai/instruct.md) | Managed cloud, Railway-managed TLS |
| Deployment Mode: prod-self-serve | [`.deployment/prod-self-serve/.ai/instruct.md`](../.deployment/prod-self-serve/.ai/instruct.md) | Self-hosted public, DDNS + Let's Encrypt |
| Prompt: /ai-deploy-mode | [`.github/prompts/ai-deploy-mode.prompt.md`](../.github/prompts/ai-deploy-mode.prompt.md) | Inspect or switch the active `DEPLOY_MODE` scope (never mutates the shell) |
| Agent: naming | [`.github/agents/pds-man-naming.agent.md`](../.github/agents/pds-man-naming.agent.md) | Authoritative naming service: must be consulted before any artifact is created or renamed; owns the five naming registries (coding-prefixes / api-conventions / database-schema / error-codes / config-vars) |
| Agent: ports-manager | [`.github/agents/pds-man-ports.agent.md`](../.github/agents/pds-man-ports.agent.md) | Authoritative port registry curator: detects collisions, range violations, drift between `.ai/ports.md` and code; proposes registry updates |
| Governance Facility | [`.ai/governance/README.md`](governance/README.md) | Pluggable external-rule overlay; separate from depth-priority `.ai/instruct.md` |
| Governed Tool Definitions | [`.ai/agents/tools/`](agents/tools/) | Built-in governed tool checklists (not MCP wire-protocol tools) |
| Project Tool Definitions | [`.ai/mcp/tools/`](mcp/tools/) | Add project-specific governed tool checklists here |
| MCP Server (template-bundled) | [`.ai/mcp/README.md`](mcp/README.md) | stdio MCP server exposing governed tools + depth-priority resolver; Python primary, Node twin |
| MCP Server: Python | [`.ai/mcp/python/`](mcp/python/) | Primary implementation (`mcp` PyPI SDK); install with `pip install -e .` |
| MCP Server: Node | [`.ai/mcp/node/`](mcp/node/) | Twin implementation (`@modelcontextprotocol/sdk`); install with `npm install` |
| MCP Pointer (VS Code) | [`.vscode/mcp.json`](../.vscode/mcp.json) | Registers `pds-ai-instruct` with VS Code Copilot |
| MCP Pointer (Cursor) | [`.cursor/mcp.json`](../.cursor/mcp.json) | Registers `pds-ai-instruct` with Cursor |
| Foresight Outputs | `.ai/foresight/` | Runtime output; gitignored |
| Knowledge Base | [`.ai/knowledge/README.md`](knowledge/README.md) | Module-organized empirical learning (cheat sheets, patterns, antipatterns, risks) |
| Knowledge Cleanup Policy | [`.ai/knowledge/.cleanup-policy.md`](knowledge/.cleanup-policy.md) | Aging, deduplication, and archival rules for knowledge entries |
| Cheat Sheet Template | [`.ai/knowledge/cheat-sheets/.template.md`](knowledge/cheat-sheets/.template.md) | Template for module-specific quick reference guides |
| Foresight Observable Logs | [`.ai/engine/foresight_engine_observable.py`](engine/foresight_engine_observable.py) | Detect gaps and risks before acting; log to `.ai/logs/foresight-*.jsonl` |
| Memory Hygiene Tool | [`.ai/engine/memory_hygiene.py`](engine/memory_hygiene.py) | Deduplicate, age, and archive knowledge base entries |
| Metrics Dashboard | [`.ai/engine/show_metrics.py`](engine/show_metrics.py) | Aggregate observable logs; show patterns, risks, task breakdown |
| Knowledge Audit Logs | `.ai/logs/foresight-*.jsonl` | Structured foresight findings per task (gitignored runtime) |
| Foresight Outputs | `.ai/foresight/` | Runtime output; gitignored |
| Knowledge Base | `.ai/knowledge/` | Accumulated runtime knowledge; gitignored |
| Audit Logs | `.ai/logs/` | All agent change logs; gitignored |

### Project Specs

| Section | File | Description |
|---------|------|-------------|
| Development Platform | [`.github/dev-specs.md`](../.github/dev-specs.md) | Developer OS, shell, editor |
| Target Platform | [`.github/dev-specs.md`](../.github/dev-specs.md) | Where the code is deployed; path & line-ending convention |
| Language & Runtime | [`.github/dev-specs.md`](../.github/dev-specs.md) | Primary languages and versions |
| Frameworks & Libraries | [`.github/dev-specs.md`](../.github/dev-specs.md) | Frontend, backend, database, ORM |
| Package Manager | [`.github/dev-specs.md`](../.github/dev-specs.md) | Dependency management tooling |
| Infrastructure & DevOps | [`.github/dev-specs.md`](../.github/dev-specs.md) | Containers, CI/CD, cloud |
| Testing | [`.github/dev-specs.md`](../.github/dev-specs.md) | Test frameworks and strategy |
| Architecture Pattern | [`.github/dev-specs.md`](../.github/dev-specs.md) | Repo and system structure |
| Notes | [`.github/dev-specs.md`](../.github/dev-specs.md) | Free-form project context |

### Conventions

| Section | File | Description |
|---------|------|-------------|
| Directory Naming | [`.ai/conventions.md`](conventions.md) | kebab-case for all directories; dot-prefix for archive dirs |
| File Naming | [`.ai/conventions.md`](conventions.md) | Language-specific file naming; no spaces |
| Documentation Naming | [`.ai/conventions.md`](conventions.md) | Numbered kebab-case for user-facing guides |
| AI Instruction File Naming | [`.ai/conventions.md`](conventions.md) | Standard name for instruction files; one type: `instruct.md` |
| .dev-docs Convention | [`.ai/conventions.md`](conventions.md) | Dev documentation subdirectory structure and rules || Plugins Convention | [`.ai/conventions.md`](conventions.md) | Optional capability modules under `.ai/plugins/`; pointer to plugin contract |
| Plugin Contract | [`.ai/plugins/README.md`](plugins/README.md) | Manifest schema, lifecycle, discovery, depth-priority interaction |
| Reference Plugin: model-dispatch | [`.ai/plugins/model-dispatch/README.md`](plugins/model-dispatch/README.md) | Optional per-task model-tier routing; ships disabled || TOC Requirement | [`.ai/conventions.md`](conventions.md) | Files with 5+ sections must have a Contents table |
| Cross-Reference Convention | [`.ai/conventions.md`](conventions.md) | Exact format for referencing source-of-truth sections |
| No-Duplication Rule | [`.ai/conventions.md`](conventions.md) | Instructions live in exactly one place |
| Versioning | [`.ai/conventions.md`](conventions.md) | Semver, instruction file dating, Last Updated auto-update rule |
| Code Organization | [`.ai/conventions.md`](conventions.md) | Project-specific structure rules (fill in per project) |
| .gitignore Decisions | [`.ai/conventions.md`](conventions.md) | What to commit vs. ignore; personal override pattern |
| AI Enforcement | [`.ai/conventions.md`](conventions.md) | How AI handles naming and organization violations |
| Stack-Specific Conventions (TypeScript+React) | [`.ai/stack-examples/typescript-react.md`](stack-examples/typescript-react.md) | Reference Code Organization rules for TS/React projects |
| Stack-Specific Conventions (Python+FastAPI) | [`.ai/stack-examples/python-fastapi.md`](stack-examples/python-fastapi.md) | Reference Code Organization rules for FastAPI projects |
| Stack-Specific Conventions (Embedded C/C++) | [`.ai/stack-examples/embedded-c.md`](stack-examples/embedded-c.md) | Reference Code Organization rules for firmware projects |

### Maintenance & Safety

| Section | File | Description |
|---------|------|-------------|
| Never Delete Rule | [`.ai/maintenance.md`](maintenance.md) | Always archive instead of permanently deleting |
| Archive Patterns | [`.ai/maintenance.md`](maintenance.md) | Path-mirroring and `YYYYMMDD/` dated snapshots; `.old` for single files |
| Never Reset Databases | [`.ai/maintenance.md`](maintenance.md) | What requires explicit confirmation before running |
| Stale Instruction Files | [`.ai/maintenance.md`](maintenance.md) | How to deprecate outdated instruction files |
| What AI Can Do Without Asking | [`.ai/maintenance.md`](maintenance.md) | Pre-approved reversible actions vs. actions requiring confirmation |

### Credentials & Security

| Section | File | Description |
|---------|------|-------------|
| Never Commit Credentials | [`.ai/credentials.md`](credentials.md) | Hard rule: no secrets in git, ever |
| .env File Convention | [`.ai/credentials.md`](credentials.md) | Flat per-module: `.env.example` (committed) + `.env` (gitignored) at each directory root |
| .gitignore Requirements | [`.ai/credentials.md`](credentials.md) | Mandatory gitignore patterns for all modules |
| Credential Warehouse Pattern | [`.ai/credentials.md`](credentials.md) | Where credentials live by environment |
| Rotating a Leaked Credential | [`.ai/credentials.md`](credentials.md) | Steps when a secret is accidentally committed |
| AI Behavior Rules | [`.ai/credentials.md`](credentials.md) | How AI handles credentials — never print, always use env vars |

### Environment & Host Isolation
| Section | File | Description |
|---------|------|-------------|
| Why This Exists | [`.ai/environment.md`](environment.md) | The problem host-mutating AI causes for a template-driven workspace |
| The Core Rule | [`.ai/environment.md`](environment.md) | Detect-then-act: containment first, host last; never silently mutate the host |
| Environment Detection | [`.ai/environment.md`](environment.md) | How to tell whether you are on the host or inside a container/venv/WSL |
| Allowed vs. Restricted Operations | [`.ai/environment.md`](environment.md) | Matrix of which commands are free, ask-first, or refuse-first by context |
| Per-Stack Containment | [`.ai/environment.md`](environment.md) | TypeScript/Node, Python, C/C++ — preferred isolation per stack |
| Devcontainers & Docker | [`.ai/environment.md`](environment.md) | When to recommend, what to scaffold |
| AI Behavior Rules | [`.ai/environment.md`](environment.md) | What the AI must do, ask, or refuse for env-mutating commands |

### Governance Overlay (pluggable; empty by default)

| Section | File | Description |
|---------|------|-------------|
| What Governance Is (and Isn't) | [`.ai/governance/README.md`](governance/README.md) | Boundary against depth-priority `.ai/instruct.md` resolution |
| How the Resolver Works | [`.ai/governance/README.md`](governance/README.md) | Default file-based resolver and how to override for external systems |
| Rule File Format | [`.ai/governance/README.md`](governance/README.md) | Frontmatter schema for `.ai/governance/*.md` rule files |
| Example: No PII in Logs | [`.ai/governance/example-no-pii-in-logs.md`](governance/example-no-pii-in-logs.md) | Reference advisory rule showing the frontmatter schema in action; remove or replace during onboarding |

### Root Project

| Section | File | Description |
|---------|------|-------------|
| Project Overview | [`.ai/instruct.md`](instruct.md) | Template root authority scaffold; describes the adopted project's purpose |
| Architecture Overview | [`.ai/instruct.md`](instruct.md) | Template root architecture scaffold; filled during onboarding |
| Key Directories | [`.ai/instruct.md`](instruct.md) | Directory map with links to module .ai/ instructions |
| Global Rules Reference | [`.ai/instruct.md`](instruct.md) | Links to the canonical global rule files |
| Coding Conventions & Validation | [`.ai/instruct.md`](instruct.md) | Element prefixes for metadata-driven UI testing |
| API Endpoint Conventions | [`.ai/instruct.md`](instruct.md) | Semantic endpoint naming conventions for discovery |
| Element Naming Prefixes Registry | [`.ai/coding-prefixes.md`](coding-prefixes.md) | Master table of element prefixes — 33 GUI types and 6 code-element types (api/ev/mt/wk/fl/st), all 2-letter |
| API Endpoint Naming Conventions | [`.ai/api-conventions.md`](api-conventions.md) | Master table of 14 standard API actions and naming patterns |
| Database Schema Conventions | [`.ai/database-schema.md`](database-schema.md) | Master table of database naming: tables (tbl_), columns (col_), indices (idx_), migrations |
| Error Code Conventions | [`.ai/error-codes.md`](error-codes.md) | Master table of error codes (ERR_{DOMAIN}_{REASON}) with HTTP status mapping |
| Configuration Variables Registry | [`.ai/config-vars.md`](config-vars.md) | Master table of typed config variables ({MODULE}_{RESOURCE}_{PROPERTY}) with validation |
| Team Version Control & Merge Governance | [`.ai/version-control.md`](version-control.md) | Branch strategies (GitHub Flow, Git Flow, Trunk-Based), scope locking, merge validation gates, registry merge strategy, conflict resolution |

### Port Configuration

| Section | File | Description |
|---------|------|-------------|
| Port Registry | [`.ai/ports.md`](ports.md) | Master list of all service ports; single source of truth for dev, test, and prod |
| Port Allocation Guidelines | [`.ai/ports.md`](ports.md) | Reserved port ranges to prevent collisions (APIs: 3000–3099, cache: 5100–5199, etc.) |
| Port Validator Engine | [`.ai/engine/port_validator.py`](engine/port_validator.py) | Scans project for hardcoded ports; compares against registry; detects collisions, drift, range violations |
| Port Manager Agent | [`.github/agents/pds-man-ports.agent.md`](../.github/agents/pds-man-ports.agent.md) | Automated drift detection and registry update proposals; never modifies source code |
| Slash Command: /ai-ports-check | [`.github/prompts/ai-ports-check.prompt.md`](../.github/prompts/ai-ports-check.prompt.md) | On-demand validation; shows findings in human-readable format; exports JSON |

### Knowledge Base & Observable Runtime

| Section | File | Description |
|---------|------|-------------|
| Knowledge Base Overview | [`.ai/knowledge/README.md`](knowledge/README.md) | Module-organized empirical learning system (cheat sheets, patterns, antipatterns, risks; separate from normative rules) |
| Phase 2 Learning Capture | [`.ai/knowledge/phase2-learnings.md`](knowledge/phase2-learnings.md) | Phase 2 execution metrics, hybrid LLM routing validation, optimization opportunities |
| Knowledge Cleanup Policy | [`.ai/knowledge/.cleanup-policy.md`](knowledge/.cleanup-policy.md) | Aging (180d), deduplication, and archival rules for knowledge entries |
| Cheat Sheet Template | [`.ai/knowledge/cheat-sheets/.template.md`](knowledge/cheat-sheets/.template.md) | Template for module-specific quick reference guides (not instructions; rather shortcuts + experience) |
| Observable Foresight Engine | [`.ai/engine/foresight_engine_observable.py`](engine/foresight_engine_observable.py) | Detect anticipated gaps and risks before acting; log findings to `.ai/logs/foresight-*.jsonl` |
| Memory Hygiene Tool | [`.ai/engine/memory_hygiene.py`](engine/memory_hygiene.py) | Deduplicate, age, and suggest archival of knowledge entries; maintains KB hygiene |
| Metrics Dashboard | [`.ai/engine/show_metrics.py`](engine/show_metrics.py) | Aggregate and visualize observable logs; show patterns, anomalies, task breakdown |
| Knowledge Logs | `.ai/logs/foresight-*.jsonl` | Structured foresight findings per task (runtime; gitignored) |

### Module: gui

| Section | File | Description |
|---------|------|-------------|
| Module Overview | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | Purpose of GUI module; interactive, testable, discoverable UI components |
| Code Generation Rules | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | Mandatory procedures for UI component creation with prefixed element IDs |
| Element Naming Convention | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | 2-letter prefix system for test discovery and automation |
| Integration with Central Controller | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | How to use `validation/gui_element_id.py` central generator |
| Validation & Discovery | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | Automated testing pipeline for UI elements |
| Common Patterns | [`gui/.ai/instruct.md`](../gui/.ai/instruct.md) | Example implementations (React, Vue, Angular, HTML) |
| Governed Tool | [`.ai/agents/tools/generate-gui-component.json`](../.ai/agents/tools/generate-gui-component.json) | Checklist for generating UI components |

### Module: api

| Section | File | Description |
|---------|------|-------------|
| Module Overview | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | Purpose of API module; consistent, discoverable, testable endpoints |
| Code Generation Rules | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | Mandatory procedures for endpoint creation with semantic naming |
| Endpoint Naming Convention | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | `{resource}_{action}[_{detail}]` pattern for discoverability |
| Integration with Central Generator | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | How to use `api/endpoint_generator.py` central generator |
| Discovery & Validation | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | Automated endpoint analysis pipeline |
| Common Patterns | [`api/.ai/instruct.md`](../api/.ai/instruct.md) | Example implementations (Express, FastAPI, Django) |
| Governed Tool | [`.ai/agents/tools/generate-api-endpoint.json`](../.ai/agents/tools/generate-api-endpoint.json) | Checklist for generating API endpoints |

### Module: .example-module

| Section | File | Description |
|---------|------|-------------|
| Module Overview | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | What .example-module does and its responsibilities |
| Subdirectory Rules | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | Rules specific to this module |
| Global Rules Reference | [`.example-module/.ai/instruct.md`](../.example-module/.ai/instruct.md) | Cross-references to global rules |

### Example Showcase: .examples/

| Section | File | Description |
|---------|------|-------------|
| Showcase Overview | [`.examples/README.md`](../.examples/README.md) | What the filled-in examples demonstrate and how to use them |
| Module: auth-api | [`.examples/auth-api/.ai/instruct.md`](../.examples/auth-api/.ai/instruct.md) | Express+JWT+Postgres: layering, security, testing rules |
| Module: auth-api Before/After | [`.examples/auth-api/before-after.md`](../.examples/auth-api/before-after.md) | Side-by-side of AI behavior with/without module rules |
| Module: data-layer | [`.examples/data-layer/.ai/instruct.md`](../.examples/data-layer/.ai/instruct.md) | TypeORM entity, repository, migration discipline |
| Module: data-layer Before/After | [`.examples/data-layer/before-after.md`](../.examples/data-layer/before-after.md) | Side-by-side of AI behavior with/without module rules |
| Module: ui-component | [`.examples/ui-component/.ai/instruct.md`](../.examples/ui-component/.ai/instruct.md) | React+Tailwind component library rules |
| Module: ui-component Before/After | [`.examples/ui-component/before-after.md`](../.examples/ui-component/before-after.md) | Side-by-side of AI behavior with/without module rules |

---

## Rebuilding This Index

Run `/ai-update-index` in Copilot Chat to scan all instruction files and regenerate the tables above.

Manual process:
1. Find all instruction files: `file_search` for `**/.ai/instruct.md` and `.ai/*.md`
2. Exclude `.dev-docs/.old/`, `.archive/`
3. For each file, extract all `##` headings
4. Group by file, add a one-line description inferred from the section content
5. Update the tables above and the "Last Updated" date

**Do not alter** the "How to Use" or "Rebuilding This Index" sections during a rebuild.
