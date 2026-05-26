---
name: generate-readme
description: "Generate a README.md file based on an existing implementation. Use when: writing a README, documenting a feature, create README from code, generate docs from implementation, document a project or folder."
argument-hint: "Path to the folder or implementation file to document (e.g. my-feature/ or my-feature/index.ts)"
---

# Generate README from Implementation

## When to Use

Invoke this skill when the user says:
- "generate a README for this"
- "create a README based on the implementation"
- "document this feature / module / project"
- "write a README for [folder]"
- "generate docs from the code"

## Procedure

### Step 1 — Locate the Implementation

1. Identify the **target scope**: a folder, a single file, or the entire workspace root.
2. List all files in the target scope (recursively if a folder).
3. Read the key source files — entry points, main modules, config files, and any existing partial docs.
4. If a `TASKS.md` or `PLAN.md` exists in the same folder, read it for context on intent and scope.

### Step 2 — Extract Key Information

While reading the code, collect the following details:

| Category | What to look for |
|----------|-----------------|
| **Purpose** | What problem does this solve? What is the main feature/module? |
| **Inputs / Outputs** | CLI args, function params, API endpoints, events consumed/produced |
| **Configuration** | Environment variables, config files, feature flags |
| **Dependencies** | External packages, services, or APIs relied upon |
| **Usage examples** | Invocation patterns, code snippets, sample commands |
| **Folder structure** | Notable sub-folders and their roles |
| **Setup / Installation** | Build steps, install commands, prerequisites |
| **Limitations / Notes** | Known edge cases, TODOs, constraints |

### Step 3 — Ask Clarifying Questions

Before writing, ask the user about anything that cannot be reliably inferred from the code:

- Target audience (internal devs, open-source contributors, end users)?
- Should usage examples be included? If so, in what language/format?
- Is there a specific README template or style guide to follow?
- Any sections to include or explicitly omit?
- License to include?

If all details are clear from the code and context, state: "The implementation is clear — no questions. Proceeding to generate README."

**Wait for the user's answers before writing the file.**

### Step 4 — Write README.md

Create (or overwrite) `README.md` **in the same folder as the target implementation**, using the structure below. Omit any section where the information genuinely does not apply.

```markdown
# <Project / Feature Name>

> <One-line description of what this does and why it exists.>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Folder Structure](#folder-structure)
- [API / Interface Reference](#api--interface-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

<2-4 sentences explaining the problem this solves and the approach taken.>

## Features

- <Feature 1>
- <Feature 2>
- ...

## Prerequisites

- <Runtime / tool with minimum version>
- <Any required service or credential>

## Installation

```bash
# Example install commands derived from package.json / Makefile / etc.
npm install
```

## Usage

```bash
# Primary invocation / entry-point command
```

<Short explanation of the happy-path workflow.>

## Configuration

| Variable / Key | Default | Description |
|----------------|---------|-------------|
| `ENV_VAR_NAME` | `value` | What it controls |

## Folder Structure

```
<root>/
├── src/           # Source files
├── tests/         # Test suites
└── ...
```

## API / Interface Reference

### `functionOrEndpointName(param: Type): ReturnType`

<Description, param table, return value, example call.>

## Examples

```<language>
// Concrete usage example
```

## Contributing

<How to run tests, lint, and submit changes.>

## License

<License name and link, or "Internal use only.">
```

### Step 5 — Validate & Report

1. Re-read the generated `README.md` and verify:
   - Every section references only real, confirmed details from the code.
   - No placeholder text (e.g., `<Your text here>`) remains unfilled.
   - Code blocks use the correct language tag.
   - Markdown renders cleanly (no broken links, no orphan headings).
2. If any section is still unknown, either omit it or add a `<!-- TODO: ... -->` comment with a clear note.
3. Report to the user: list every section that was written, and any that were skipped and why.
