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
| [Key Directories](#key-directories) | Directory map with links to module .ai/ instructions |
| [Global Rules Reference](#global-rules-reference) | Links to canonical cross-cutting rules |
| [Coding Conventions & Validation](#coding-conventions--validation) | Element prefixes for test discovery |
| [API Endpoint Conventions](#api-endpoint-conventions) | Semantic endpoint naming for discovery |
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

## Key Directories

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

## AI-INSTRUCT Maintenance Rule

> **→ [AI-INSTRUCT Maintenance Rule](../.github/copilot-instructions.md#ai-instruct-maintenance-rule)** — update instruction files as part of every architectural change; run `/ai-update-index` after.
