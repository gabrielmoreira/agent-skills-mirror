---
name: vibe-code-cleanup
description: "Hardens vibe-coded Next.js/React/Node apps by removing proven-dead imports, unused files, and broken refs without rewriting working routes. Use when a rapidly built app works but is messy before launch. Not for greenfield features, broad architecture rewrites, or deleting files still referenced by routes or APIs."
category: fullstack
risk: safe
source: self
source_type: self
date_added: "2026-05-31"
tags: [cleanup, refactor, nextjs, production, vibe-code, fullstack, nodejs]
tools: [claude, cursor, gemini, claude-code]
version: 1.0.1
---

# Vibe-Code Cleanup — Production Refactor Skill

A safe, incremental cleanup workflow for AI-generated / vibe-coded fullstack apps.
The goal is to make the codebase production-ready **without** breaking anything that already works.

> **Surgery, not demolition.** Remove only what is provably dead. Preserve everything else.

## When to Use

- Use when a rapidly built app works but has broken imports, duplicated logic, dead code, unclear environment variables, or fragile release hygiene.
- Use before launch or handoff to convert exploratory code into a maintainable production baseline.
- Use when cleanup must preserve existing behavior and avoid broad rewrites of routes, APIs, auth, data models, or integrations.
- Trigger keywords: `cleanup`, `dead code`, `broken imports`, `unused files`, `production-ready`, `refactor`, `vibe code`, `hardening`.

## Prerequisites

- Node.js project with a working `package.json` and installable dependencies.
- TypeScript recommended but not required (type-check commands assume TS; skip if pure JS).
- Git repository with a clean working tree so each batch can be reverted independently.
- Windows host is primary. Use PowerShell for file-system and grep commands. Bash equivalents are provided where the toolchain expects POSIX shells (e.g., `npx tsc`).
- Consolidation templates and env-var documentation patterns are in Steps 4–5 of this file.

## Procedure

### Step 1 — Reconnaissance (read before touching)

Before changing anything, map the codebase. **Do NOT change anything yet — document findings only.**

**PowerShell:**

```powershell
# List all Next.js app-router pages
Get-ChildItem -Recurse -Include page.js,page.jsx,page.ts,page.tsx -ErrorAction SilentlyContinue | Select-Object FullName

# List pages-router files (exclude _app, _document, _error, etc.)
Get-ChildItem -Path pages -Recurse -Include *.js,*.jsx,*.ts,*.tsx -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike '_*' } | Sort-Object FullName | Select-Object FullName

# Find debug leftovers
Select-String -Path *.js,*.jsx,*.ts,*.tsx -Recurse -Pattern 'console\.log|debugger|TODO|FIXME|HACK' | Select-Object Path, LineNumber, Line
```

**Bash (if running in WSL or CI):**

```bash
find . -type f \( -name 'page.js' -o -name 'page.jsx' -o -name 'page.ts' -o -name 'page.tsx' \)
find pages -type f \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' \) | rg -v '/_' | sort
grep -r "console\.log\|debugger\|TODO\|FIXME\|HACK" --include="*.{js,ts,jsx,tsx}" -l
```

**TypeScript projects — list all type errors:**

```bash
npx tsc --noEmit 2>&1 | head -80
```

**Optional — find unused exports (larger projects):**

```bash
npx ts-prune 2>/dev/null | head -40
```

### Step 2 — Fix Broken Imports First

Broken imports cause build failures and must be fixed before anything else.

```bash
# TypeScript: list all errors
npx tsc --noEmit 2>&1
```

Common patterns to fix:
- Missing file (file was deleted or renamed)
- Wrong relative path (`../lib` vs `../../lib`)
- Named export that doesn't exist

**Fix rule:** Fix the import reference. Do NOT delete the referenced file unless you've confirmed it's unused everywhere (Step 3).

### Step 3 — Identify Dead Code (verify before removing)

A file/export is safe to remove **only if all three** are true:
1. No other file imports it (grep-confirmed)
2. It's not referenced in config, sitemap, or route manifest
3. It's not a public-facing URL (`page.js`, `route.js`)

**PowerShell:**

```powershell
# Check if a file is imported anywhere
Select-String -Path *.js,*.jsx,*.ts,*.tsx -Recurse -Pattern 'my-file' | Select-Object Path, LineNumber, Line

# Check if a component is used anywhere
Select-String -Path *.js,*.jsx,*.ts,*.tsx -Recurse -Pattern 'MyComponent' | Select-Object Path, LineNumber, Line
```

**Bash:**

```bash
grep -r "from.*my-file\|require.*my-file" --include="*.{js,ts,jsx,tsx}" .
grep -r "MyComponent" --include="*.{js,ts,jsx,tsx}" .
```

### Step 4 — Consolidate Repeated Logic into Helpers

Use the consolidation targets, anti-patterns, and `buildPageMetadata` helper in this step.

Look for repeated patterns (metadata blocks, API fetch wrappers, error handlers) that appear in **3+ places**.

**Good consolidation targets:**
- Page-level SEO metadata (Open Graph, Twitter cards, canonical)
- Fetch wrappers with error handling
- Repeated utility functions (slugify, formatDate, truncate)

