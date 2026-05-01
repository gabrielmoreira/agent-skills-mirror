---
type: instruction
lifecycle: stable
inheritance: master-only
description: "Release discipline for Alex_ACT_Edition — preflight is non-negotiable, releases require the full ACT pass"
application: "When cutting any release of Alex_ACT_Edition"
applyTo: "**/CHANGELOG.md,**/package.json,**/Alex_ACT_Edition/**"
currency: 2026-04-28
lastReviewed: 2026-01-01
---

# Release Discipline

Releases ship the brain template to the ACT-Edition fleet. They are **always high-stakes**, regardless of size. This instruction is the always-on rule; [release-ritual](../skills/release-ritual/SKILL.md) is the procedure.

## Hard Rules

1. **Preflight is non-negotiable.** Every check in release-ritual's preflight table must pass before any irreversible step (commit, tag, push). A failing check stops the release.
2. **Full ACT pass for every release.** Even a one-line typo fix gets the full 7-step pass — the irreversibility is what makes it high-stakes, not the size.
3. **No release without a CHANGELOG entry.** The entry lands in the *same commit* as the version bump, not after.
4. **Tag every release.** Heirs pull by tag; an untagged release is invisible to the fleet.
5. **Push order: commit → tag → push main → push tag.** Reversed order can leave the fleet seeing a tag that points at a commit not yet on `main`.
6. **Announce after push, not during.** The announcement file in `feedback/announcements.md` updates *after* the push succeeds, never speculatively.

## Visible Markers

Every release commit should include in its body or in PR description:

```text
Preflight: ✓ all checks pass
ACT pass: full (7 steps)
Breaking: <count>
Feature: <count>
Fix: <count>
```

## Forbidden Operations

| Operation | Why |
|---|---|
| `git push --force` to a release tag | Heirs may have already pulled; force-push silently corrupts |
| Editing a tag after publish | Tags are immutable contracts |
| Bumping version without CHANGELOG entry | Releases are documentation events, not code events |
| Releasing on top of a failing brain-qa | Ship-it-and-fix-it doesn't work for fleet templates |

## Rollback Trigger

Cut an emergency patch release within 24 hours if any of:

- Heir reports the release breaks their setup
- A failing brain-qa surfaces post-release
- A security issue is discovered in shipped artifact

After 24 hours, follow the standard fix-forward path — never delete tags.

## Related

- [release-ritual](../skills/release-ritual/SKILL.md) — full procedure
- [act-pass](act-pass.instructions.md) — required full pass
- [brain-curation-rules](brain-curation-rules.instructions.md) — sibling discipline
