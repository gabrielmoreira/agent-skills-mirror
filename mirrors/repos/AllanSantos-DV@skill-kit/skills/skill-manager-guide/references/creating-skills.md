# Creating Your Own Skill

For a complete, in-depth guide on creating skills — including frontmatter reference, body best practices, templates, and quality checklist — use the **skill-creator** skill:

```
/skill-creator Describe the domain or topic the new skill should cover
```

## Quick Start

```bash
# Inside your skills repo
mkdir -p skills/my-skill
```

Create `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: What this skill teaches
---

# My Skill

Instructions and knowledge for the AI agent...
```

## Publish

Push your repo to GitHub (public or private) and share the URL. Users add it via:

```
Ctrl+Shift+P → Skills: Add Repository → paste URL
```
