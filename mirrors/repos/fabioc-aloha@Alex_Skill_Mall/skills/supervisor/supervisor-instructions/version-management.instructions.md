---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Always-on semver discipline for Alex_ACT_Edition releases — every PR is classified before merge, every release records its bump"
application: "Always active when reviewing or releasing changes to Alex_ACT_Edition"
applyTo: "**/Alex_ACT_Edition/**,**/CHANGELOG*,**/package.json"
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Version Management Rules

Always-on discipline for the Edition's semver contract. Pairs with [version-management](../skills/version-management/SKILL.md).

## Hard Rules

1. **Every Edition PR is classified at review time** as patch / minor / major. The classification is recorded in the PR description and in `decisions/curation-log.md` at merge.
2. **Behavior changes are always major.** "It's just a fix" does not bypass this — if heirs depending on the old behavior break, it's major regardless of authorial intent.
3. **Two-step deprecation is non-negotiable.** Removing an artifact requires a prior minor release that marked it `lifecycle: deprecated`. No exceptions.
4. **Patch releases ship no new artifacts.** A new skill, instruction, prompt, or config field is at minimum a minor bump.
5. **Major releases carry a migration note in CHANGELOG.** The note tells a heir on N-1 exactly what to do.

## Classification Triggers

A change is **major** if it does any of:

- Removes a skill, instruction, prompt, agent, or muscle
- Renames any of the above (alias path is required for one minor cycle)
- Changes the schema of `.github/config/*.json` in a way that requires heir action
- Changes the *behavior* of an existing artifact (different output, different invocation, different routing)
- Adds a required field to a frontmatter schema that existing heir copies don't carry

A change is **minor** if it is purely additive: a new skill, a new optional config field, a new prompt — and existing heirs would work unchanged if they ignored it.

A change is **patch** if it is invisible to heirs: typo fixes, internal script refactors, comment improvements, doc clarifications that don't change directives.

## Visible Marker (per release)

Append to the curation-log entry:

> `Bump: <patch|minor|major>` · `Breaks: <none|categories>` · `Deprecated: <none|list>` · `Removed: <none|list>`

For a patch: `Bump: patch · Breaks: none · Deprecated: none · Removed: none` is acceptable but the marker is still required.

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Bumping based on "feel" instead of the rules | Run the would-a-heir-notice test |
| Marketing-driven version bumps (forcing 1.0 because it sounds ready) | Versions reflect API contract, not maturity narrative |
| Skipping the deprecation step "because no one uses it yet" | The two-step protocol holds even when heirs are zero |
