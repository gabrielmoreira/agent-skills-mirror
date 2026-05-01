---
type: skill
lifecycle: stable
inheritance: inheritable
name: github-readme-override
description: GitHub README display rules — which README renders when multiple exist, profile READMEs, org READMEs
tier: standard
applyTo: '**/*github*,**/*readme*,**/*override*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# GitHub README Override

**Category**: GitHub
**Time Saved**: 30-60 minutes
**Battle-tested**: Yes — multiple projects affected

---

## The Problem

You update your root `README.md` with new documentation. You push to GitHub. The repo landing page still shows the old content — or worse, a completely different file.

## Why It Happens

GitHub treats `.github/README.md` as a "community health file" and displays it on the repository landing page **instead of** the root `README.md`. This is documented behavior but surprising when you don't expect it.

## The Hierarchy

```
GitHub displays the FIRST match found in this order:

1. .github/README.md     ← Overrides everything
2. README.md             ← Standard location
3. docs/README.md        ← Alternative location
```

## The Fix

**Option 1: Delete the override**

```bash
git rm .github/README.md
git commit -m "Remove README override"
git push
```

**Option 2: Rename it**

```bash
# Keep the file but don't let it override
git mv .github/README.md .github/ABOUT.md
git commit -m "Rename to prevent override"
git push
```

**Option 3: Symlink (if you want both)**

```bash
# Make .github/README.md a symlink to root
cd .github
ln -s ../README.md README.md
git add README.md
git commit -m "Symlink README"
git push
```

Note: GitHub renders symlinks, but some Git clients handle them poorly on Windows.

## When .github/README.md Is Intentional

Sometimes you **want** different content on the landing page vs. what developers see locally:

| Use Case | Root README | .github/README |
|----------|-------------|----------------|
| Internal tool | Technical setup | Public-facing overview |
| Template repo | "How to use template" | "What this template does" |
| Monorepo | Navigation/workspace docs | Project overview |

## Verification

```bash
# Check if override exists
ls -la .github/README.md

# See what GitHub will display
# Push and check the repo landing page
```

## Common Symptoms

- "I updated README but GitHub shows old content"
- "My README looks different on GitHub vs. locally"
- "README changes aren't showing up"

## Related Files That Override

Similar override behavior exists for:

- `.github/CONTRIBUTING.md` → overrides root `CONTRIBUTING.md`
- `.github/CODE_OF_CONDUCT.md` → overrides root `CODE_OF_CONDUCT.md`
- `.github/SECURITY.md` → overrides root `SECURITY.md`
- `.github/SUPPORT.md` → overrides root `SUPPORT.md`

## Verification Checklist

- [ ] Check if `.github/README.md` exists
- [ ] Determine if override is intentional
- [ ] Delete, rename, or symlink as appropriate
- [ ] Verify on GitHub after push

## Related Skills

- `github-wiki-flat` — Wiki structure gotchas
