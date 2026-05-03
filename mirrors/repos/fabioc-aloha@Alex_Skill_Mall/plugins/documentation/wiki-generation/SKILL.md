---
type: skill
lifecycle: stable
inheritance: inheritable
name: wiki-generation
description: Generate structured documentation from codebases — architecture mapping, page writing, and onboarding guides. Use when asked to create a wiki, document a repo, generate onboarding docs, map architecture for documentation, or produce a documentation plan from source code.
tier: standard
applyTo: '**/*wiki*,**/*generation*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Wiki Generation

Generate structured technical documentation from codebases. Three integrated capabilities: architecture mapping (plan the wiki), page writing (produce the content), and onboarding generation (new-contributor guides).

## When to Use

- User asks to "create a wiki", "document this repo", "generate docs"
- User wants onboarding documentation for new team members
- User needs a documentation plan or structure for an existing codebase
- User wants comprehensive technical deep-dives with source citations

## When NOT to Use

- Writing a single API reference (use `api-documentation`)
- Fixing existing documentation (use `doc-hygiene`)
- Creating diagrams only (use `markdown-mermaid`)

---

## Capability 1: Architecture Mapping

Generate a hierarchical documentation structure by analyzing the codebase.

### Procedure

1. **Scan** the repository file tree, README, and build files
2. **Detect** project type, languages, frameworks, architectural patterns
3. **Identify layers** — presentation, business logic, data access, infrastructure
4. **Generate catalogue** — hierarchical structure with section titles, scope, and source file references

### Output: Documentation Catalogue

```markdown
## Documentation Structure

### Getting Started
- Overview (README + architecture summary)
- Setup (build files, env requirements)
- Quick Reference (key commands, endpoints)

### Architecture
- System Overview (layer diagram, component map)
- [Component A] (per major module)
- [Component B]
- Data Flow (how data moves through the system)

### Onboarding
- Principal-Level Guide (architectural deep-dive)
- Zero-to-Hero Guide (contributor walkthrough)
```

### Constraints

- Max nesting depth: 4 levels
- Max 8 children per section
- Small repos (≤10 files): Getting Started only, skip Deep Dive
- Every section must reference specific source files
- Derive all titles from actual repository content — never use generic placeholders

---

## Capability 2: Page Writing

Generate rich technical documentation pages with source citations and diagrams.

### Depth Requirements (Non-Negotiable)

1. **Trace actual code paths** — do not guess from file names; read the implementation
2. **Every claim needs a source** — file path + function/class name
3. **Distinguish fact from inference** — if you read the code, say so; if inferring, mark it
4. **First principles** — explain WHY something exists before WHAT it does
5. **No hand-waving** — don't say "this likely handles..." — read the code or say "Unknown"

### Page Structure

```markdown
# [Component/Feature Name]

## Overview
Why this exists. What problem it solves. (1-2 paragraphs)

## Architecture
Mermaid diagram showing component relationships.

## Key Abstractions
The load-bearing interfaces and types.

## Data Flow
How data moves through this component (sequence diagram).

## Implementation Details
Non-obvious behaviors, algorithms, edge cases.
(Cite: `path/to/file.ts:functionName`)

## Error Handling
What can go wrong and how the system responds.

## References
- Source files cited in this page
- Related documentation
```

### Rules

- Minimum 2 Mermaid diagrams per page (architecture + flow)
- Minimum 5 different source files cited per page
- If evidence is missing: mark as `(Unknown — verify in path/to/check)`
- Use Markdown tables for APIs, configs, and component summaries

---

## Capability 3: Onboarding Generation

Generate two complementary onboarding documents for any codebase.

### Guide A: Principal-Level (Senior Engineers)

**Audience**: Staff+ engineers who need the "why" behind decisions.

Required sections:

1. **System Philosophy** — design principles, invariants, key choices
2. **Architecture Overview** — component map with Mermaid diagram
3. **Key Abstractions** — load-bearing interfaces everything depends on
4. **Decision Log** — major architectural decisions with context and trade-offs
5. **Dependency Rationale** — why each major dependency was chosen
6. **Data Flow** — how data moves (traced from code, not guessed)
7. **Failure Modes** — what breaks, how errors propagate, recovery patterns
8. **Performance Characteristics** — bottlenecks, hot paths, scaling limits
9. **Security Model** — auth, trust boundaries, data sensitivity
10. **Testing Strategy** — what's tested, what isn't, testing philosophy
11. **Known Technical Debt** — honest assessment of shortcuts and risks

### Guide B: Zero-to-Hero (New Contributors)

**Audience**: New contributors who need step-by-step practical guidance.

Required sections:

1. **What This Project Does** — 2-3 sentence elevator pitch
2. **Prerequisites** — tools, versions, accounts needed
3. **Environment Setup** — step-by-step with exact commands and expected output
4. **Project Structure** — annotated directory tree (what lives where and why)
5. **Your First Task** — end-to-end walkthrough of adding a simple feature
6. **Development Workflow** — branch strategy, commit conventions, PR process
7. **Running Tests** — how to run, what to test, how to add a test
8. **Debugging Guide** — common issues and how to diagnose them
9. **Code Patterns** — "If you want to add X, follow this pattern" templates
10. **Common Pitfalls** — mistakes every new contributor makes
11. **Glossary** — terms used in the codebase that aren't obvious
12. **Quick Reference Card** — cheat sheet of most-used commands and patterns

### Rules for Both Guides

- Every claim backed by `(file_path:line_number)` citation
- All code examples in the detected primary language
- Every setup command must be copy-pasteable with expected output
- Include Mermaid diagrams for architecture and workflow

---

## Language Detection

Scan repository for build files to determine primary language:

| Build File | Language |
| ---------- | -------- |
| `package.json` / `tsconfig.json` | TypeScript/JavaScript |
| `*.csproj` / `*.sln` | C# / .NET |
| `Cargo.toml` | Rust |
| `pyproject.toml` / `setup.py` | Python |
| `go.mod` | Go |
| `pom.xml` / `build.gradle` | Java |

Use the primary language for all code examples. When explaining complex patterns, optionally include a comparison in a familiar language.

---

## Error Handling

| Scenario | Action |
| -------- | ------ |
| Repository has no README | Generate catalogue from file structure alone |
| Language detection fails | Default to most common language by file count |
| Repo has fewer than 3 files | Produce minimal single-section documentation |
| Build/setup commands unclear | Mark with "verify" annotations |
| Cited file paths cannot be verified | Mark as `(Unknown — verify in path/to/check)` |
| Insufficient source files (<5) | Cite what's available and note the gap |

---

## Example Workflow

**User**: "Create wiki documentation for this project"

1. **Architecture Mapping** → scan repo, produce documentation catalogue
2. **User confirms** structure (or adjusts)
3. **Page Writing** → generate each section with citations and diagrams
4. **Onboarding** → produce Principal-Level and Zero-to-Hero guides

**Output**: Complete documentation set grounded in actual source code, not assumptions.
