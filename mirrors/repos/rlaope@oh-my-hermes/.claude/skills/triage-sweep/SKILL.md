---
name: triage-sweep
description: >-
  Backfill labels across oh-my-hermes issues and pull requests. Run manually to
  sweep everything currently unlabeled, or pass a number to triage one item.
  Use when issues and PRs have accumulated without labels, after adding a new
  label to .github/labels.yml, or before a release when the backlog needs to be
  readable by area.
allowed-tools: Bash, Read, Grep, Glob
---

# Triage sweep

The procedure lives in [`docs/TRIAGE-SWEEP.md`](../../../docs/TRIAGE-SWEEP.md).
Read that file and follow it.

It is kept there rather than here because Codex, Hermes handoffs, and generic
executor profiles run the same sweep, and `AGENTS.md` requires that no single
executor own a shared surface. This file exists so the procedure is reachable
as `/triage-sweep`; it deliberately holds no rules of its own, so there is
nothing here to drift out of sync with the real one.

Start by reading, in this order:

```sh
cat docs/TRIAGE-SWEEP.md
cat .github/labels.yml
```

Two things worth knowing before you open the procedure, because they are what
the sweep gets wrong most often:

- `.github/labels.yml` is the **entire** allowlist. Never apply a label that is
  not in it, and never create one on the fly.
- The default is a **dry run**. Print the plan and stop for confirmation unless
  the invocation carried `--apply`.

Arguments pass through verbatim: a bare number triages one item, `sync-labels`
reconciles the repository against the manifest, `--closed` widens the sweep,
`--apply` writes.
