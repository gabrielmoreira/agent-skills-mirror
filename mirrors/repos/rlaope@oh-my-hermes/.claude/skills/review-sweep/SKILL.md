---
name: review-sweep
description: >-
  Review oh-my-hermes pull requests that have not been reviewed at their
  current head commit. Run manually to sweep the open backlog, or pass a number
  to review one PR. Applies the repository's REVIEW.md policy and posts
  findings as a GitHub review with inline comments.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
---

# Review sweep

The procedure lives in [`docs/REVIEW-SWEEP.md`](../../../docs/REVIEW-SWEEP.md).
Read that file and follow it.

It is kept there rather than here because Codex, Hermes handoffs, and generic
executor profiles run the same sweep, and `AGENTS.md` requires that no single
executor own a shared surface. This file exists so the procedure is reachable
as `/review-sweep`; it deliberately holds no rules of its own, so there is
nothing here to drift out of sync with the real one.

Start by reading, in this order:

```sh
cat docs/REVIEW-SWEEP.md
cat REVIEW.md
```

Two things worth knowing before you open the procedure, because they are what
the sweep gets wrong most often:

- Never review from the diff alone. This repo's defects are about consistency
  with code that is *not* in the diff, so the procedure checks the PR out into
  a worktree and runs the gates.
- The default is a **dry run**. A review is a public, notifying write to
  someone else's work; print the findings and stop for confirmation unless the
  invocation carried `--apply`.

Arguments pass through verbatim: a bare number reviews one PR, `--drafts` and
`--mine` widen the sweep, `--apply` posts.
