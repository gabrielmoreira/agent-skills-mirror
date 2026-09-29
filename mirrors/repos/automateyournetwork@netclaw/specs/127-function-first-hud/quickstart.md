# Implementation and acceptance quickstart

Spec127 is implemented locally for review, with required live/browser acceptance still pending. It has not been pushed or deployed.

1. Read [spec.md](spec.md), [workflows.md](workflows.md), [research.md](research.md), [plan.md](plan.md) and [tasks.md](tasks.md).
2. Start/checkout a GAIT session, inspect Git status and record scope. User ratified T001 on 2026-09-28; preserve the review-before-push requirement.
3. In `ui/netclaw-visual`, run `npm test` and `npm run build` for the baseline using existing installed dependencies. Capture synthetic old-format canvas sessions before edits.
4. Use the existing `npm run dev` workflow only after checking ports/runtime settings. Keep loopback access restrictions and both HUD/`canvas.html` entries. Do not expose the listener for mobile testing; use the supported access path.
5. Implement tasks in order. Never use private production evidence in committed fixtures or screenshots. No paid Jev evaluation is required to test detailed views.
6. Record browser, viewport, source revision, fixture/live classification and result for each acceptance journey. A green build is not proof of canvas preservation or authenticated task ownership.

## Required demo journeys

- Open an old canvas session → inspect a dashboard finding → return → branch → synthesize → inspect all four tabs → export/reopen with identical content and relationships.
- Toggle Basic/Advanced while a draft/reply is active; verify no lost work or extra request.
- Walk every deployment fixture and workflow destination, including unavailable sources.
- Open a bound Jev assessment and its one reconsideration; compare typed answers and Border influence. Try a foreign ID and imported reference; show no detail.
- Select a member/peer/mobile edge in table and Three.js, then disable WebGL and continue using tables and canvas.
- Lose a source/gateway during use; verify stale/unavailable state and explicit fallback identity without false health claims.

## Current limits

Trusted task linkage and authenticated detail mediation are design requirements, not existing browser features. The current global Jev snapshot cannot satisfy them. No runtime, native mobile or WSL deployment has been performed by this specification package. The common upgrade utility is outside spec127.
