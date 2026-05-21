# PR Description Format Guide

The format every generated PR description must follow. Read before writing.

---

## Required Sections

### Summary

One to two sentences. What does this PR do and why?

- Use present tense, active voice: "Adds Redis caching to reduce database load on high-traffic endpoints."
- Include the motivation if it's clear from the diff or commits: "Fixes a race condition in the session store that caused intermittent 401s under load."
- Do not start with "This PR" or "This commit"

Good:
```
Adds Redis caching for user session lookups. Reduces average response time on /api/me from 340ms to 12ms by eliminating a database query on every authenticated request.
```

Bad:
```
This PR adds caching. It should improve performance.
```

---

### Changes

A bulleted list of what changed. One bullet per logical change.

Rules:
- Start each bullet with a verb: "Adds", "Removes", "Moves", "Fixes", "Refactors", "Updates"
- Be specific: file names, function names, config keys where relevant
- Group related changes under a sub-header if there are more than 6 bullets

Good:
```
- Adds `src/cache/redis.ts` with `get`, `set`, and `invalidate` methods
- Wraps `UserService.getById()` with a 5-minute Redis cache
- Removes the inline `Map` cache in `auth.middleware.ts` (replaced by Redis)
- Updates `.env.example` with `REDIS_URL` and `REDIS_TTL_SECONDS`
```

Bad:
```
- Updated files
- Fixed the bug
- Added new feature
```

---

### Testing

How to verify this PR works. Actionable steps someone else can follow.

Format options:

**For code changes with clear test steps:**
```
- Run `npm test` — all tests pass
- Start the server and hit `GET /api/me` 10 times rapidly — confirm only 1 DB query appears in logs
- Check Redis with `redis-cli monitor` while making requests — confirm cache hits after the first request
```

**For simple refactors with no behavior change:**
```
- Run `npm test` — no regressions
- No behavior change expected
```

**For infrastructure / config changes:**
```
- Deploy to staging and confirm the service starts without errors
- Check CloudWatch logs for `[redis] connected` on startup
```

Omit this section if the change is purely documentation or a trivially safe refactor with no observable behavior.

---

### Screenshots (optional)

Only include if there are UI changes in the diff. Skip entirely for backend-only or infrastructure changes.

```
Before: [paste screenshot or describe]
After: [paste screenshot or describe]
```

---

### Linked Issues (optional)

Only include if the PR closes or references an issue.

```
Closes #123
Related to #456
```

Use GitHub closing keywords: `Closes`, `Fixes`, `Resolves` to auto-close on merge.

---

## What to Omit

- Do not list every file changed — that is what the diff is for
- Do not repeat the commit messages verbatim
- Do not include "TODO" items or future work unless the reviewer needs to know about them
- Do not add "cc @person" — leave that for reviewers
- Do not add a changelog entry — that belongs in a separate file
- Do not include a "Why" section — fold motivation into the Summary

---

## Length Guide

| PR size | Description length |
|---------|-------------------|
| 1-3 files changed | 5-10 lines total |
| 4-10 files changed | 10-20 lines total |
| 10+ files changed | 20-40 lines total, use sub-headers in Changes |

Longer is not better. A clear 8-line description beats a padded 40-line one.

---

## Title Format

Imperative mood, present tense, under 72 characters.

Good:
- `Add Redis caching for session lookups`
- `Fix race condition in auth middleware`
- `Migrate user service to TypeScript`
- `Remove deprecated /v1 API endpoints`

Bad:
- `Added caching` (past tense)
- `This PR fixes the auth bug that was causing issues` (too long, filler)
- `WIP: caching stuff` (not ready to merge)
- `JIRA-1234: add caching` (ticket reference in title)
