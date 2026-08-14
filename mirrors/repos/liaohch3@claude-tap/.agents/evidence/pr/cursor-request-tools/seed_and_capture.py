#!/usr/bin/env python3
"""Capture dashboard evidence for reconstructed Cursor request tools/system.

Usage (from repo root):

    uv run python .agents/evidence/pr/cursor-request-tools/seed_and_capture.py

Imports a real local Cursor JSONL plus the matching chat-store system prompt
blob into ``.traces/cursor-request-tools/traces.sqlite3`` and screenshots the
live dashboard viewer. Screenshots are backed by real transcript data, not
fabricated request/response rows.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
EVIDENCE_DIR = Path(__file__).resolve().parent
TRACE_DIR = REPO_ROOT / ".traces" / "cursor-request-tools"
DB_PATH = TRACE_DIR / "traces.sqlite3"
CURSOR_HOME = TRACE_DIR / "cursor-home"
TOOLS_SHOT = EVIDENCE_DIR / "dashboard-cursor-session-tools.png"
TRACE_SHOT = EVIDENCE_DIR / "dashboard-cursor-session-trace-tools.png"

PROJECT_SLUG = "Users-youngcan-claude-tap"
CURSOR_SESSION_ID = "0b95c4b6-03e2-4780-8c3a-124f43625297"
REAL_TRANSCRIPT = (
    Path.home()
    / ".cursor"
    / "projects"
    / PROJECT_SLUG
    / "agent-transcripts"
    / CURSOR_SESSION_ID
    / f"{CURSOR_SESSION_ID}.jsonl"
)
REAL_STORE = Path.home() / ".cursor" / "chats" / "6b5c49853e58218945cfc724b74858f8" / CURSOR_SESSION_ID / "store.db"


def _stage_real_transcript() -> Path:
    if not REAL_TRANSCRIPT.is_file():
        raise SystemExit(f"Real Cursor transcript not found: {REAL_TRANSCRIPT}")
    if CURSOR_HOME.exists():
        shutil.rmtree(CURSOR_HOME)
    dest = (
        CURSOR_HOME
        / ".cursor"
        / "projects"
        / PROJECT_SLUG
        / "agent-transcripts"
        / CURSOR_SESSION_ID
        / f"{CURSOR_SESSION_ID}.jsonl"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REAL_TRANSCRIPT, dest)
    return dest


def _stage_chat_store() -> Path | None:
    if not REAL_STORE.is_file():
        return None
    dest = CURSOR_HOME / ".cursor" / "chats" / "ws" / CURSOR_SESSION_ID / "store.db"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{REAL_STORE}?mode=ro", uri=True)
    dst = sqlite3.connect(dest)
    try:
        dst.execute("CREATE TABLE meta (key TEXT, value TEXT)")
        dst.execute("CREATE TABLE blobs (id TEXT PRIMARY KEY, data BLOB)")
        try:
            for key, value in src.execute("SELECT key, value FROM meta"):
                dst.execute("INSERT INTO meta(key, value) VALUES (?, ?)", (key, value))
        except sqlite3.Error:
            pass
        best_id = ""
        best = b""
        try:
            rows = src.execute("SELECT id, data FROM blobs").fetchall()
        except sqlite3.Error:
            rows = []
        for blob_id, data in rows:
            raw = data.encode("utf-8") if isinstance(data, str) else data
            if not isinstance(raw, bytes) or not raw.lstrip().startswith(b"{"):
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict) or obj.get("role") != "system":
                continue
            if len(raw) > len(best):
                best_id = str(blob_id)
                best = raw
        if best_id:
            dst.execute("INSERT INTO blobs(id, data) VALUES (?, ?)", (best_id, best))
        dst.commit()
    finally:
        src.close()
        dst.close()
    return dest


async def _import_real_transcript() -> str:
    os.environ["CLOUDTAP_DB"] = str(DB_PATH)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    lock_path = Path(str(DB_PATH) + ".write.lock")
    if lock_path.exists():
        lock_path.unlink()

    from claude_tap.cursor_transcript import import_cursor_transcripts
    from claude_tap.trace_store import get_trace_store, reset_trace_store

    reset_trace_store()
    store = get_trace_store()
    watcher = await import_cursor_transcripts(since=0, home=CURSOR_HOME, store=store)
    try:
        if not watcher.session_ids:
            raise SystemExit("Import produced no Cursor sessions from the real transcript")
        session_id = watcher.session_ids[0]
        for candidate in watcher.session_ids:
            records = store.load_records(candidate)
            if records and records[0].get("capture", {}).get("cursor_project") == PROJECT_SLUG:
                session_id = candidate
                break
        records = store.load_records(session_id)
        body = (records[0].get("request") or {}).get("body") or {}
        tools = body.get("tools") or []
        if not tools:
            raise SystemExit("Imported records are missing reconstructed request tools")
        model = str(body.get("model") or "")
        summary = {"api_calls": len(records)}
        if model:
            summary["models_used"] = {model: len(records)}
        store.finalize_session(session_id, summary)
        return session_id
    finally:
        watcher.close()


async def _capture(session_id: str) -> None:
    from playwright.async_api import async_playwright

    from claude_tap.live import LiveViewerServer

    server = LiveViewerServer(port=0, dashboard_mode=True)
    port = await server.start()
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            await page.goto(
                f"http://127.0.0.1:{port}/dashboard/session/{session_id}",
                wait_until="domcontentloaded",
                timeout=15000,
            )
            await page.get_by_text("Full viewer", exact=True).click()
            frame = page.frame_locator(".viewer-frame")
            await frame.locator(".sidebar-item").first.wait_for(timeout=15000)
            await frame.locator(".sidebar-item").first.click()
            await frame.locator("#detail .section").first.wait_for(timeout=15000)
            tools_header = frame.locator(".section-header", has_text="Tools")
            await tools_header.wait_for(timeout=10000)
            await tools_header.click()
            read_tool = frame.locator(".tb-name", has_text="Read").first
            await read_tool.wait_for(timeout=5000)
            await read_tool.click()
            system_header = frame.locator(".section-header", has_text="System Prompt")
            if await system_header.count():
                await system_header.click()
            await page.wait_for_timeout(400)
            await page.screenshot(path=str(TOOLS_SHOT), full_page=False)

            await frame.locator(".detail-tab", has_text="Trace").click()
            await frame.locator(".trace-code").first.wait_for(timeout=5000)
            await frame.locator('.trace-format-btn[data-format="json"]').click()
            schema = frame.locator(".trace-code").first.get_by_text('"input_schema"', exact=False)
            await schema.wait_for(timeout=5000)
            await schema.scroll_into_view_if_needed()
            await page.wait_for_timeout(400)
            await page.screenshot(path=str(TRACE_SHOT), full_page=False)
            await browser.close()
    finally:
        await server.stop()


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    staged = _stage_real_transcript()
    store = _stage_chat_store()
    session_id = asyncio.run(_import_real_transcript())
    asyncio.run(_capture(session_id))
    print(f"source={REAL_TRANSCRIPT}")
    print(f"staged={staged}")
    print(f"store={store}")
    print(f"db={DB_PATH}")
    print(f"session_id={session_id}")
    print(f"tools_shot={TOOLS_SHOT}")
    print(f"trace_shot={TRACE_SHOT}")


if __name__ == "__main__":
    main()
