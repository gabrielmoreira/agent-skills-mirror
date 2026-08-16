# Recovery and rollback

Recovery is evidence-driven. Rollback is non-destructive and proposal-only.

## Run states

Use the implementation's explicit phase enum and allowed transition graph. Conceptually the run advances through:

```text
initialized
→ preflighted
→ scanned
→ clustered
→ staged/visibility-verified
→ candidate-built
→ manifest-frozen
→ pre-refresh-audited
→ refresh-authorized
→ refreshed
→ post-refresh-audited
→ ui-validated
→ finalized
```

A failure state may be recorded from an active phase. Exact enum names in code are authoritative; do not invent a transition that `state.py` rejects.

## Locking

Acquire the task lock before mutating state, journal, or run artifacts.

A lock record binds task id, owner token, pid, host, acquisition time, and expiry/staleness information. Re-entrant use is allowed only for the same owner token where the implementation permits it.

Never break a lock merely because it is old. Stale-lock recovery requires both:

- expiry/staleness under the configured policy; and
- evidence that the recorded process is no longer alive.

On Windows, process liveness must use a non-signalling process query. Do not call `os.kill(pid, 0)` on Windows.

## Recovery scan

To recover a run:

1. validate task id and canonical run root;
2. read the journal strictly;
3. reject malformed, reordered, duplicate, truncated, or digest-invalid events;
4. validate each transition against the allowed graph;
5. recompute every referenced artifact digest;
6. validate parent lineage and source binding;
7. determine the highest contiguous verified phase;
8. report orphaned or future artifacts without adopting them;
9. write a recovery event only while holding the lock and only when the implementation authorizes it.

If journal and artifacts disagree, choose the lower proven phase. Never skip a failed gate because a later file exists.

## Orphans and tamper signals

Treat these as manual-review or failure conditions:

- artifact exists but is absent from lineage;
- lineage references a missing file;
- raw file hash differs from recorded hash;
- parent digest differs;
- source digest changed;
- frozen write-once path contains conflicting bytes;
- two attempts claim the same destination/report paths;
- a live lock belongs to another owner;
- a finalization record exists but any bound evidence no longer verifies.

Retain all such artifacts for diagnosis.

## Rollback proposal

Generate a strict JSON proposal; do not execute it automatically. The proposal may:

- identify the highest verified source artifact for the requested target phase;
- propose copying it to a new, absent destination;
- list expected input and output hashes;
- list artifacts that remain retained;
- explain why an in-place overwrite is prohibited.

It must not:

- delete source, candidate, destination, diagnostics, journal, audits, or evidence;
- overwrite an existing path;
- reduce required citation occurrences or acceptance counts;
- rewrite history or remove failed attempts;
- claim that a proposal has been executed.

## Reporting

A recovery/rollback result should include:

- requested target phase;
- highest verified phase;
- lock status;
- verified lineage chain;
- orphaned/tampered artifacts;
- proposal path and digest, if created;
- explicit statement that no files were deleted or overwritten.
