# Skill Templates — Copy-Paste Starters

Ready-to-use templates for common skill types. Copy, adapt, and fill in.

---

## Template 1: Workflow Skill

For skills that guide the agent through a process or methodology.

```markdown
---
name: <skill-name>
description: "**WORKFLOW SKILL** — <one-line summary>. USE FOR: <use case 1>, <use case 2>, <use case 3>. DO NOT USE FOR: <exclusion 1>, <exclusion 2>."
argument-hint: <What the user should provide as context>
---

# <Skill Name>

You are helping a developer with <domain>. Follow these instructions
to provide accurate, consistent guidance.

## Core Workflow

### Step 1: <First Step>
<Instructions>

### Step 2: <Second Step>
<Instructions>

### Step 3: <Third Step>
<Instructions>

## Key Rules

- Always <rule 1>
- Never <rule 2>
- When <condition>, prefer <approach>

## Reference

| <Column 1> | <Column 2> | <Column 3> |
|------------|------------|------------|
| ... | ... | ... |

## When the User Asks for Help

- **"How do I <X>?"** → <Answer for X>
- **"Why is <Y> failing?"** → <Diagnosis for Y>
- **"What's the best approach for <Z>?"** → <Recommendation for Z>
```

---

## Template 2: Knowledge/Reference Skill

For skills that provide domain expertise and lookup tables.

```markdown
---
name: <skill-name>
description: "<Domain> knowledge covering <topic 1>, <topic 2>, and <topic 3>. Includes <key feature: commands, examples, patterns>."
---

# <Domain> — Agent Reference

You are a <domain> expert. Use this knowledge to help developers
with <scope>.

## Concepts

### <Concept 1>
<Explanation + when/how to apply>

### <Concept 2>
<Explanation + when/how to apply>

## Commands / API

| Command | Purpose | Example |
|---------|---------|---------|
| `<cmd>` | <what it does> | `<usage>` |

## Patterns

### <Pattern Name>
**When to use:** <condition>
**Implementation:**
\```<lang>
<code example>
\```

## Common Pitfalls

| | Pitfall | Consequence |
|---|---------|-------------|
| ❌ | <mistake> | <what happens> |
| ✅ | <correct approach> | <why it works> |

## When the User Asks for Help

- **"Explain <concept>"** → <Clear explanation>
- **"Show me how to <task>"** → <Code example from Patterns>
- **"What's wrong with <code>?"** → <Check Common Pitfalls table>
```

---

## Template 3: Tool/Extension Skill

For skills that teach how to use a specific tool or extension.

```markdown
---
name: <tool-name>-guide
description: "How to use <Tool Name> — <key capabilities summary>"
argument-hint: Describe what you need help with in <Tool Name>
---

# <Tool Name> — User Guide

You are helping a developer who uses **<Tool Name>**. This skill
teaches you how the tool works so you can guide them effectively.

## What is <Tool Name>?

<One paragraph: what it does and why developers use it>

## Commands / Interface

| Command / Action | What it does |
|-----------------|-------------|
| `<command>` | <description> |

## Configuration

Users configure <Tool Name> via <mechanism>:

\```jsonc
{
  // <setting description>
  "<setting.key>": <default value>
}
\```

## Common Workflows

### <Workflow 1: e.g., Initial Setup>
1. <Step>
2. <Step>

### <Workflow 2: e.g., Daily Usage>
1. <Step>
2. <Step>

## When the User Asks for Help

- **"How do I <setup>?"** → <Setup instructions>
- **"<Thing> isn't working"** → <Troubleshooting steps>
- **"How do I configure <feature>?"** → <Point to Configuration section>
```

---

## Template 4: Coding Standards Skill

For skills that enforce team conventions and coding patterns.

```markdown
---
name: <team>-standards
description: "Coding standards for <team/project> — naming conventions, file structure, patterns, and review checklist. Covers <lang/framework>."
user-invocable: false
---

# <Team/Project> Coding Standards

Apply these standards when helping developers write or review code
in this project.

## File Structure

\```
src/
  components/     ← <convention>
  services/       ← <convention>
  utils/          ← <convention>
  types/          ← <convention>
\```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Components | PascalCase | `UserProfile` |
| Functions | camelCase | `getUserById` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Files | kebab-case | `user-profile.tsx` |

## Patterns to Follow

### <Pattern 1>
\```<lang>
// Good
<example>

// Bad
<counter-example>
\```

## Code Review Checklist

- [ ] Follows naming conventions above
- [ ] No business logic in components
- [ ] Error handling at system boundaries
- [ ] Tests for new public functions
```
