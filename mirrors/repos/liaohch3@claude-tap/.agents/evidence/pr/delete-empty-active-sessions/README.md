# Delete empty-active sessions evidence

## Problem shape

Abandoned Claude Code startups can remain `status=active` with `record_count=0`.
The dashboard shows them as `EMPTY`, but fresh writers must stay protected until
stale finalization proves they were abandoned.

## Deterministic recreation

From the repo root:

```bash
uv run python .agents/evidence/pr/delete-empty-active-sessions/seed_and_capture.py
uv run python scripts/check_screenshots.py \
  .agents/evidence/pr/delete-empty-active-sessions/dashboard-empty-active-selectable.png
```

The seed script:

1. Builds a local store at `.traces/delete-empty-active-sessions/traces.sqlite3`
   through `TraceStore.create_session()` / `append_record()` / `finalize_session()`
2. Adds one finalized Claude Code turn and two empty sessions:
   - stale empty (`updated_at` 20 minutes ago) → selectable after finalize
   - fresh empty (`updated_at` now) → still protected
3. Opens `LiveViewerServer(dashboard_mode=True)`, enters edit mode, selects the
   stale empty row, and writes the committed screenshot

`.traces/` remains gitignored; reviewers reproduce the store with the committed
`seed_and_capture.py` script above.

## Artifacts

- `seed_and_capture.py`: deterministic seed + Playwright capture
- `dashboard-empty-active-selectable.png`: edit-mode screenshot with the stale
  empty session selected (`1 selected`)
