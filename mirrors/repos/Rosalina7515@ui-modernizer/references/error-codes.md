# Error codes (v0.9+)

Every error ui-modernizer surfaces is identified by a `UMD-NNN` code. The code maps to a one-paragraph remedy and (often) a docs link, so you can fix it without guessing.

The codes are grouped by feature area. The first digit of the suffix indicates the area:

| Range | Area |
|---|---|
| 001–009 | Stack detection |
| 010–019 | Config file (`.ui-modernizer.json`) |
| 020–029 | Backup / rollback |
| 030–039 | Visual regression / screenshots |
| 040–049 | AST safety net |
| 050–059 | Style profile system |
| 060–069 | Component substitution (shadcn) |
| 999 | Unknown / internal — please file a bug |

---

## UMD-001 — Tailwind CSS not detected

`tailwindcss` is missing from `package.json`. Both v3 and v4 are supported.

```bash
npm install -D tailwindcss
```

Docs: [`references/tailwind-v4.md`](./tailwind-v4.md)

## UMD-002 — Unsupported runtime

Neither `react`, `vue`, nor `svelte` was found. Install one to use ui-modernizer.

## UMD-003 — Meta-framework missing

| Runtime | Required framework |
|---|---|
| React | Next.js |
| Vue | Nuxt **or** Vite |
| Svelte | SvelteKit **or** Vite |

## UMD-010 — `.ui-modernizer.json` parse error

The config file has invalid JSON. Validate it:

```bash
jq . .ui-modernizer.json     # or paste into jsonlint.com
```

Common causes: trailing comma, single quotes instead of double, unquoted keys.

Docs: [`references/config-file.md`](./config-file.md)

## UMD-011 — Config validation failed

One or more fields have invalid values. The error `details` array tells you which. Full schema in [`references/config-file.md`](./config-file.md).

## UMD-012 — Unknown profile name

The `profile` field doesn't match any built-in. Built-ins: `linear`, `vercel`, `stripe`, `shadcn`, `notion`, `raycast`, `apple`. For a custom profile, use a path ending in `.md`.

Errors of this kind include a `didYouMean` suggestion based on Levenshtein distance — if you typed `lineer`, expect `{ "didYouMean": "linear" }`.

Docs: [`references/profile-pluggability.md`](./profile-pluggability.md)

## UMD-020 — Backup directory missing

`.ui-modernizer-backup/` does not exist. Either the modernization run was never started, or the directory was cleaned up. There is nothing to roll back to.

## UMD-021 — Backup file not found in manifest

A file listed in `manifest.json` is missing on disk. The backup may be partially corrupted. Check `.ui-modernizer-backup/<stamp>/files/` manually.

## UMD-030 — Playwright not installed

Visual regression and screenshots require Playwright (optional dependency):

```bash
npm install -D playwright
npx playwright install chromium
```

Without it, modernization still works — only the Risks section in `report.md` is omitted.

Docs: [`references/visual-regression.md`](./visual-regression.md)

## UMD-031 — Dev server failed to start

`npm run dev` did not respond within 90s. Check the dev log:

```
.ui-modernizer/snapshots/<before|after>/dev-server.log
```

Common causes: port conflict, missing dependencies, build error.

## UMD-032 — Snapshot pair missing

`visual-diff.mjs` needs *both* a `before` and `after` snapshot per route. Re-run `visual-snapshot.mjs before` and `visual-snapshot.mjs after`.

## UMD-040 — `@babel/parser` not installed

AST safety for JSX/TSX (optional but recommended):

```bash
npm install -D @babel/parser @babel/traverse
```

Without it, the modernizer falls back to regex extraction — still functional, just less precise.

Docs: [`references/ast-safety.md`](./ast-safety.md)

## UMD-041 — Source file parse error

The file contains a syntax error or uses a feature `@babel/parser` doesn't recognize with the configured plugins. Verify the file compiles in your normal build first.

## UMD-050 — Profile validation failed

The profile file does not conform to the [v1.0 format spec](./style-references/_PROFILE_FORMAT.md). See error details for which checks failed.

## UMD-051 — Profile missing required frontmatter

YAML frontmatter at the top of a profile must include: `name`, `displayName`, `version`, `vibe`, `darkFirst`, `recommendedFonts`, `authors`.

## UMD-052 — Profile name does not match filename

The `name` field in frontmatter must equal the filename without the `.md` extension. Rename one to match the other.

## UMD-060 — shadcn `components.json` missing

Component substitution needs shadcn initialized:

```bash
npx shadcn@latest init    # interactive — choose style, base color, etc.
```

Then re-run modernization with the substitution opt-in phrase.

Docs: [`references/component-substitution.md`](./component-substitution.md)

## UMD-061 — shadcn install failed

`npx shadcn add` exited non-zero. Common causes:
- No network access
- Version conflict in `package.json`
- Missing tsconfig path aliases (`@/*`)

Run the command manually to see the full error output, then retry.

## UMD-999 — Unknown internal error

This shouldn't happen. Please [file an issue](https://github.com/Rosalina7515/ui-modernizer/issues) with the full output.
