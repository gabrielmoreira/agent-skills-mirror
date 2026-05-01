---
name: gh-address-comments
description: Fetch all review comments and threads on the current branch's open GitHub PR using the gh CLI, present a numbered summary, and address the ones the user selects.
argument-hint: "[comment numbers to address (optional; if omitted, shows all and asks)]"
user-invocable: true
---

# Address PR Review Comments

Fetch all review comments for the current branch's open PR, present a numbered summary, and apply fixes for the comments the user selects.

## Prerequisites

Verify `gh` authentication before doing anything else:

```
gh auth status
```

If unauthenticated, ask the user to run `gh auth login`, then stop.

## Workflow

### 1. Resolve the PR

```
# if the user specified a PR number or URL:
gh pr view <number-or-url> --json number,url,headRefName

# otherwise (current branch):
gh pr view --json number,url,headRefName
```

Extract `owner` and `repo` from the returned `url` field — PR URLs have the form `https://github.com/<owner>/<repo>/pull/<number>`, so split on `/` to get the 4th and 5th segments. These are the base (target) repository coordinates, and are reliable even for cross-fork PRs.

### 2. Fetch comments

Run the following to get all review threads (inline) and conversation comments:

```
gh api graphql -f query='
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      number url title state
      comments(first:100) {
        nodes { id body author { login } createdAt }
      }
      reviews(first:100) {
        nodes { id state body author { login } submittedAt }
      }
      reviewThreads(first:100) {
        nodes {
          id isResolved isOutdated path line
          comments(first:100) {
            nodes { id body author { login } createdAt }
          }
        }
      }
    }
  }
}' -F owner=<owner> -F repo=<repo> -F number=<pr-number>
```

If GraphQL is unavailable, fall back to:

```
gh pr view <pr-number> -R <owner>/<repo> --json reviews,reviewRequests,comments
```

Note: the fallback output does not include thread-level `isResolved`/`isOutdated` fields. In fallback mode, treat all returned comments as actionable.

### 3. Present a numbered summary

List every unresolved comment/thread (or all comments in fallback mode) with a number, author, file/line (if inline), and a one-line description of the requested change. Example:

```
1. @alice [src/auth.ts:42] — Use bcrypt instead of MD5 for password hashing
2. @bob — Nit: rename `doThing` to `processPayload` for clarity
3. @alice [src/auth.ts:88] — Add input validation before DB query
```

### 4. Ask which to address

If the user already provided numbers in the skill argument, proceed with those. Otherwise ask:

> Which comments should I address? (e.g. "1 3" or "all")

### 5. Apply fixes

For each selected comment:

- Read the relevant file and context.
- Apply the requested change.
- Note any cases where the comment is unclear or the fix has side effects — confirm with the user before proceeding.

### 6. Summarize

After all fixes, provide a brief summary listing which comments were addressed and any that were skipped (with reason).
