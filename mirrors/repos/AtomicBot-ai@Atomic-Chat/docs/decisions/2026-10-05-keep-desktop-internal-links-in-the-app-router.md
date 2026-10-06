---
date: 2026-10-05
title: "Keep desktop internal links in the app router"
---

# 2026-10-05 — Keep desktop internal links in the app router

- **Context:** Sidebar clicks on Windows ARM were reported opening `tauri.localhost/settings/general` and other app pages in Edge. The exact ordinary-click trigger is unconfirmed. A reproducible escape exists for Ctrl/Shift clicks: TanStack Router leaves them to the browser and the default opener plugin forwards HTTP links to the system browser. On Windows the Tauri app uses an HTTP custom-protocol origin, which an external browser cannot serve.
- **Decision:** Install a desktop Tauri document listener after React's link handling and before the opener's window listener. Route otherwise-unhandled same-origin clicks, including modified and middle clicks, through the existing router and cancel native navigation. Compare protocol, host and origin, including the opaque `tauri:` origin on macOS/Linux.
- **Consequences:** Internal routes stay in the app and retain queries and fragments. External links, download anchors, fragment-only links and clicks already prevented by components keep their existing handling. Browser-only and mobile builds do not install the listener. Malformed URLs are ignored without throwing from the global listener. Windows ARM release reproduction remains necessary to confirm the reported ordinary-click case.
- **Owner:** team.
- **Links:** `web-app/src/lib/internal-navigation.ts`, `web-app/src/lib/internal-navigation.test.tsx`, `web-app/src/main.tsx`; [Tauri webview URLs](https://v2.tauri.app/reference/javascript/api/namespacewebview/).

## Verification

A Chromium probe on macOS loaded the installed React/TanStack Router versions,
this handler and the unmodified `tauri-plugin-opener` 2.5.3 `init-iife.js` at
`http://tauri.localhost/`. The native IPC boundary recorded opener requests
instead of launching another application. Before the change, Shift-click and
`target="_blank"` forwarded internal URLs to opener, and middle-click created a
second browser page. After the change, all three navigated the existing page;
ordinary clicks, external links and downloads retained their behavior. A Ctrl
mouse event also passed; it was dispatched in the browser because macOS maps a
physical Ctrl-click to its context menu. Malformed-link coverage first exposed
an uncaught URL-constructor error, which the handler now avoids.

This checks browser event ordering with the real opener script, not the Windows
WebView2 host. It does not establish why the reported ordinary clicks escape on
the affected Windows ARM machine. Regression tests use the real app router in
`web-app/src/lib/internal-navigation.test.tsx`.
