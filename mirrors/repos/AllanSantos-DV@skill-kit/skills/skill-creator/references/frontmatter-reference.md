# Frontmatter Fields — Complete Reference

This document provides detailed guidance on every SKILL.md frontmatter field, including edge cases and advanced usage.

## `name` (required)

- **Type:** string
- **Format:** kebab-case, lowercase, no spaces
- **Constraint:** Must match the folder name exactly
- **Examples:** `react-testing`, `docker-compose`, `git-workflow`

```yaml
name: react-testing
```

**Common mistake:** Using camelCase or spaces. The name is used as an identifier in file paths and commands — stick to kebab-case.

## `description` (required)

- **Type:** string
- **Max recommended length:** 300 characters
- **Purpose:** Primary discovery mechanism. The agent reads this to decide relevance.

### Patterns by Skill Type

**Workflow skill** (guides a process):
```yaml
description: "**WORKFLOW SKILL** — Create and manage Docker containers. USE FOR: scaffolding compose files, debugging container issues, optimizing images. DO NOT USE FOR: Kubernetes, container orchestration at scale."
```

**Knowledge skill** (provides reference):
```yaml
description: "PostgreSQL administration covering backup strategies, replication setup, performance tuning, and query optimization. Includes command reference and config examples."
```

**Tool skill** (teaches a specific tool):
```yaml
description: "How to use the Skill Manager for Copilot extension — install, configure, sync and manage skills"
```

### Description Anti-Patterns

| Bad | Why | Better |
|-----|-----|--------|
| "A skill about React" | Too vague, no action verbs | "React component testing with RTL and Jest — create, debug, and optimize test suites" |
| "This skill helps with..." | Wastes characters on filler | Start directly with the topic |
| 500+ char description | Gets truncated, loses signal | Dense 200-char version |

## `argument-hint`

- **Type:** string
- **Purpose:** Shown to users when they type `/skill-name` — guides what to type next
- **When to use:** When the skill benefits from user-provided context

```yaml
argument-hint: Describe the Docker setup you want to create
```

Good hints are:
- Action-oriented: "Describe what you want to build"
- Specific: "Paste the error message you're seeing"
- Optional guidance: "Optionally include your tech stack"

## `user-invocable`

- **Type:** boolean
- **Default:** `true`
- **Purpose:** Controls whether users can invoke the skill directly via `/skill-name` in chat

Set to `false` for skills that should only be activated automatically by the model:

```yaml
user-invocable: false
```

Use case: Background knowledge skills that augment the agent passively (e.g., coding conventions skill).

## `disable-model-invocation`

- **Type:** boolean
- **Default:** `false`
- **Purpose:** If `true`, the model won't auto-activate this skill based on user queries. Only explicit `/skill-name` invocation works.

```yaml
disable-model-invocation: true
```

Use case: Sensitive or disruptive skills that should only activate when explicitly requested (e.g., a skill that modifies CI/CD config).

## `compatibility`

- **Type:** string[]
- **Purpose:** Declares which Copilot surfaces this skill supports

```yaml
compatibility:
  - copilot-chat
```

Currently recognized values:
- `copilot-chat` — VS Code Copilot Chat panel

## `license`

- **Type:** string
- **Purpose:** SPDX license identifier for the skill content

```yaml
license: MIT
```

## `metadata`

- **Type:** object (free-form)
- **Purpose:** Arbitrary key-value pairs for tooling and catalog integration

```yaml
metadata:
  author: allan-santos
  tags:
    - devops
    - containers
    - docker
  version: 1.2.0
  category: infrastructure
```

The Skill Manager extension reads `metadata.tags` for catalog filtering and `metadata.version` for update tracking.

## Complete Frontmatter Example

```yaml
---
name: docker-compose
description: "Docker Compose workflows — create, debug, and optimize multi-container setups. Covers v2 CLI, health checks, networking, volumes, and production profiles."
argument-hint: Describe what you want to do with Docker Compose
user-invocable: true
disable-model-invocation: false
compatibility:
  - copilot-chat
license: MIT
metadata:
  author: allan-santos
  tags:
    - devops
    - docker
    - containers
  version: 1.0.0
---
```
