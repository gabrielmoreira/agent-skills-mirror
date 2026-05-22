# API stability commitment (v1.0+)

Starting with **v1.0.0** (released 2026-05-19), ui-modernizer follows [Semantic Versioning](https://semver.org). This document defines what counts as **public API** — the surface we promise not to break in 1.x.

## What is public API

The following are versioned and stable. We will not break them in a minor (1.x) release.

### 1 · The trigger phrase

Saying *"modernize this UI"* to Claude Code with ui-modernizer installed will continue to run the Skill workflow. The exact set of accepted variants is listed in `SKILL.md`.

### 2 · The Skill workflow

The 8-step workflow in `SKILL.md` (DETECT → PLAN → BACKUP → SCREENSHOT BEFORE → APPLY → SCREENSHOT AFTER + DIFF → REPORT → DONE) is the public contract for what happens when you trigger the Skill. Steps may gain capabilities; they will not be removed or reordered.

### 3 · Config file: `.ui-modernizer.json`

The schema documented in [`references/config-file.md`](./config-file.md) is stable. We may **add** new optional fields. We will not **rename** or **remove** existing fields.

### 4 · CLI script outputs

Every script in `scripts/` that has CLI entry behavior (`if (isMain) { ... }`) produces JSON output wrapped in the **unified envelope**:

```ts
{
  ok: boolean,
  command: string,
  version: string,
  timestamp: string,         // ISO 8601
  payload?: any,             // when ok === true
  errors?: ErrorEntry[],     // when ok === false
  warnings?: WarningEntry[]
}

type ErrorEntry = {
  code: string,              // 'UMD-NNN'
  title: string,
  remedy: string,
  docs: string | null,
  details: Record<string, any>,
}
```

The keys at the envelope level (`ok`, `command`, `version`, `timestamp`, `payload`, `errors`, `warnings`) are stable. New keys may be added; existing keys will keep their shape.

The internal shape of `payload` per script may evolve in minor releases — see "What is not public API" below.

### 5 · Profile format spec

[`references/style-references/_PROFILE_FORMAT.md`](./style-references/_PROFILE_FORMAT.md) v1.0 is the stable contract for profile files. We will not retire required frontmatter fields or required sections in 1.x. We may add new optional ones.

The 7 built-in profile names (linear, vercel, stripe, shadcn, notion, raycast, apple) will not be renamed or removed.

### 6 · Error codes

Every `UMD-NNN` code listed in [`references/error-codes.md`](./error-codes.md) retains its meaning across 1.x. A code's *remedy* text may be improved; the *condition* it represents will not change.

New codes are added freely. Reading by code (`if (e.code === 'UMD-040')`) is the stable way to handle errors.

### 7 · `bin/install.mjs` CLI

The subcommands are stable:

```
npx ui-modernizer                # install skill globally (~/.claude/skills/)
npx ui-modernizer --project      # install skill into ./.claude/skills/
npx ui-modernizer rollback       # restore latest backup
npx ui-modernizer uninstall      # remove the skill
npx ui-modernizer --version
npx ui-modernizer --help
```

### 8 · `scripts/_errors.mjs` and `scripts/_response.mjs` exports

The named exports `ERRORS`, `makeError`, `didYouMean`, `success`, `failure` are stable. Their signatures will not change in 1.x.

The same is true for `extractFile` exported from `scripts/ast-extract.mjs` and `loadConfig` from `scripts/load-config.mjs`.

## What is NOT public API

These are internal implementation details. We may change them in any release without notice.

- **Internals of any `_*.mjs` file** (`_errors.mjs`, `_response.mjs`, `_cli.mjs`) — only the named exports are stable.
- **Internal variables and helper functions** inside any script.
- **Field-level shape of `payload`** inside script JSON output may evolve (new fields added, internal-only fields removed). Always read defensively (`r.payload?.foo`).
- **Per-rule details inside `dry-run.mjs`**. The set of stale-pattern rules may grow or shrink between minors. Read `byRule` totals as informational.
- **`.ui-modernizer-backup/` directory layout**. Use the `backup.mjs` CLI to interact with backups; don't shell out into the directory directly.
- **Markdown content of `references/*.md`** is allowed to be revised. The *file paths* are stable (linked from SKILL.md); the content is editorial.
- **The Skill's prompt wording**. We may rewrite SKILL.md substantially without a major version bump as long as the workflow steps + trigger phrases remain.
- **CI workflow** in `.github/workflows/`. This is project-internal.
- **Test files** in `tests/`. Not user-facing.

## Breaking change policy

A change is *breaking* if it removes, renames, or changes the meaning of anything in "What is public API" above.

- We will not knowingly ship a breaking change in 1.x.
- If a breaking change becomes necessary, it ships in 2.0.0 with:
  1. A deprecation warning printed by affected scripts during the last 1.x minor
  2. A migration guide in `MIGRATION.md`
  3. The old behavior retained in a deprecated/v1-compat code path for at least one major
  4. An issue tracker with a label `breaking-change-2.0` listing what's planned

## Patch-level commitments (1.x.y)

Patch releases only:
- Fix bugs
- Improve error messages (titles/remedies, not codes)
- Improve documentation
- Add or fix tests
- Update dependencies (security)

Patches never:
- Change CLI flag names or shapes
- Add or remove error codes
- Change JSON output shape

## Minor-level commitments (1.x)

Minor releases may:
- Add new scripts
- Add new CLI flags (existing flags keep their meaning)
- Add new fields to JSON output (existing fields keep their meaning)
- Add new error codes
- Add new built-in style profiles
- Add new optional dependencies
- Improve, expand, or refactor internal code

## How to depend on us safely

If you build tooling on top of ui-modernizer:

1. **Pin a minor range**: `"ui-modernizer": "^1.0.0"` is correct (it allows `1.x.y` updates and refuses `2.0.0`).
2. **Read `errors[].code`, not `errors[].title`**. Codes are stable; titles may improve.
3. **Defensively read `payload`** with optional chaining (`payload?.field`).
4. **Don't import from `scripts/_*.mjs`** — those are internal.
5. **Watch the [Unreleased] section in CHANGELOG.md** to anticipate next-minor changes.

---

This document itself is part of public API. We will not rename or move it in 1.x.
