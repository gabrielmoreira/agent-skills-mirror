#!/usr/bin/env python3
"""Deterministically recreate the delete-empty-active-sessions dashboard evidence.

Usage (from repo root):

    uv run python .agents/evidence/pr/delete-empty-active-sessions/seed_and_capture.py

This writes:

- `.traces/delete-empty-active-sessions/traces.sqlite3` (gitignored local store)
- `.agents/evidence/pr/delete-empty-active-sessions/dashboard-empty-active-selectable.png`
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_DIR = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / ".traces" / "delete-empty-active-sessions" / "traces.sqlite3"
SCREENSHOT_PATH = EVIDENCE_DIR / "dashboard-empty-active-selectable.png"


def _seed_store() -> tuple[str, str]:
    os.environ["CLOUDTAP_DB"] = str(DB_PATH)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    lock_path = Path(str(DB_PATH) + ".write.lock")
    if lock_path.exists():
        lock_path.unlink()

    from claude_tap.trace_store import get_trace_store, reset_trace_store

    reset_trace_store()
    store = get_trace_store()
    done = store.create_session(client="claude", proxy_mode="reverse")
    store.append_record(
        done,
        {
            "timestamp": "2026-07-28T08:00:00+00:00",
            "turn": 1,
            "duration_ms": 120,
            "request": {
                "method": "POST",
                "path": "/v1/messages",
                "body": {
                    "model": "claude-sonnet-4-6",
                    "messages": [{"role": "user", "content": "delete-empty-active evidence seed"}],
                },
            },
            "response": {
                "status": 200,
                "body": {
                    "content": [{"type": "text", "text": "ok"}],
                    "usage": {"input_tokens": 12, "output_tokens": 3},
                },
            },
        },
    )
    store.finalize_session(done, {"api_calls": 1})

    stale_empty = store.create_session(client="claude", proxy_mode="reverse")
    fresh_empty = store.create_session(client="claude", proxy_mode="reverse")
    now = datetime.now(timezone.utc)
    conn = store._connect()
    conn.execute(
        "UPDATE sessions SET updated_at = ? WHERE id = ?",
        ((now - timedelta(minutes=20)).isoformat(), stale_empty),
    )
    conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now.isoformat(), fresh_empty))
    conn.commit()
    return stale_empty, fresh_empty


async def _capture(stale_empty_id: str) -> None:
    from playwright.async_api import async_playwright

    from claude_tap.live import LiveViewerServer

    server = LiveViewerServer(port=0, dashboard_mode=True)
    port = await server.start()
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            await page.goto(f"http://127.0.0.1:{port}/dashboard", wait_until="domcontentloaded", timeout=15000)
            await page.locator("#edit-sessions").wait_for(state="visible", timeout=10000)
            await page.locator("#edit-sessions").click()
            checkbox = page.locator(f'[data-select-session="{stale_empty_id}"]')
            await checkbox.wait_for(state="visible", timeout=10000)
            assert await checkbox.is_enabled(), "stale empty session checkbox should be enabled"
            await checkbox.check()
            await page.wait_for_function(
                "() => (document.querySelector('#bulk-selected-count')?.textContent || '').includes('1')",
                timeout=5000,
            )
            await page.wait_for_timeout(200)
            await page.screenshot(path=str(SCREENSHOT_PATH), full_page=False)
            await browser.close()
    finally:
        await server.stop()


def main() -> None:
    stale_empty_id, fresh_empty_id = _seed_store()
    asyncio.run(_capture(stale_empty_id))
    print(f"db={DB_PATH}")
    print(f"screenshot={SCREENSHOT_PATH}")
    print(f"stale_empty_id={stale_empty_id}")
    print(f"fresh_empty_id={fresh_empty_id}")


if __name__ == "__main__":
    main()
