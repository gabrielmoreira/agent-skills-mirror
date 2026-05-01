# Contributing to Alex Skill Mall

Thank you for sharing your hard-won knowledge. This guide explains how to contribute skills that meet our quality standards.

---

## Before You Contribute

### Quality Gates

Every skill must pass ALL of these:

| Gate | Question | If No |
|------|----------|-------|
| **Time savings** | Would this save someone >30 min of debugging? | Too shallow |
| **Non-obvious** | Is this NOT the first result on Google/Stack Overflow? | Too common |
| **Battle-tested** | Has this been used in a real project? | Unverified |
| **Specific** | Does this solve a concrete problem, not a vague concern? | Too abstract |
| **Current** | Is this still relevant (not fixed in a newer version)? | Outdated |

### What We Don't Accept

- Generic best practices ("use meaningful variable names")
- Documentation summaries ("here's how Azure Functions work")
- Shallow checklists ("don't forget to test")
- Anything easily found with a basic search
- Theoretical patterns without real-world validation
- Content with PII or client-specific details

---

## Skill Format

### Directory Structure

```
skills/category/skill-name/
├── SKILL.md              # Required: The knowledge itself
├── skill-name.instructions.md  # Optional: Auto-load trigger
└── examples/             # Optional: Code examples
    └── ...
```

### SKILL.md Template

```markdown
# Skill Name

**Tags**: `tag1` `tag2` `tag3`
**Currency**: 2026-04-27
**Time saved**: X hours

---

## The Problem

[Describe the specific problem this skill solves. Be concrete.]

## Why This Is Hard to Find

[Explain why Google/Stack Overflow/LLMs don't easily surface this.]

## The Solution

[The actual knowledge. Be specific and actionable.]

### Code Example (if applicable)

\`\`\`language
// Concrete example
\`\`\`

## Evidence

- [Link to issue where this was discovered]
- [Link to project where this was used]
- [Other validation]

## Related

- [Links to related skills]
- [Links to official docs that are incomplete]
```

### Optional: Instructions File

If the skill should auto-load in certain contexts, add an instructions file:

```markdown
---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "One-line description of when this loads"
applyTo: "**/*.ts"  # Glob pattern for auto-loading
currency: 2026-04-27
---

# Skill Name

[Brief trigger content that tells the AI to read the full SKILL.md]

See `.github/skills/skill-name/SKILL.md` for full details.
```

---

## Scaffold Format

### Directory Structure

```
scaffolds/scaffold-name/
├── README.md             # What this scaffold provides
├── .github/              # Pre-configured brain
│   └── ...
├── src/                  # Starter code
│   └── ...
├── package.json          # Dependencies (if applicable)
└── ...                   # Other project files
```

### README Requirements

Every scaffold README must include:

1. **What you get** — List of pre-configured features
2. **Prerequisites** — Required tools and accounts
3. **Quick start** — Copy, configure, deploy
4. **What's pre-configured** — Explain each decision
5. **Customization points** — What to change for your needs
6. **Known limitations** — Be honest about what's not covered

---

## Submitting a Skill

### 1. Fork and Branch

```bash
git clone https://github.com/YOUR_USERNAME/Alex_ACT_KB.git
git checkout -b skill/your-skill-name
```

### 2. Create the Skill

Follow the format above. Include:

- Concrete problem description
- Why it's hard to find
- Actionable solution
- Evidence links

### 3. Regenerate CATALOG.json

Run `node scripts/generate-catalog.cjs` to update the machine-readable catalog.

### 4. Submit PR

Use this PR template:

```markdown
## Skill: [Name]

### Quality Gate Checklist

- [ ] Time savings: >30 min
- [ ] Non-obvious: Not first Google result
- [ ] Battle-tested: Used in real project
- [ ] Specific: Solves concrete problem
- [ ] Current: Still relevant

### Evidence

- Issue where discovered: [link]
- Project where used: [link]

### Description

[Brief description of what this skill solves]
```

---

## Review Process

1. **Automated checks** — Format validation, required files
2. **Value review** — Does it pass the quality gates?
3. **Technical review** — Is the solution correct and complete?
4. **Merge** — Added to catalog

Reviews typically complete within 1 week.

---

## Updating Existing Skills

Skills can become outdated. To update:

1. Check if the issue is still relevant in current versions
2. Update the solution if platform behavior changed
3. Update the `currency` date
4. Note what changed in your PR

To deprecate a skill:

1. Add `**Status**: Deprecated as of [version]` to SKILL.md
2. Explain what changed (e.g., "Fixed in Azure SWA v2.0")
3. Skill will be removed after 6 months

---

## Code of Conduct

- Be respectful and constructive in reviews
- Credit original discoverers when known
- No PII or client-specific content
- Keep skills focused and actionable

---

## Questions?

Open an issue with the `question` label.
