# addvalue — examples

## Example A — Upstream library (Hatch)

**Input:** `/addvalue pypa/hatch`

**Map:** Build backend, `pathspec` VCS excludes, active issues.

**Bank (abbrev):**

| id | kind | score | note |
|----|------|-------|------|
| nested-gitignore | bug | 18 | #304 — subdirectory projects disagree with Git |
| env-prune-dir | bug | 11 | #737 — draft PR already exists → skip |
| better-error-vcs | ux | 12 | opaque exclude surprises |

**Winner:** nested-gitignore (#304)  
**Why:** Maintainer-acknowledged; no open PR; clear tests; high packaging impact.

**Gate:** Implement locally; wait for `Take pypa/hatch#304`.

---

## Example B — Local app (no GitHub)

**Input:** `/addvalue ~/projects/myapp`

**Friction:** First-run needs 4 env vars with no `.env.example`; Windows path breaks on screenshot export.

**Winner:** `.env.example` + validate-on-boot errors naming the missing key.  
**Why:** Unblocks every new clone; tiny diff; demoable.

---

## Example C — With Ollama partner

**Input:** `/addvalue . --ollama`

1. Agent maps repo + top 15 issue titles  
2. One `/ollama` call ranks opportunities  
3. Agent merges scores, picks winner, implements if local-owned  
4. Report shows both agent and GLM rankings when they disagree

---

## Example D — Reject vanity

**Candidate:** Fix typo in CONTRIBUTING.  
**Reject:** novelty 1, impact 1 — fails addvalue bar even if “easy merge.”
