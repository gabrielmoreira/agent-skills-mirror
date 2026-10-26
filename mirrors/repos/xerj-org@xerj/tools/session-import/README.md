# Import one Claude Code transcript for decision retrieval

`xerj sessions import` is the explicit preparation step for a single Claude Code
JSONL transcript. It runs locally, calls no model or node, and exports text
turns through XERJ's existing native PII plugin. Review the export, then give its
folder to ordinary `xerj autoindex`. This is the first scoped part of
[#1793](https://github.com/xerj-org/xerj/issues/1793), not automatic transcript
discovery, a multi-client adapter, a live conversation view or incremental sync.

## Try the synthetic example

From the repository root with a built binary and Python 3:

```sh
(cd engine && cargo build --locked --release -j 32 -p xerj-server)
python3 tools/session-import/smoke.py --binary engine/target/release/xerj
```

The example uses only the committed synthetic transcript, prepares a private
export, starts a private loopback node on unused ports, dry-runs autoindex,
indexes and queries the decision, repeats indexing to check idempotence, then
checks graceful restart. It removes its own temporary data at exit. It neither
contacts nor removes any existing node/index. The node runs in default lexical
mode; indexing explicitly uses `--no-semantic`. No semantic-quality claim is made.

## Import your own archived transcript

Choose a stopped/archived file explicitly; this command does not inspect your
home directory or discover other sessions. Use a private destination directory
whose parent you control. The output file must not exist, even if empty.

```sh
set -eu
SESSION_EXPORT=$(mktemp -d)
xerj sessions import --format claude-code \
  --input /path/to/archived-session.jsonl \
  --output "$SESSION_EXPORT/records.jsonl"
```

Success prints a JSON summary containing the schema version, exported-record
count, physical source-line count, skipped-record count, skipped-block count,
and SHA-256 of the source bytes consumed and the exact exported bytes. Blank
lines count as source lines but not skipped records. Skipped blocks count the
non-text blocks inspected in non-meta user/assistant messages. Skipped records
count other top-level records, `isMeta` messages and messages with no text.

The redactor handles the existing email, IP, credit-card, US SSN and phone
patterns. It does not remove every credential, person name, repository path or
private fact. Check the exported JSONL before indexing it. Raw tool payloads,
tool results, thinking and arbitrary message metadata are excluded, including
fields the importer does not recognize. The importer does not change the input.

After review, against your running node:

```sh
set -eu
xerj autoindex "$SESSION_EXPORT" --prefix session-history --dry-run
# Check the estimate and prefix ownership before indexing.
xerj autoindex "$SESSION_EXPORT" --prefix session-history
xerj autoindex map --prefix session-history
xerj search --prefix session-history "why did we drop polling"
```

Only put prepared exports in that folder. Ordinary `autoindex` still accepts
raw JSONL; pointing it at the original transcript folder does **not** activate
this preparation or redaction. Use a prefix you own; follow the normal
autoindex estimate/approval contract for large exports.

## Record and source contract

One output line is one text-bearing `user` or `assistant` event. `message.content`
may be a string or an array of `text`/recognized non-text blocks. Text blocks
retain their order. Each output object has the same key set:

| Fields | Meaning |
|---|---|
| `session_schema_version`, `session_format` | Export schema 1, `claude-code` |
| `id`, `session_id`, `message_id` | Canonical validated UUIDs; ID is session/message UUID |
| `parent_id` | Explicit `parentUuid`, or null; it may reference a skipped event |
| `role`, `title`, `body` | Event role and redacted text; title is the first text line, capped at 120 characters |
| `source_file`, `source_line`, `source_byte_offset` | Redacted original basename, 1-based physical line, 0-based byte offset |
| `files` | Redacted `file_path` values explicitly requested by Read/Write/Edit/MultiEdit blocks in this event |
| `cwd`, `git_branch`, `timestamp` | Explicit metadata or null; timestamp must be RFC 3339 |
| `is_sidechain`, `is_summary` | Explicit branch/compaction flags, default false |

File paths are references in a tool request, not proof that a change succeeded.
No files are opened through these references, and no commit is inferred from
prose, shell commands or branch names. File references in tool-only events are
not exported in this text-only version. Autoindex citations still identify the
prepared file/record; the `source_*` fields locate the original event, whose
byte offset is meaningful only for that archived source digest. Redaction may
change the original filename/path spelling. Query the stored record with
`_source: true` to read all source metadata.

The importer preserves all text-bearing branches in file order. It does not
reconstruct the active conversation, merge forks or claim that a discarded
alternative is current. Compaction summaries are marked, not treated as original
turns. Non-text attachments are not OCRed, and tool results are not searched.

## Refusals, reruns and limits

Exit 0 is a complete export; 2 is invalid CLI usage; 1 is an import or
publication/reporting error. If stdout fails after publication, stderr explicitly
says the export was published: inspect and reuse that complete file rather than
expecting a second import to overwrite it. Diagnostics name the line and schema problem, without
echoing the source payload. Invalid JSON (including a truncated tail), UUIDs,
roles, timestamps or flags, unsupported content blocks, mixed session IDs,
repeated message UUIDs and a changed source refuse the whole export. There is
no fallback to unredacted generic JSONL/text. Metadata-only input also refuses.

Input and output are capped at 512 MiB each, source lines at 1 MiB including
newline, collected turn text at 256 KiB and message UUIDs at 100,000. These are
admission limits, not a measured peak-memory claim. Parsing is line by line.
The temporary output contains only redacted, allowlisted records, is hidden
and is removed on ordinary failure. It is synced before no-clobber publication;
the tempfile implementation may leave an extra hidden hard link on platforms
that need a link/unlink fallback or after an interruption. This is not a
transactional directory-durability guarantee. On Unix the new export has mode 0600. No existing output,
including a concurrent writer's file or a symlink, is replaced.

An unchanged import rerun refuses the existing output; reuse that snapshot for
unchanged autoindex reruns. For an updated source or parser version, prepare a
new export folder and index it under a new prefix/state directory. This version
does not refresh or remove a previous snapshot. Retain the old snapshot/index
until the new one has been verified, then use the normal ownership-aware
autoindex remove workflow. A killed process can leave a hidden sanitized temp
file; it is not a complete export. Use a new destination after interruption.

## Format evidence and verification boundary

Claude Code documents its on-disk JSONL as an internal format that can change:
[session storage](https://code.claude.com/docs/en/sessions#where-transcripts-are-stored).
This adapter supports the explicit shapes above, not every client version,
`stream-json`, rendered `/export` text, Codex or Cursor logs.

Reference retrieved before implementation: Anthropic's MIT-licensed SDK at
`0e89b298e771259378a6cd3734e00d323dff5703`,
[`sessions.py:897–929`](https://github.com/anthropics/claude-agent-sdk-python/blob/0e89b298e771259378a6cd3734e00d323dff5703/src/claude_agent_sdk/_internal/sessions.py#L897-L929)
parses typed UUID-bearing events, and
[`sessions.py:1248–1285`](https://github.com/anthropics/claude-agent-sdk-python/blob/0e89b298e771259378a6cd3734e00d323dff5703/src/claude_agent_sdk/_internal/sessions.py#L1248-L1285)
distinguishes visible messages and session identities. Approach only; no code
copied. XERJ intentionally refuses malformed input instead of silently skipping
it, and exports branch flags rather than choosing the SDK's active chain.

All checked-in fixtures are synthetic. No real personal transcript or real
Claude client release is claimed validated by those fixtures. Unit and CLI
tests cover redaction, provenance, filtering, size limits, malformed tails,
unsupported shapes, no-clobber publication and recovery.
