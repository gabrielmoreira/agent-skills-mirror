# Documentation Orchestration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Good documentation is parallel-friendly.                  │
│   Multiple sections, generated simultaneously.              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Load when**: API documentation, code documentation, README generation, architecture docs, user guides
> **Common patterns**: Endpoint Discovery, Batch JSDoc Generation, Comprehensive README

## Table of Contents

1. [API Documentation](#api-documentation)
2. [Code Documentation](#code-documentation)
3. [README Generation](#readme-generation)
4. [Architecture Documentation](#architecture-documentation)
5. [User Guides](#user-guides)

---

## API Documentation

### Pattern: Endpoint Discovery and Documentation

```
User Request: "Document all REST API endpoints"

Phase 1: EXPLORE
└─ Explore agent: Find all route definitions

Phase 2: FAN-OUT (Parallel documentation by domain)
├─ Agent A: Document auth endpoints
├─ Agent B: Document user endpoints
├─ Agent C: Document product endpoints
└─ Agent D: Document order endpoints

Phase 3: REDUCE
└─ General-purpose agent: Compile into unified OpenAPI/Swagger spec
```

### Pattern: Interactive Documentation

```
Phase 1: PIPELINE (Foundation)
├─ Explore agent: Extract all endpoints with types
└─ General-purpose agent: Generate OpenAPI spec

Phase 2: FAN-OUT (Enhancement)
├─ Agent A: Add example requests
├─ Agent B: Add example responses
└─ Agent C: Add authentication examples

Phase 3: PIPELINE
└─ General-purpose agent: Setup Swagger UI / Redoc
```

---

## Code Documentation

### Pattern: Batch JSDoc/Docstring Generation

```
User Request: "Add documentation to the utils module"

Phase 1: EXPLORE
└─ Explore agent: Find all undocumented functions

Phase 2: MAP (Parallel documentation)
├─ Agent A: Document file1.ts functions
├─ Agent B: Document file2.ts functions
└─ Agent C: Document file3.ts functions

Phase 3: PIPELINE
└─ General-purpose agent: Verify consistency, generate type docs
```

### Pattern: Module Overview Generation

```
Phase 1: EXPLORE
└─ Explore agent: Map module structure, exports, dependencies

Phase 2: PIPELINE
├─ General-purpose agent: Write module overview
├─ General-purpose agent: Document public API
└─ General-purpose agent: Add usage examples
```

---

## README Generation

### Pattern: Comprehensive README

```
User Request: "Create a README for this project"

Phase 1: FAN-OUT (Parallel information gathering)
├─ Explore agent: Project structure and technologies
├─ Explore agent: Build and run scripts (package.json, Makefile)
├─ Explore agent: Environment variables and config
├─ Explore agent: Test setup and commands
└─ Explore agent: Existing docs and comments

Phase 2: REDUCE
└─ General-purpose agent: Synthesize into structured README

Sections:
- Overview and purpose
- Quick start
- Installation
- Configuration
- Usage examples
- Development setup
- Testing
- Contributing
```

---

## Architecture Documentation

### Pattern: C4 Model Documentation

```
User Request: "Document the system architecture"

Phase 1: FAN-OUT (Parallel level documentation)
├─ Agent A: Context diagram (system + external actors)
├─ Agent B: Container diagram (applications, data stores)
├─ Agent C: Component diagram (internal components)
└─ Agent D: Code diagram (critical classes/modules)

Phase 2: REDUCE
└─ General-purpose agent: Compile into architecture doc with diagrams
```

### Pattern: Decision Record Generation

```
Phase 1: EXPLORE
└─ Explore agent: Find architectural patterns in code

Phase 2: FAN-OUT
├─ Agent A: Document decision 1 (why this database?)
├─ Agent B: Document decision 2 (why this framework?)
└─ Agent C: Document decision 3 (why this structure?)

Each ADR includes:
- Context
- Decision
- Consequences
- Alternatives considered
```

---

## User Guides

### Pattern: Feature-Based Guides

```
User Request: "Write user documentation for the dashboard"

Phase 1: EXPLORE
└─ Explore agent: Map dashboard features and capabilities

Phase 2: FAN-OUT (Parallel feature guides)
├─ Agent A: Guide for feature 1 (with screenshots)
├─ Agent B: Guide for feature 2
├─ Agent C: Guide for feature 3
└─ Agent D: Troubleshooting guide

Phase 3: REDUCE
└─ General-purpose agent: Compile into user manual with TOC
```

---

## Task Management for Documentation

Structure documentation work with parallel generation:

```bash
# Create documentation tasks
npx cc-mirror tasks create --subject "Audit existing docs" --description "Review current documentation state..."
npx cc-mirror tasks create --subject "Document API endpoints" --description "REST API documentation..."
npx cc-mirror tasks create --subject "Document components" --description "React component docs..."
npx cc-mirror tasks create --subject "Document utilities" --description "Helper function docs..."
npx cc-mirror tasks create --subject "Review consistency" --description "Ensure consistent style..."
npx cc-mirror tasks create --subject "Verify examples" --description "Test all code examples..."

# Parallel doc generation after audit
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 1
npx cc-mirror tasks update 4 --add-blocked-by 1
npx cc-mirror tasks update 5 --add-blocked-by 2,3,4
npx cc-mirror tasks update 6 --add-blocked-by 5
```

```python
# Spawn parallel documentation agents (sonnet for well-structured work)
Task(subagent_type="general-purpose", prompt="Task 2: Document API endpoints...",
     model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Task 3: Document components...",
     model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Task 4: Document utilities...",
     model="sonnet", run_in_background=True)
```

## Output Formats

| Doc Type     | Format              | Tool                   |
| ------------ | ------------------- | ---------------------- |
| API docs     | OpenAPI/Swagger     | YAML/JSON              |
| Code docs    | JSDoc/docstrings    | Inline                 |
| READMEs      | Markdown            | .md files              |
| Architecture | Markdown + diagrams | Mermaid/PlantUML       |
| User guides  | Markdown/HTML       | Static site generators |

---

```
─── ◈ Documentation ─────────────────────
```
