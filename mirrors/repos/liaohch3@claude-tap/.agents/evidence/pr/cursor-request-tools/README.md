# Cursor request tools / system backfill evidence

## Problem shape

Cursor transcript-only sessions synthesize Anthropic-shaped requests from
`agent-transcripts/*.jsonl`. Those files do not store the request `tools`
catalog or system prompt, so the viewer Request / Trace panes had an empty
Tools section even when the assistant called tools.

## Real-trace recreation

From the repo root (requires the source Cursor transcript on this machine):

```bash
uv run python .agents/evidence/pr/cursor-request-tools/seed_and_capture.py
uv run python scripts/check_screenshots.py .agents/evidence/pr/cursor-request-tools/
```

The seed script:

1. Copies the real nested transcript
   `~/.cursor/projects/Users-youngcan-claude-tap/agent-transcripts/0b95c4b6-03e2-4780-8c3a-124f43625297/0b95c4b6-03e2-4780-8c3a-124f43625297.jsonl`
2. Copies `meta` plus the longest `role=system` JSON blob from the matching
   Cursor `store.db` (not the full protobuf blob store)
3. Imports through `import_cursor_transcripts()` into
   `.traces/cursor-request-tools/traces.sqlite3`
4. Opens `LiveViewerServer(dashboard_mode=True)` and captures the session
   viewer Default Tools section and Trace request JSON

`.traces/` remains gitignored. Screenshots are committed under this directory.

## Artifacts

- `seed_and_capture.py`: real-transcript stage + import + Playwright capture
- `dashboard-cursor-session-tools.png`: Default view Tools catalog reconstructed
  from observed `tool_use` plus system prompt from `store.db`
- `dashboard-cursor-session-trace-tools.png`: Trace view request JSON with
  `tools` and `system`
