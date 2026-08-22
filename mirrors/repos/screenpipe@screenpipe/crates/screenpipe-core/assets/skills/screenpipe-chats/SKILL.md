---
name: screenpipe-chats
description: Search existing screenpipe, Codex, Claude, and Cursor chats, then continue or steer one exact chat when the user explicitly asks. Use for requests about finding another agent conversation or sending work to one.
---

# existing agent chats

screenpipe exposes `search_chats` and `send_to_chat` as agent tools. They use a
private core capability passed into the current chat process; do not scrape
transcript folders, guess runtime commands, or call a localhost app route.

## search

1. Call `search_chats` with a short title, message, workspace, or exact id. Omit
   the query to list recent chats. Filter `sources` only when the user named a
   runtime.
2. Show enough title, source, preview, and workspace information to distinguish
   ambiguous results.
3. Treat the returned `source` and `id` as the address. Never derive an id from
   a title or reuse a stale result after the target disappears.

Searching is read-only and does not require confirmation.

## send

1. Require an exact result from `search_chats` in the current turn.
2. Require explicit user authorization for that target and message. A draft,
   suggestion, or request to inspect chats is not permission to send.
3. Call `send_to_chat` with the exact `source`, `id`, message, and
   `confirmed: true`.
4. Use `mode: queue` by default. Use `mode: steer` only when the user asked to
   redirect a currently running screenpipe chat.
5. Report the returned status and exact target. Do not retry an uncertain or
   failed send until the result is reconciled.

The tool refuses self-sends, guessed ids, dormant-chat steering, oversized
messages, and sends without confirmation. Cross-chat sending is disabled in
unattended scheduled runs.
