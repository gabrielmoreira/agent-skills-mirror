# Quickstart: NetClaw for Zoom — Meeting Intelligence (MVP)

## Prerequisites (operator setup, before implementation can be exercised end-to-end)

1. **Zoom Developer account** with a Marketplace app registration (General App or Server-to-Server
   OAuth app) — provides `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`, `ZOOM_ACCOUNT_ID`.
2. **RTMS scopes added to the app** — confirmed live 2026-08-17 against a real Marketplace app, the
   full and correct scope set for this feature's needs is:
   `meeting:read:meeting`, `meeting:read:meeting_transcript`, `meeting:read:meeting_chat`,
   `rtms:read:rtms_started`, `rtms:read:rtms_stopped`, `user:read:user`, `zoomapp:inmeeting`,
   `meeting:write:open_app`. Deliberately *not* requested: `meeting:read:meeting_audio`,
   `meeting:read:meeting_video`, `meeting:read:meeting_screenshare` (we consume transcript/chat text
   only, not raw audio/video/screen content — least-privilege, Constitution Principle IX), and all
   `webinar:*` scopes / `zoomapp:inwebinar` (out of scope — Meetings only, no Webinars selected under
   product selection). These were all selectable directly in the Marketplace Scopes picker without a
   separate Developer Pack purchase or manual Zoom enablement request for this account, contrary to
   some 2026 developer-forum reports for other accounts. Once the two RTMS scopes are added, "Allow
   auto-start for RTMS apps" (General Features) becomes toggleable — it stays grayed out until they're
   present. Actual RTMS *usage* is still separately metered per Zoom's Developer Pack pricing
   (~$0.01/meeting-streaming-minute for video-only was one data point found) — scope availability and
   usage billing are two different things.
3. **RTMS webhook secret token** (Zoom validates the webhook handshake with this) —
   `ZOOM_RTMS_WEBHOOK_SECRET`.
4. **A public HTTPS endpoint** that Zoom's RTMS-start webhook can reach — whatever ingress the
   operator's environment already runs (ngrok HTTP tunnel, reverse proxy, Cloudflare Tunnel HTTP
   mode). Not something this feature provisions (research.md R5).
5. **Official Zoom Meetings MCP access** — credential shape TBD once Zoom's connector setup flow is
   confirmed at implementation time (research.md R6); tracked as `remote/OAuth` per
   `docs/ADDING-AN-MCP.md`.
6. **A separate Zoom App registration** for the side-panel surface — its own Client ID/Secret/
   redirect URL, with **Collaborate Mode** toggled on under Features and **submitted for Zoom's app
   review** (required before Collaborate Mode works for real participants, per Zoom's own docs).
7. **Layers API "Camera mode" access**, for User Story 5 only — requires the Controller-mode
   component and, per research.md R8, Zoom's own app review. If this isn't grantable in time, User
   Story 5 is skippable without affecting Stories 1/2/3/4.

None of the above blocks finishing the plan/design artifacts in this directory — they're prerequisites
for `/speckit.implement`, documented here so setup can happen in parallel with task breakdown.

## Demo script (once implemented)

1. Start a Zoom meeting; enable NetClaw listening via `zoom_enable_listening`.
2. Open the NetClaw Zoom App side panel — confirm avatar shows `listening`.
3. Say aloud: "Toronto lost its BGP sessions about ten minutes ago, what happened?"
4. Confirm the panel avatar moves through `thinking` → `investigating` → `answered`, and a
   synthesized, evidence-backed answer appears — visible to every participant with the panel open,
   including one who joined as an unauthenticated guest.
5. Say, as a clearly hypothetical aside: "we could just shut that interface I guess" — confirm
   nothing is queued for approval and no action is attempted (FR-009).
6. Ask directly: "shut interface Gi0/1 on EDGE-TOR-01" — confirm the request is held for explicit
   human approval through NetClaw's existing approval mechanism, not executed automatically
   (FR-008).
7. Reference a prior, real meeting by topic — confirm historical correlation via the Zoom Meetings
   MCP surfaces in the panel (User Story 2).
8. (If Layers API access is available) enable the camera overlay on your own feed from the panel —
   confirm the avatar bubble appears on your outgoing video and disappears when disabled (User
   Story 5).
9. End the meeting — confirm the live buffer and `MeetingSession` are gone (FR-014, SC-006).
