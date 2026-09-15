# Desktop agent notes

Desktop Go is a separate module; root Go tests do not cover it.

For changes affecting transcript viewport, scrolling, loaded history, or
delayed geometry work, read the
[transcript scroll and history contract](../docs/TRANSCRIPT_SCROLL_CONTRACT.md)
([中文](../docs/TRANSCRIPT_SCROLL_CONTRACT.zh-CN.md)).
It preserves single-writer ownership, generation isolation, reader intent,
bounded rendering, the bounded reading window, and deterministic regression
requirements.

Other Desktop work does not require the scroll-specific procedure.

## Natural-flow chat

The transcript uses ChatSource and ChatScrollController. It has one natural-flow
implementation for local and remote sessions. Do not restore the retired
window adapter, measurement ledger, geometry revision loop or logical selection.

- Stable node keys derive from message/call identities, never array positions.
  Streaming and settlement update the same assistant host; unchanged node and
  order snapshots retain their references.
- Business state remains in the controller/history owners. ChatSource is a
  reconstructable view projection. Structural changes batch in microtasks;
  existing controller frame batching owns stream publication.
- Only frontend/src/lib/transcriptViewportWriter.ts writes the chat viewport.
  ChatScrollController owns programmatic follow, reader anchoring and navigation.
  Native input is never synthesized or prevented to keep the tail pinned.
- A small upward reader movement releases follow even inside the 24px bottom
  threshold. Prepend and resize preserve a stable node plus viewport offset.
  Old observers, requests and callbacks cannot act on a replaced session.
- Markdown, tables and loaded history use document flow. Parsing may be lazy,
  but must not create a nested virtual vertical scroller. Collapsed
  process/tool bodies are mounted on demand.
- History is a bounded reading window, not an ever-growing list. The resident
  store keeps a small number of adjacent pages (`windowMaxPages`, default 3 of
  32-message pages) per session, including the active one: paging past that
  reclaims a page from the end the reader is moving away from and re-fetches
  it on demand. Nothing is deleted — the persisted session is authoritative —
  and the reclaimed direction stays reachable through its cursor. Do not add a
  path that holds every loaded page resident, and do not treat "all history is
  mounted" as a correctness property; assert reachability and bounded
  residency instead.
- Paging is bidirectional. `loadOlder`/`loadNewer` reclaim from the opposite
  end and hand the caller the ids to drop; a caller that ignores them will
  render rows the store has already released. Window cursors pin a fixed
  snapshot: appends keep them valid, a storage replacement answers
  `stale_cursor`, and a cursor the server cannot read is that same typed
  answer rather than a transport error.
- History reads route by the tab's binding identity, never by the result of a
  failed call: a local error must not be answered by a remote service holding
  a different session. A remote service that never negotiated
  `history-window-v1` answers with the typed `unsupported` status and keeps
  its protocol-7 pages.
- No geometry snapshots are stored in React state. Layout observers must
  converge without a render/measurement feedback loop.
- Native selection is browser-owned. No cross-window selection overlay or
  clipboard interception belongs to the chat.
- Keep draft input, approvals, questions, model controls and the session bridge
  outside the presentation refactor. Do not change persisted/provider bytes.
- Run pnpm test:transcript and the applicable browser suite. The primary cases
  are small reader gestures, stream growth, prepend, disclosure, session change,
  stale callbacks and unchanged-node render isolation. Do not weaken performance
  gates to hide regressions.
