---
title: Version control operations
applicability:
- When a change's base or revision must be identified from version control
- When a merge or rebase must be resolved
- Before version-control state is altered
x-claim-provenance:
- claim: Software configuration management includes configuration identification, change control, status accounting, and build and release management.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
- claim: A forced push replaces a remote ref that is not an ancestor of the local ref and can cause the remote repository to lose commits that others have built on.
  source: https://git-scm.com/docs/git-push
- claim: The merge base is the best common ancestor of two commits, the point a three-way merge measures each side's changes from.
  source: https://git-scm.com/docs/git-merge-base
- claim: A committed secret is revoked or rotated first; rewriting history does not remove it from existing clones and forks.
  source: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
---

Establish the repository's version-control state before relying on it: the checked-out branch or detached revision, the upstream it tracks, uncommitted and untracked material, and any merge, rebase, or stash in progress. A change's base is the common ancestor it diverged from, the merge base with its target, not the target's current tip; comparing against the tip folds later unrelated work into the change under review. The working tree, the staged index, the last commit, and a built artifact can each describe a different state, so bind every observation and verdict to the one it came from.

A commit records one coherent change together with the reconciliation and evidence that change required. Its message states what changed and, where a later reader could not otherwise see it, why, and carries no process narration or tool output. Recording, amending, or tagging is a durable effect of its own, taken only under the request or standing instructions that authorize it and in the project's recorded conventions for branches, messages, sign-off, and linked identifiers.

A hook, required check, or protected-branch rule is verification the project adopted: its failure is a result to classify, and bypassing it turns an unverified change into one that reads as verified. Rewriting history that another person, machine, or branch may already hold, by a forced push, a rebase of a shared branch, or an amendment of a pushed commit, discards the commits they built on and is destructive beyond the workspace; it needs explicit authority for that exact operation and target. Pushing, opening or updating a change request, and publishing a tag are externally visible effects with authority of their own.

Resolve a merge or rebase conflict by establishing what each side intended, from its commits, tests, and consumers, and producing a result that preserves both contracts; taking one side, or the syntactically simpler union, silently reverts the other. Verify the merged result with evidence sensitive to both changes, not only the checks that passed on each side alone.

A secret already committed is exposed to every holder of that history, and a later commit that removes it changes nothing about that exposure: revoke or rotate it first, and treat removing it from history as a separate destructive operation that still leaves existing clones and forks holding it.
