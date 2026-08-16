# Live Refresh protocol

Read this file only after the user has explicitly authorized the exact Word/Zotero integration attempt. This reference does not itself grant authorization.

## Required authorization statement

Before execution, establish all of the following in the current conversation or approved run record:

- the exact candidate and protected source;
- the exact destination, report, diagnostic, and authorization files;
- permission to launch Microsoft Word;
- permission to run `refresh_word_zotero.ps1` once;
- permission to invoke `ZoteroRefresh` once;
- whether the restricted read-only Local API visibility check is permitted;
- confirmation that no Zotero write is requested by the wrapper.

If any item is absent or ambiguous, stop. Do not broaden authorization from “validate the script,” “finish the Skill,” or “continue the workflow.”

## Pre-execution gates

1. Inventory exact files and recompute their hashes.
2. Load and verify the frozen manifest, pre-Refresh audit, and Refresh authorization.
3. Verify protected source and candidate size/SHA-256.
4. Verify destination/report/diagnostic paths are exactly authorized, pairwise distinct, and appropriately absent or idempotent.
5. If enabled, run only the restricted read-only visibility check against `http://127.0.0.1:23119`.
6. Parse the PowerShell wrapper and confirm the static wrapper contract tests still pass.
7. Confirm that no prior incomplete attempt or live lock is active.

Any failure cancels the attempt before Word COM creation.

## Wrapper behavior

The wrapper must:

- perform Python authorization and visibility gates before Word COM creation;
- copy candidate to destination, never source to destination by mutation;
- create its own Word application instance;
- snapshot and later restore `Visible` and `DisplayAlerts`;
- open only the authorized destination;
- invoke `ZoteroRefresh` exactly once;
- never retry the macro automatically;
- wait for stable field fingerprints rather than assuming immediate completion;
- save and close the destination;
- re-check source and candidate hashes;
- write the JSON report atomically;
- create a diagnostic document copy only from the outer failure handler.

Do not wrap execution in an external retry. A second attempt requires a new attempt id and new authorization.

## Failure handling

On failure:

- preserve the source, candidate, destination, report fragments, diagnostic copy, logs, and journal;
- do not delete or overwrite evidence;
- report whether Word was created, whether the macro call began, and whether destination bytes changed;
- mark the state failed through an allowed journal transition;
- propose recovery or a copy-only rollback; do not perform destructive cleanup.

## Post-execution gates

A wrapper exit code or “success” text is not enough. Verify:

1. report schema and authorization binding;
2. exactly one macro invocation;
3. source and candidate remained unchanged;
4. destination exists and matches report size/SHA-256;
5. post-Refresh static audit passes manifest counts;
6. citation and bibliography UI evidence are collected separately on disposable copies and cancelled;
7. finalization verifies and freezes write-once.

## Mandatory disclosure

The completion report must state exactly which live actions occurred:

- Word launched: yes/no;
- wrapper executed: yes/no;
- `ZoteroRefresh` invoked: zero/one;
- Local API contacted: yes/no and exact origin;
- Zotero modified: yes/no;
- diagnostic copy retained: path or none.
