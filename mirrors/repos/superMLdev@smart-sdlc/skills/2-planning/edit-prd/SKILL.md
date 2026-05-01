---
name: edit-prd
description: "Edit and refine an existing PRD section by section. Use when the user says 'update the PRD', 'change a requirement', or 'add a feature to the PRD'."
---

# Edit PRD

## Goal

Make targeted edits to an existing PRD while maintaining document integrity, version history, and consistency.

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Ask: "Which PRD are we editing?" — default: latest file in `{planning_artifacts}/prd/`
3. Load the PRD. Show its current version and status.

## Edit Session

Ask: "What would you like to change? (You can describe it in plain language)"

For each requested change:

1. **Locate** the affected section(s)
2. **Show** the current text
3. **Propose** the change
4. ⏸️ **STOP** — get approval before writing

After making changes:
- Bump version number in frontmatter (1 → 1.1, or 1.1 → 2 for major changes)
- Add a changelog entry:

```markdown
## Changelog
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.1 | {date} | {user_name} | {description of change} |
```

## Consistency Check After Edits

After all edits, run a quick scan:
- Does the change create any contradictions with other requirements?
- Does it affect any acceptance criteria in other sections?
- Does it invalidate any open questions (now resolved)?

Flag any detected inconsistencies.

## Completion

> "✅ PRD updated to v{new_version}. Saved at `{planning_artifacts}/prd/{project_name}-prd.md`."
>
> If stories have been generated from this PRD, note: "⚠️ Stories were previously generated from v{old_version}. Consider re-running `create-epics-stories` to regenerate affected stories."
