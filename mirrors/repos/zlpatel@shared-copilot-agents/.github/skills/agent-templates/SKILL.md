---
name: agent-templates
description: "Scaffold new Copilot agents from reusable templates. Use when: creating a new agent from scratch, bootstrapping agents for a new team, generating agent files from a template pattern. Templates cover: service engineer agent, code review agent, product owner agent, solution architect agent, research-only agent."
---

# Agent Templates

Scaffold new `.agent.md` files from proven, reusable templates. Each template encodes best practices: keyword-rich descriptions, minimal tool sets, explicit constraints, and single-role focus.

## When to Use

- Bootstrapping agents for a new team
- Creating a new agent and want a solid starting point
- Standardizing agent structure across teams

## Procedure

1. Ask the user which template they need (or infer from context)
2. Read the appropriate template from `./references/`
3. Customize the template: replace placeholders with team-specific names, tech stack, and conventions
4. Save the agent file to the target workspace's `.github/agents/` folder
5. Validate YAML frontmatter and suggest 3 example prompts to test

## Available Templates

| Template | File | Best For |
| --- | --- | --- |
| Service Engineer | [service-engineer.md](./references/service-engineer.md) | Teams that implement features, fix bugs, write tests |
| Code Review | [code-review.md](./references/code-review.md) | Read-only code review agents with structured findings |
| Product Owner | [product-owner.md](./references/product-owner.md) | JIRA story/epic creation, acceptance criteria, backlog |
| Solution Architect | [solution-architect.md](./references/solution-architect.md) | Technical design docs, API design, trade-off analysis |
| Research | [research.md](./references/research.md) | Read-only codebase exploration and Q&A |

## Customization Points

Every template has these placeholders to replace:

- `{TEAM}` — Team or product name (e.g., "RM", "SAA", "CC")
- `{STACK}` — Primary tech stack (e.g., "Java 17, Spring Boot, Angular")
- `{CONVENTIONS_FILE}` — Path to the team's conventions instruction file
- `{PLATFORM_FILE}` — Path to the team's platform instruction file
- `{JIRA_PROJECT}` — JIRA project key if applicable

## Rules

- Do NOT use a template verbatim — always customize for the team
- Do NOT add tools beyond what the template specifies unless the user explicitly requests it
- Do NOT skip the constraints section — every agent needs explicit boundaries