**Bad consolidation targets (leave alone):**
- One-off business logic
- Route handlers with different contracts
- Anything touching DB schema or auth

**Pattern for shared metadata helper (Next.js):**

```js
// lib/socialMetadata.js
export function buildPageMetadata({ title, description, path, image }) {
  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://yourdomain.com';
  const imageUrl = image?.startsWith('http') ? image : `${baseUrl}${image}`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `${baseUrl}${path}`,
      images: [{ url: imageUrl, width: 1200, height: 630, alt: title }],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
    },
    alternates: {
      canonical: `${baseUrl}${path}`,
    },
  };
}
```

### Step 5 — Environment Variable Audit

Document every `process.env` key used in code in `.env.example` with `YOUR_KEY` placeholders. Never add secrets to version control.

**PowerShell:**

```powershell
# List all env vars used in code
Select-String -Path *.js,*.jsx,*.ts,*.tsx -Recurse -Pattern 'process\.env\.\w+' | ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } | Sort-Object -Unique

# Compare against .env.example or .env.local
Get-Content .env.example -ErrorAction SilentlyContinue; Get-Content .env.local -ErrorAction SilentlyContinue
```

**Bash:**

```bash
grep -r "process\.env\." --include="*.{js,ts,jsx,tsx}" . | grep -oP 'process\.env\.\w+' | sort -u
cat .env.example 2>/dev/null || cat .env.local 2>/dev/null
```

Flag any env vars used in code but missing from `.env.example`. **Never add secrets to version control.** Use `YOUR_KEY` placeholders in `.env.example`.

### Step 6 — Validate After Every Batch

Run this after every meaningful batch of cleanup changes:

```bash
# TypeScript check
npx tsc --noEmit

# Lint
npx eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0

# Build (catches runtime issues TypeScript misses)
npm run build

# Tests (if present)
npm test -- --runInBand --passWithNoTests
```

If build or typecheck breaks → **revert the last batch** before continuing.

### Step 7 — Commit Strategy

Each commit should be a single logical unit:

```text
fix: remove broken import in app/blog/page.js
refactor: consolidate social metadata into lib/socialMetadata.js
chore: remove verified-unused utils/oldHelper.js
fix: standardize env var references to NEXT_PUBLIC_BASE_URL
```

**Never** bundle UI changes + logic changes + file deletions in one commit. Smaller commits = easier rollback.

## Pitfalls

### NEVER do these (hard rules)

- **Never** rewrite working systems for cosmetic reasons.
- **Never** rename routes, slugs, or API endpoints that may be indexed or cached.
- **Never** change tool inputs/outputs, API contracts, DB schema, or auth flow.
- **Never** delete files you haven't verified are unused (grep-confirmed + config-checked).
- **Never** make broad sweeping changes in a single commit.
- **Never** add real secrets to version control. Use `YOUR_KEY` placeholders only.
- **Never** bundle UI changes + logic changes + file deletions in one commit.

### Off-limits areas (unless there's a verified bug)

| Area | Why |
|------|-----|
| Route slugs / page paths | May be indexed by Google |
| API route contracts | Callers depend on exact shape |
| DB schema / Prisma models | Migration required |
| Auth flow logic | Security-sensitive |
| Third-party integration configs | Keys/webhooks are environment-specific |
| Working tool pages | User-facing functionality |

### Common mistakes

- Deleting a file that is dynamically imported (e.g., `await import(...)` or Next.js dynamic routes) — grep for string-based imports too.
- Removing an "unused" export that is actually consumed by a barrel file (`index.js` re-exports).
- Consolidating route handlers that look similar but have different response contracts.
- Forgetting that `process.env.NEXT_PUBLIC_*` vars are inlined at build time — renaming them requires a rebuild and may break cached clients.

## Verification

Run the full validation suite after the final batch:

```bash
# 1. TypeScript — zero errors expected
npx tsc --noEmit
# Expected: no output, exit code 0

# 2. Lint — zero warnings
npx eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0
# Expected: no output, exit code 0

# 3. Build — must succeed
npm run build
# Expected: "✓ Compiled successfully" or equivalent, exit code 0

# 4. Tests — pass or no tests
npm test -- --runInBand --passWithNoTests
# Expected: all suites green or "No tests found"
```

**Cleanup checklist — confirm every item:**

- [ ] TypeScript errors fixed
- [ ] No broken imports
- [ ] Dead code removed (grep-verified)
- [ ] Shared helpers created for repeated patterns (3+ uses)
- [ ] No hardcoded secrets or local-only URLs
- [ ] All env vars documented in `.env.example`
- [ ] Build passes
- [ ] Tests pass (or no tests exist)
- [ ] Lint passes
- [ ] Each commit is scoped and explainable

## Limitations

- Does not infer product intent from code alone; confirm behavior before deleting routes, components, API contracts, or data models.
- Cleanup should be applied in small reviewed batches because broad refactors can hide regressions.
- Avoid changing auth, billing, persistence, or third-party integration behavior without explicit requirements and tests.

## Related Skills

- `production-deployment-prep` — pre-launch deployment hardening
- `env-var-management` — structured environment variable documentation
- `typescript-strict-migration` — moving to strict TS after cleanup
