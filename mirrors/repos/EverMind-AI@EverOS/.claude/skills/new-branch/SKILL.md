---
name: new-branch
description: Create a branch following the project's GitFlow Lite model
---

# /new-branch

Cut a new branch under the GitFlow Lite model.

## Branch model

```
master  = released / stable (tagged on release; protected)
dev     = integration branch (protected)
feat/*  = cut from dev  → PR → merge into dev
fix/*   = cut from dev  → PR → merge into dev
hotfix/* = cut from master → merge into master AND synced into dev (double merge)
release  = dev → master + tag on master (no separate release branch)
```

## Steps

1. Ask (or infer) the change type: `feat`, `fix`, or `hotfix`.
2. Pick the parent:
   - `feat/*`, `fix/*` → branch from **`dev`**.
   - `hotfix/*` → branch from **`master`**.
3. Update the parent first:
   ```bash
   git checkout <parent>
   git pull --ff-only
   ```
4. Create the branch with a kebab-case slug:
   ```bash
   git checkout -b feat/<short-slug>
   ```
5. For a `hotfix`, remember it must later merge into **both** `master` and `dev`.

## Naming

- `feat/add-agentic-rerank`, `fix/empty-profile-crash`, `hotfix/lancedb-conn-leak`.
- Lowercase, hyphen-separated, no spaces, concise.

Never commit directly to `master` or `dev` — always via a branch + PR.
