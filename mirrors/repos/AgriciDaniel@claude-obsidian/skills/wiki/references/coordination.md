# External editors and multiple machines

The local mutation lock serializes cooperating claude-obsidian writers on the
selected local vault. Expected SHA-256 preconditions detect changed targets at
inspection/apply time. Obsidian, other editors, sync clients, and other machines
do not acquire that lock. A file can still change after a check. This is not a
cross-device merge or distributed-lock protocol.

For an operation that changes notes or ledgers:

1. Finish edits and wait for sync to settle on every device. Keep a recoverable
   backup. Select one machine as the only writer for the operation.
2. Pause overlapping plugin writers and background checkpoints. Avoid editing
   targeted files in Obsidian while a reviewed transaction applies.
3. Read and hash targets, inspect once, and apply the exact approved bundle.
   Exit 75 requires a fresh read and rebuilt plan; do not retry stale writes.
4. Verify the receipt, changed paths, source bytes, and deterministic lint before
   resuming sync. Retain operation evidence outside the syncing vault if needed.
5. Resume other writers only after every device converges on the verified bytes.
   Conflicted copies need a separate evidence-preserving review, not last-writer
   overwrite. Never erase a raw payload to make a sync conflict disappear.

If sync interrupts an apply, stop competing writers, preserve the complete vault
and `.vault-meta/` journal together, and use `transaction recover`. Do not sync
half a journal independently of its targets/backups. Do not force a stale lock
until an operator has independently confirmed that no writer is alive.

These steps reduce overlap; no live cloud-sync or network-filesystem convergence
is claimed by offline tests. A REST ETag protects one transport operation and
cannot replace the multi-file journal, local hashes, or single-writer agreement.
Filesystem/CLI reads remain preferable when an optional transport adds no value.
