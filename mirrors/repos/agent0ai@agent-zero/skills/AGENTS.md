# Bundled Skills DOX

## Purpose

- Own bundled Agent Zero skills and their agent-facing instructions.
- Keep skill workflows accurate, composable, and safe for runtime loading.

## Ownership

- Each direct skill directory owns its `SKILL.md` and any local supporting files.
- Plugin-distributed skills belong under the relevant plugin directory.
- User-local skills belong under `usr/skills/`.

## Local Contracts

- Every skill directory must include a `SKILL.md`.
- Skill instructions must be operational and scoped to the skill's purpose.
- Do not include secrets, private user data, or environment-specific credentials.
- Supporting files referenced by a skill must exist relative to that skill directory.

## Work Guidance

- Keep skills focused on repeatable workflows that agents should actively follow.
- Prefer updating an existing skill over creating overlapping skill variants.
- When a skill refers to repository paths, commands, or plugin architecture, keep those references current with source and docs.

## Verification

- Run skill runtime/import tests after changing skill loading assumptions or skill format.
- Manually read changed `SKILL.md` files for broken relative references.

## Child DOX Index

No child DOX files.
