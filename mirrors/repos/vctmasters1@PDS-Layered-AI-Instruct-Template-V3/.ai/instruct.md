# [PROJECT_NAME] — Root AI Instructions (Template Scaffold)

**Scope**: Authoritative for the entire project (workspace root)
**Last Updated**: 2026-06-02

> This is the **root-level** `.ai/instruct.md` template scaffold. In this template repository, placeholders are intentional.
> After adoption, this file becomes authoritative for your project-wide concerns once `/ai-onboard` (or manual setup) fills the fields.
> Module-level `.ai/instruct.md` files are **more authoritative** than this file when working inside those directories.
> See `.github/copilot-instructions.md` for how the hierarchy works.

---

## Contents

| Section | What's here |
|---|-------------|
| [Project Overview](#project-overview) | What this project is and does |
| [Architecture Overview](#architecture-overview) | High-level structure and tech stack |
| [Routing & Orchestration Gateway](#routing--orchestration-gateway) | **Core feature**: How `/ai-route` powers all major workflows |
| [Key Directories](#key-directories) | Directory map with links to module .ai/ instructions |
| [Global Rules Reference](#global-rules-reference) | Links to canonical cross-cutting rules |
| [Governed Workflows — Import/Merge](#governed-workflows--importmerge) | **MANDATORY**: Import patterns and guardrails |
| [Coding Conventions & Validation](#coding-conventions--validation) | Element prefixes for test discovery |
| [API Endpoint Conventions](#api-endpoint-conventions) | Semantic endpoint naming for discovery |
| [Hybrid LLM Routing Strategy](#hybrid-llm-routing-strategy) | Local vs. frontier model tier selection for file generation |
| [AI-INSTRUCT Maintenance Rule](#ai-instruct-maintenance-rule) | When and how to update this system |

---

## Project Overview

> **Replace this section with your project description.**

**[PROJECT_NAME]** is a [one-sentence description of what the project does].

**Purpose**: [What problem does it solve? Who uses it?]

**Tech stack**:
- [e.g., TypeScript / Node.js / Express]
- [e.g., React / Vite / Tailwind]
- [e.g., PostgreSQL / TypeORM]
- [e.g., Docker / Railway]

**Primary language(s)**: [LANGUAGES]

**Environments**:
| Name | URL / Access | Notes |
|------|-------------|-------|
| Local dev | `localhost:[PORT]` | — |
| Staging | [URL] | — |
| Production | [URL] | — |

---

## Architecture Overview

> **Replace with your architecture diagram or description.**

```
[PROJECT_NAME]/
├── [module-a]/         ← [what it does — e.g., React frontend]
├── [module-b]/         ← [what it does — e.g., Express API + TypeORM]
├── [module-c]/         ← [what it does — e.g., shared DB entities]
└── [module-d]/         ← [what it does — e.g., firmware/device layer]
```

**Data flow**: [Describe how data moves through the system at a high level.]

**Key external dependencies**: [List critical third-party services: payment processors, email providers, cloud storage, etc.]

---

## Routing & Orchestration Gateway

**This is the core feature that powers all AI-assisted workflows in this project.**

Every major operation in this project — imports, validation, reflection, module creation, index updates — flows through the **routing gateway** (`/ai-route`). This ensures:

✅ **Scope awareness**: The deepest `.ai/instruct.md` for the affected path(s) is always authoritative  
✅ **Governance integration**: External rules and constraints are applied consistently  
✅ **Stage gating**: Pass/fail/block review points between phases  
✅ **Escalation**: Failures halt gracefully with guidance rather than proceeding blindly  
✅ **Audit trail**: Every routing decision is logged for transparency  

### How It Works

```
User invokes a major workflow (e.g., /ai-import-execute)
    ↓
Workflow recognizes the task and extracts parameters
    ↓
/ai-route (gateway) is called with task context
    ↓
Router resolves:
  • Which .ai/instruct.md is authoritative for the affected paths?
  • Are there governance rules (external constraints) to apply?
    ↓
Router delegates to the appropriate domain manager/supervisor
    ↓
Domain manager executes the full workflow with routing context
    ↓
Results passed back through the router for final validation
```

### Routed Workflows

All of these major workflows are **routed through `/ai-route`**:

| Workflow | Purpose | Domain Manager |
|----------|---------|-----------------|
| [`/ai-import-execute`](../.github/prompts/ai-import-execute.prompt.md) | Import/merge external projects (Phase 0-7 orchestration) | `pds-man-imports` |
| [`/ai-adapt-infrastructure`](../.github/prompts/ai-adapt-infrastructure.prompt.md) | Adapt imported prompts/agents/skills to routing paradigm | `pds-man-infrastructure` |
| [`/ai-validate`](../.github/prompts/ai-validate.prompt.md) | Scope-aware instruction & port validation | `pds-pipe-validator` |
| [`/ai-reflect`](../.github/prompts/ai-reflect.prompt.md) | Post-task reflection & instruction gap analysis | `pds-meta-learner` |
| [`/ai-update-index`](../.github/prompts/ai-update-index.prompt.md) | Rebuild `.ai/index.md` at scope level | `pds-man-curator` |
| [`/ai-new-module`](../.github/prompts/ai-new-module.prompt.md) | Create new module with hierarchy integration | `pds-pipe-scaffolder` |

### Using the Router

Invoke directly when you need to analyze a request before delegating:

```
/ai-route

Task: [description of what you're trying to do]
Scope: [affected paths, or "root"]
Context: [any governance or scope hints]
```

The router will:
1. Analyze the task
2. Resolve the target scope(s)
3. Check for applicable governance rules
4. Suggest the appropriate agent/manager
5. Either route the task or explain why it can't be routed

**→ [/ai-route prompt](../.github/prompts/ai-route.prompt.md)** — full router documentation  
**→ [pds-meta-router agent](../.github/agents/pds-meta-router.agent.md)** — technical details

---

| Directory | AI Instructions | Covers |
|-----------|-----------------|--------|
| Root | `.ai/instruct.md` (this file) | Project-wide rules and architecture |
| `.ai/` | (global shared files) | Cross-cutting rules: conventions, maintenance, credentials, index, agent-config |
| `.ai/engine/` | (runtime scripts) | Foresight engine + instruction resolver |
| `.ai/agents/tools/` | (MCP tool definitions) | Built-in governed tools with checklists |
| `.ai/mcp/tools/` | (project MCP tools) | Add project-specific tool definitions here |
| `.ai/foresight/` | (runtime output, gitignored) | Foresight analysis results |
| `.ai/knowledge/` | (runtime output, gitignored) | Accumulated knowledge base |
| `.ai/logs/` | (runtime output, gitignored) | Agent audit logs |
| `.ai/autonomous/` | [`.ai/autonomous/orchestrator.md`](autonomous/orchestrator.md) | **Opt-in autonomous layer — disabled by default.** See `autonomy-config.yaml`. |
| `[module-a]/` | `[module-a]/.ai/instruct.md` | [description] |
| `[module-b]/` | `[module-b]/.ai/instruct.md` | [description] |
| `.example-module/` | `.example-module/.ai/instruct.md` | Bare scaffold for a new module (reference) |
| `.examples/` | `.examples/README.md` | Filled-in module showcases: `auth-api`, `data-layer`, `ui-component` |
| `.github/` | `.github/copilot-instructions.md` | AI tooling meta-instructions |
| `.cursor/` | `.cursor/rules/project.mdc` | Pointer rules so Cursor reads the same `.ai/` hierarchy |
| `.deployment/` | `.deployment/<mode>/.ai/instruct.md` | Per-mode deployment scopes selected by `DEPLOY_MODE`; see [`.deployment/README.md`](../.deployment/README.md) |

> Add a row for every major directory that has its own `.ai/instruct.md`.

### Active deployment scope

When `DEPLOY_MODE` is set, the matching `.deployment/<mode>/.ai/instruct.md` is **authoritative** for deployment-relevant questions, layered above this root file by depth-priority. Inspect or switch with [`/ai-deploy-mode`](../.github/prompts/ai-deploy-mode.prompt.md). Drift is owned by the [`deployment-manager`](../.github/agents/pds-man-deployment.agent.md) agent.

---

## Global Rules Reference

These rules are canonical and live in `.ai/`. **Do not restate them here — only link.**

| Rule | Canonical location |
|------|-------------------|
| Naming & file organization | [`.ai/conventions.md`](conventions.md) |
| Archive / never-delete / never-reset-db | [`.ai/maintenance.md`](maintenance.md) |
| Credential warehousing & .gitignore | [`.ai/credentials.md`](credentials.md) |
| Agentic runtime config | [`.ai/agent-config.yaml`](agent-config.yaml) |
| Master index of all instruction sections | [`.ai/index.md`](index.md) |
| Element naming prefixes for test discovery (GUI + code) | [`.ai/coding-prefixes.md`](coding-prefixes.md) |
| API endpoint naming conventions | [`.ai/api-conventions.md`](api-conventions.md) |

---

## Governed Workflows — Import/Merge

**MANDATORY**: All project imports, clones, and merges are governed workflows. See [`copilot-instructions.md#governed-workflows--importmerge-pattern-guard`](../.github/copilot-instructions.md#governed-workflows--importmerge-pattern-guard) for the complete pattern-match guard.

**Recognition keywords** (any mention triggers the guard):
- "clone" + repo
- "import" + project
- "merge" / "consolidate" / "integrate" + projects
- "adopt" / "migrate" + codebase

**Do not** run ad-hoc `git clone`, `Move-Item`, or `cp` commands without `/ai-import-execute` orchestration.

---

## Coding Conventions & Validation

### Element Prefixes & Metadata-Driven Testing

This project uses **2-letter element prefixes** to enable automated test discovery and validation.

**Example:**
```jsx
// Buttons (bu_), toggles (tg_), inputs (in_) can be discovered and tested automatically
<button id="bu_submit" onClick={handleSubmit}>Submit</button>
<input id="in_email" type="email" />
<input id="tg_darkmode" type="checkbox" />
```

**Why?** Prefixes serve as metadata that allows the validation system to:
- Automatically discover all interactive elements
- Route elements to appropriate test strategies (existence, accessibility, functional, visual)
- Generate test reports indexed by element type
- Enable hierarchical per-module testing conventions

### How it Works

1. **Discovery phase** (`validation/discovery.py`):
   - Scans codebase for 2-letter prefixes: `bu_`, `tg_`, `in_`, etc.
   - Generates a JSON registry with element locations and types

2. **Testing phase** (`validation/test_facility.py`):
   - Reads registry and applies test strategies
   - Currently supports: **existence checks** (ready), **accessibility**, **functional**, **visual** (framework-specific stubs)

### Master Prefix Registry

→ **[Element Naming Prefixes](coding-prefixes.md)** — canonical table of all element types (buttons, toggles, inputs, modals, cards, etc.)

Quick reference:
- `bu_` = Button
- `tg_` = Toggle
- `in_` = Input field
- `md_` = Modal
- `cr_` = Card
- ... and 20+ more

### Running Validation

```bash
# Generate element IDs (central controller)
python validation/gui_element_id.py --type button --name "Submit Form"
# Output: bu_submit_form

# Discover all prefixed elements
python validation/discovery.py --scan-root ./src --output prefixes-found.json

# Run existence checks
python validation/test_facility.py --registry prefixes-found.json

# Run all test strategies
python validation/test_facility.py --registry prefixes-found.json --all --output results.json
```

→ **[GUI Element ID Generator](../validation/gui-element-id-guide.md)** — how to use the central controller for ID generation
→ **[Validation System Documentation](../validation/README.md)** — detailed setup, integration, and troubleshooting

### Hierarchical Prefix Definitions

- **Workspace root** (`.ai/coding-prefixes.md`): Master table; all projects inherit these
- **Module level** (`[module]/.ai/coding-prefixes.md`): Optional; extends or overrides workspace prefixes
  - Example: A payment module might add `py_` (payment form)
  - Example: A reporting module might add `rp_` (report widget)

---

## API Endpoint Conventions

Parallel to element prefixes, this project uses **semantic endpoint naming** to enable automated API discovery and testing.

### Pattern: `{resource}_{action}[_{detail}]`

Endpoints follow a consistent, searchable naming pattern:

```python
# FastAPI / Express examples:
user_list      → GET    /api/v1/users
user_create    → POST   /api/v1/users
user_detail    → GET    /api/v1/users/{id}
user_update    → PUT    /api/v1/users/{id}
product_search → GET    /api/v1/products/search
invoice_export_pdf → GET /api/v1/invoices/{id}/export.pdf
```

**Why?** Similar to UI elements:
- Automatically discoverable: grep all user endpoints, all list endpoints, etc.
- Consistent across the codebase
- Supports metadata extraction (HTTP methods, paths, parameters)
- Enables automated API documentation and testing

### Master Action Registry

→ **[API Endpoint Naming Conventions](api-conventions.md)** — canonical table of actions (list, create, detail, update, delete, search, export, import, batch, etc.)

### Running API Tools

```bash
# Generate endpoint name (central controller)
python api/endpoint_generator.py --resource user --action create
# Output: user_create (POST /api/v1/users)

# Discover all endpoints in code
python api/endpoint_discovery.py --scan-root ./src --output endpoints.json

# Validate endpoints
python api/endpoint_generator.py --validate user_create
python api/endpoint_generator.py --list-actions
```

→ **[API Endpoint Generator Guide](../api/endpoint-generator-guide.md)** — how to use the central controller
→ **[API System Documentation](../api/README.md)** — full setup and integration

### Hierarchical API Conventions

- **Workspace root** (`.ai/api-conventions.md`): Master table; all APIs inherit these
- **Module level** (`[module]/.ai/api-conventions.md`): Optional; extends or overrides workspace conventions
  - Example: A payments module might add `payment_refund` action
  - Example: A reporting module might add custom `report_generate` action

---

## Hybrid LLM Routing Strategy

**When**: Batch-generating governance files (README.md, .gitignore, .ai/instruct.md) across multiple modules

**Tier Selection**:

### Local LLM Tier
OpenAI-compatible models (e.g., coder-0 via LM Studio at localhost:1234/v1)

**Use for**:
- README.md templating (module overviews, architecture sections)
- .gitignore generation (credential patterns, build artifacts)
- .ai/instruct.md boilerplate (module scopes, governance links)
- Bulk file generation (parallel or serial)

**Config**:
- Temperature: 0.3 (deterministic output)
- Timeout: 180 seconds
- Tokens: 1024 per batch
- Fallback: Template generation if unavailable

**Validation** (Phase 2): 22 files generated, 100% success, zero timeouts

### Frontier Model Tier
GPT-4 / Claude (reserved for complex reasoning)

**Use for**:
- Security review (credential patterns compliance, sensitive data detection)
- Conflict resolution (naming collisions, schema conflicts across modules)
- Architecture validation (dependency analysis, coupling assessment)
- Policy exceptions (when local tier output violates governance)

**Implementation**: Phase 3+ enhancement

**Cost**: ~5-10s per task (frontier is slower but handles hard problems)

### Routing Logic

```python
if task_type in ["readme_md", "gitignore", "instruct_md"]:
    if complexity_estimate < 5:  # templating is low-complexity
        route_to = "local_llm"   # 1.5-2s, deterministic
    else:
        route_to = "frontier_llm" # 5-10s, reasoning-intensive
else:
    route_to = "manual_or_escalate"
```

→ **[Phase 2 Learnings](knowledge/phase2-learnings.md)** — metrics, patterns, optimization opportunities from hybrid routing validation

---

## AI-INSTRUCT Maintenance Rule

> **→ [AI-INSTRUCT Maintenance Rule](../.github/copilot-instructions.md#ai-instruct-maintenance-rule)** — update instruction files as part of every architectural change; run `/ai-update-index` after.
