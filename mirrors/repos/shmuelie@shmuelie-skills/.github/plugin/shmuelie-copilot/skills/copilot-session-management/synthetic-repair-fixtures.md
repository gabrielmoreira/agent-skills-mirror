# Synthetic repair fixtures for session integrity

These fixtures are **fictional**. They are not copied from any real Copilot CLI
session and they do not claim to represent a stable published event schema.
They are small, line-oriented models for reasoning about safe repair behavior.

Use them only to answer questions like "what is the safest disposition when a
log is truncated or references dangle?" Do **not** replay them into real user
session folders.

## Fixture 1 - Missing result after a request

```json
{"line":1,"sessionId":"S-001","eventId":"evt-1","kind":"user","timestamp":"2026-08-01T10:00:00Z","text":"Run the tests"}
{"line":2,"sessionId":"S-001","eventId":"evt-2","kind":"toolRequest","requestId":"req-7","tool":"powershell","timestamp":"2026-08-01T10:00:01Z","command":"dotnet test"}
{"line":3,"sessionId":"S-001","eventId":"evt-3","kind":"assistant","timestamp":"2026-08-01T10:00:02Z","text":"Waiting for test output"}
{"line":4,"sessionId":"S-001","eventId":"evt-4","kind":"toolResult","requestId":
```

**Expected diagnostic:** trailing JSON is truncated, and the final visible
request/result pair is incomplete.

**Safe disposition:** back up first. A syntactically valid prefix is not enough
to authorize deletion: repair or remove the tail only when the supported
version's pairing and reference rules permit it. Keep the outcome of `req-7`
unknown unless verified evidence establishes it; the tool may have completed
before its result was recorded. Restore a genuine result from a verified backup
if available, but never fabricate success, failure, or interruption. Do not
automatically rerun a state-changing request. If unresolved requests cannot be
represented safely, recover from a known-good backup or start a fresh session.

## Fixture 2 - Equal timestamps must keep original order

```json
{"line":11,"sessionId":"S-002","eventId":"evt-10","kind":"toolRequest","requestId":"req-9","timestamp":"2026-08-01T10:05:00.000Z","tool":"rg","pattern":"TODO"}
{"line":12,"sessionId":"S-002","eventId":"evt-11","kind":"toolResult","requestId":"req-9","timestamp":"2026-08-01T10:05:00.000Z","exitCode":1}
{"line":13,"sessionId":"S-002","eventId":"evt-12","kind":"assistant","timestamp":"2026-08-01T10:05:00.000Z","text":"No matches found"}
```

**Expected diagnostic:** timestamps alone are not enough to reconstruct
causality because all three records are equal.

**Safe disposition:** preserve the original line order. Do not sort or
reserialize the file just to make timestamps "look ordered."

## Fixture 3 - Interleaved records from different sessions

```json
{"line":20,"sessionId":"S-100","eventId":"evt-20","kind":"user","timestamp":"2026-08-01T11:00:00Z","text":"Fix build break"}
{"line":21,"sessionId":"S-200","eventId":"evt-88","kind":"user","timestamp":"2026-08-01T11:00:00Z","text":"Summarize PR"}
{"line":22,"sessionId":"S-100","eventId":"evt-21","kind":"toolRequest","requestId":"req-1","timestamp":"2026-08-01T11:00:01Z","tool":"powershell","command":"dotnet build"}
{"line":23,"sessionId":"S-200","eventId":"evt-89","kind":"assistant","timestamp":"2026-08-01T11:00:01Z","text":"Reviewing pull request"}
```

**Expected diagnostic:** the records belong to different sessions. This is an
ownership inconsistency if the file is supposed to contain one session, but may
be valid in an explicitly supported multi-session export. Timestamps do not
establish the ownership rules.

**Safe disposition:** preserve each source session's record order and identity.
Use only a supported merge, split, or restore operation with known reference
rules; a global timestamp sort is not a repair. Stop if version-specific
ownership rules are unclear rather than inventing a replacement stream.

## Fixture 4 - Dangling reference after removal or compaction

```json
{"line":30,"sessionId":"S-300","eventId":"evt-30","kind":"assistant","timestamp":"2026-08-01T12:00:00Z","text":"Created repair plan"}
{"line":31,"sessionId":"S-300","eventId":"evt-31","kind":"checkpoint","checkpointId":"cp-1","references":["evt-30","evt-32"],"timestamp":"2026-08-01T12:00:01Z"}
{"line":32,"sessionId":"S-300","eventId":"evt-32","kind":"assistant","timestamp":"2026-08-01T12:00:02Z","text":"Will compact history now"}
```

Assume `evt-32` is removed during compaction without updating `cp-1`.

**Expected diagnostic:** `cp-1` now points to a missing record, so the repair
introduced a dangling cross-reference.

**Safe disposition:** restore the missing record from backup, or remove/repair
the checkpoint only if the current CLI version clearly documents that reference
format. If the schema is unknown, stop instead of guessing.
