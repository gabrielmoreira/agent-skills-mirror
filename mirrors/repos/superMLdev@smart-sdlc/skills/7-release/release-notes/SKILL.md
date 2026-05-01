# Skill: Release Notes

> **Activation**: `#file:_superml/skills/7-release/release-notes/SKILL.md`

---

## Purpose

Generate user-facing and internal release notes that clearly communicate what changed, what was fixed, and any breaking changes or migration steps required.

---

## Inputs

Load before starting:
- PRD: `{output_path}/planning/prd.md`
- Epics & stories: `{output_path}/planning/epics.md`
- Bug triage log: `{output_path}/qa/bug-triage.md`
- Deployment runbook: `{output_path}/release/deploy-runbook.md`

---

## Deliverable

**`{output_path}/release/release-notes.md`**

After completing, update `_superml/config.yml`:
```yaml
artifacts:
  release_complete: true
```

---

## Release Notes Structure

```markdown
# Release Notes — {project_name} v{version}

**Release date**: {date}
**Release type**: Major / Minor / Patch / Hotfix

---

## Highlights

{1–3 sentence summary of what this release delivers and why it matters}

---

## New Features

### {Feature Name}
{Brief description of what it does and the value it provides}

### {Feature Name}
{Brief description}

---

## Improvements

- **{Area}**: {What improved and how it helps users}
- **{Area}**: {What improved}

---

## Bug Fixes

| Bug ID | Summary | Affected Users |
|--------|---------|----------------|
| BUG-001 | {Summary} | {Who was affected} |

---

## Breaking Changes

> ⚠️ Review these carefully before upgrading.

### {Breaking change title}
- **What changed**: {Describe the change}
- **Why**: {Business/technical reason}
- **Migration steps**:
  1. Step 1
  2. Step 2
- **Rollback**: {How to revert if needed}

---

## Known Issues

| Issue | Severity | Workaround | Fix ETA |
|-------|----------|-----------|---------|
| {Description} | P{N} | {Workaround} | {Sprint/Date} |

---

## Upgrade Notes

{Any configuration changes, dependency updates, or environment variable changes required}

---

## Technical Details

- **Git tag**: v{version}
- **Build**: {CI build number / link}
- **Deployed to**: {environments}
- **Deployment date**: {date}

---

## Acknowledgements

{Optional: thank contributors, highlight team effort}
```

---

## Validation Checklist

- [ ] All new features described in user-facing language (not technical jargon)
- [ ] All P1/P2 bug fixes listed
- [ ] Breaking changes section complete (or marked "None")
- [ ] Known issues documented with workarounds
- [ ] `artifacts.release_complete` updated in `_superml/config.yml`

---

## 🎉 Release Complete

Congratulations! Set `artifacts.release_complete: true` to close out the release phase.

The full SDLC cycle is complete:
```
Product → Architecture → Team Lead → Development → QA → Release ✅
```
