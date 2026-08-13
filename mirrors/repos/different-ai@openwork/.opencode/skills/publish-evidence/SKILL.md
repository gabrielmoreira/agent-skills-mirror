---
name: publish-evidence
description: Publish evidence, publish all tapes, update PR verification, audit a red tape. Use for the human-verification layer after @openwork/testkit runs.
---

# Skill: Publish Evidence

The orchestrator owns this human-verification step. Publishing makes the
agent-first verdict inspectable; it never decides pass/fail and never reruns a
test.

## Make every claim auditable

- Show the spec name and verdict, each claim's assertion or fact, the relevant
  frames, the source tape, and the reproduction command.
- Require one sticky-comment section per claimed spec. If a claim has no visible
  tape section, report the PR `Incomplete`.
- Keep both `<!-- photo-roll -->` and `<!-- fraimz -->` markers.

## Publish the PR head

After a multi-spec run, publish each tape whose `gitSha` matches the PR head,
once per roll:

```bash
pnpm evals --publish --pr <n> --roll <dir|name>
```

`evals --publish` judges pending vision claims on the selected tape, then
publishes it. It publishes existing `@openwork/testkit` tapes, not legacy
flows, and never reruns tests.

- Omitting `--roll` selects the most recent roll; pass `--roll` explicitly
  when several rolls exist so each spec's tape is published deliberately.
- Publishing replaces the sticky comment with the selected roll. Confirm the
  final comment shows the spec and verdict you intend reviewers to see.
- Exit codes: `0` published, `1` failed claims published (or publish failed),
  `2` pending claims still need judging (set a vision key and rerun).

## Refuse misleading evidence

- Never use `--force` to hide a SHA mismatch. Re-run the spec on the PR head.
- Use `--force` only to deliberately publish a historical or red tape. The
  output is annotated; call the exception out explicitly. Red tapes are valid
  human-verification artifacts and should be published when they explain a
  `Failed` or `Incomplete` verdict.
- Read `BLOB_READ_WRITE_TOKEN` from the environment or the Infisical fallback.
  Without it, still post verdicts with a no-screenshots note.
