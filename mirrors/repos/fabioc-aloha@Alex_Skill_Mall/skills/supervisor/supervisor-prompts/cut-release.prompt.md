---
description: "Supervisor: Cut a release of Alex_ACT_Edition with full preflight and ACT pass"
mode: agent
lastReviewed: 2026-04-30
---

# /cut-release

Run the [release-ritual](../skills/release-ritual/SKILL.md) skill against the sibling repo at `../Alex_ACT_Edition`.

This is **high-stakes** — the full 7-step [act-pass](../instructions/act-pass.instructions.md) is mandatory.

Steps:

1. Confirm the user has authorized a release. If unclear, **stop and ask**.
2. Run the full ACT pass (Materiality, Hypothesise, Alternatives, Disconfirmers, Audit-priors, Severity, Commit). Show all 7 markers.
3. Run preflight from release-ritual's SKILL.md. Every check must pass — stop on any failure.
4. Confirm the version bump (major/minor/patch) based on PR categorization.
5. Show the CHANGELOG entry, version bump, and proposed commit message to the user. **Wait for explicit approval** before any irreversible step.
6. Execute commit → tag → push main → push tag.
7. Update `feedback/announcements.md` with a one-line entry.
8. Confirm the release with a final verification (tag visible on remote, announcement landed).

If any step fails, **stop**. Roll back per release-ritual's rollback procedure if the failure is mid-push.

Never run `/cut-release` automatically or in a batch — releases require human authorization at step 5.
