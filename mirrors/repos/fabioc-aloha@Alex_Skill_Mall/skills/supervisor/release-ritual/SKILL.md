---
type: skill
lifecycle: stable
inheritance: master-only
name: release-ritual
description: Cut a release of Alex_ACT_Edition — preflight, brain-qa, changelog, version bump, tag, push
tier: standard
applyTo: '"**/Alex_ACT_Edition/**,**/CHANGELOG.md,**/package.json"'
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Release Ritual

Cut a versioned release of `Alex_ACT_Edition`. Releases are **high-stakes** operations: they ship the brain template to heir projects across the fleet. Run the full 7-step ACT pass before invoking the irreversible steps.

## When to Use

- Accepted PRs accumulate to a meaningful release
- A critical bug requires a patch release
- The 60-day re-evaluation cycle ends and a checkpoint release is appropriate

**Do not use** for: in-progress drafts, single-skill experiments, untested submissions.

## Preflight (must all pass before any irreversible step)

| Check | Tool | Pass criterion |
|---|---|---|
| All accepted PRs merged | `git log` against `../Alex_ACT_Edition` | No open PRs marked "ship in this release" |
| Working tree clean | `git status` | No uncommitted changes |
| brain-qa exits 0 | `node ../Alex_ACT_Edition/scripts/brain-qa.cjs` (when present) | Exit code 0 |
| Self-contained check | grep for `../master-wiki/` or absolute paths in `.github/` | Zero matches |
| CHANGELOG.md updated | manual review | Entry for the new version with all merged PRs |
| Version bumped | `grep version package.json` (when present) or `currency:` in frontmatter | New version > previous |
| ACT pass complete | this skill | Full 7-step trail recorded |

## Release Steps (in order)

### 1. Confirm scope

List every PR being released. Categorize:

| Category | Examples |
|---|---|
| Breaking | API changes, removed skills, renamed files heirs depend on |
| Feature | New skills, new instructions, new prompts |
| Fix | Bug fixes, typo fixes, link repairs |
| Chore | Dependency bumps, dev-only changes |

If **breaking** is non-empty, bump major version (`X.0.0`). Else if **feature** is non-empty, bump minor (`x.X.0`). Else bump patch (`x.x.X`).

### 2. Update CHANGELOG.md

```markdown
## [x.y.z] - YYYY-MM-DD

### Breaking
- ...

### Added
- ...

### Fixed
- ...

### Chore
- ...
```

### 3. Bump version

Update version in:

- `package.json` (if present)
- `README.md` version badge (if present)
- `.github/copilot-instructions.md` if it carries a version stamp

### 4. Run preflight

All checks from the table above must pass. If any fail, **stop**. Fix and re-run.

### 5. Commit

```text
git add CHANGELOG.md package.json README.md .github/
git commit -m "Release vX.Y.Z"
```

### 6. Tag

```text
git tag -a vX.Y.Z -m "Alex_ACT_Edition vX.Y.Z"
```

### 7. Push (irreversible)

This is the high-stakes step. Run the full ACT pass before:

```text
git push origin main
git push origin vX.Y.Z
```

### 8. Announce

Write a one-line entry to `feedback/announcements.md` (create if absent):

```markdown
- vX.Y.Z (YYYY-MM-DD) — <one-line summary>. See CHANGELOG for details.
```

Heirs poll this on next session-start.

## Rollback Procedure

If a release introduces a regression and is caught within 24 hours:

```text
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
git revert <release-commit-sha>
git push origin main
```

Then immediately cut a patch release with the revert + a `Fixed` entry citing the regression.

If the regression is caught after 24 hours, **do not delete the tag** — heirs may have already pulled. Cut a patch release instead and document the bug in CHANGELOG.

## Anti-Patterns

| Anti-pattern | Correction |
|---|---|
| Pushing before preflight | Preflight is non-negotiable — even for "obvious" patch releases |
| Skipping ACT pass on a "small" release | Releases are always high-stakes; small does not mean low-risk |
| Forgetting the tag | Heirs pull by tag; an untagged commit is invisible to the fleet |
| Editing CHANGELOG after the fact | CHANGELOG must be committed as part of the release commit, not after |

## Related

- [release-discipline](../../instructions/release-discipline.instructions.md) — the always-on rule
- [act-pass](../../instructions/act-pass.instructions.md) — full pass mandatory for releases
- `/cut-release` prompt
