# Chat Components DOX

## Purpose

- Own chat composer, attachments, message queue, navigation, and top-section component groups.

## Ownership

- `input/` owns composer input, progress, banners, and bottom action bars.
- `attachments/` owns drag/drop and attachment preview UI.
- `message-queue/` owns queued message display and store state.
- `navigation/` owns chat navigation state.
- `top-section/` owns chat header/top area.

## Local Contracts

- Preserve Store Gating for all store-backed chat components.
- Use shared API, WebSocket, notification, and attachment helpers where available.
- Do not bypass CSRF or WebSocket state-sync expectations.
- The shared composer can be mounted on the Welcome screen with no selected chat; sending from that state must create and select a chat context before dispatch.
- Composer text uses the main UI font by default and switches to the code font while the caret is inside an open triple-backtick fenced block.

## Work Guidance

- Keep composer and attachment changes responsive across desktop and mobile.
- Coordinate payload changes with backend chat, upload, and WebSocket handlers.

## Verification

- Smoke-test sending, queued messages, attachments, drag/drop, and navigation after visible changes.

## Child DOX Index

No child DOX files.
