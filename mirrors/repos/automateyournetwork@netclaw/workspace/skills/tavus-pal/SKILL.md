---
name: tavus-pal
description: Set up or troubleshoot the optional Tavus voice companion in the NetClaw HUD, including stock faces, free allowance, local icon and interrupted-call recovery.
---

# Tavus Pal

Use [the setup guide](../../../docs/TAVUS-PAL.md) for commands and deployment checks.
The first implementation explains concepts through an isolated NetClaw agent with
all tools denied. It does not provide device access or the main agent's memory.

- The HUD calls the local stdio `pal_query(question, session_id)` facade. Its
  results stay local until the operator selects **Speak this answer**. Do not
  send raw results through Tavus events or reinterpret tool output as approval.
- Free uses stock video faces. A locally selected smiley/lobster is only a browser
  icon; do not describe it as a custom Tavus avatar. Custom image training is not
  part of this free workflow.
- `status`, `faces` and `verify` do not create conversations. Provisioning creates
  a PAL and tool, not a call. The API key alone never enables Pal.
- Confirm current allowance before starting. A lost create/end response consumes
  its reservation and blocks another start. Use Reconcile; do not reset the ledger,
  create another PAL or retry a mutation blindly to regain minutes.
- A gateway/policy failure means unavailable, not a device-health finding. GAIT
  failure prevents new dispatch; call cleanup must remain possible.

Never upgrade, train a custom face, publish a listener or contact other people as
a side effect of setup. Honor existing session authorization for the requested
local setup and keep incomplete live acceptance visible.
