---
name: pr
description: Open a GitHub PR targeting the correct branch with the project template
---

# /pr

Open a pull request on GitHub using the `gh` CLI and the repo's PR template.

## Steps

1. Confirm the branch and target:
   - `feat/*`, `fix/*` → base **`dev`**.
   - `hotfix/*` → base **`master`** (then a follow-up PR/sync into `dev`).
2. Ensure local checks pass first:
   ```bash
   make ci
   ```
   Do not open a PR with failing lint/tests.
3. Push the branch:
   ```bash
   git push -u origin HEAD
   ```
4. Create the PR, filling the template
   ([.github/PULL_REQUEST_TEMPLATE.md](../../../.github/PULL_REQUEST_TEMPLATE.md)):
   ```bash
   gh pr create --base dev --fill-first
   ```
   Then edit the body to complete each section:
   - **Summary** — what changed and why.
   - **Area** — tick the relevant box (architecture / benchmark / use case /
     docs / DX / CI-build-release).
   - **Verification** — paste the commands you ran (`make ci`, manual checks).
   - **Checklist** — tick honestly; don't tick boxes you didn't satisfy.
   - **Notes for Reviewers** — anything subtle.

## Notes

- Keep the PR scoped to one area. Split unrelated changes.
- If `make ci` was not fully run, say so in Verification rather than implying it passed.
- A `hotfix` is not done until it has landed on **both** `master` and `dev`.
