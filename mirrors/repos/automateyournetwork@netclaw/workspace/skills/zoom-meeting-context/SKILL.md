---
name: zoom-meeting-context
description: "Zoom meeting intelligence — correlates a live or referenced Zoom meeting discussion against NetClaw's historical meeting record (via the official Zoom Meetings MCP) and today's actual network state. Use when someone in a Zoom meeting references a past discussion or incident ('didn't we have this issue before?'), or asks to search prior meetings for a topic. Does not itself recognize live in-meeting questions — that happens automatically inside zoom-rtms-mcp's own extractor (spec 118) before this skill is ever invoked."
version: 1.0.0
license: Apache-2.0
tags: [zoom, meetings, rtms, history, correlation, external]
user-invocable: true
metadata:
  { "openclaw": { "requires": { "bins": ["python3"], "env": ["ZOOM_MEETING_MCP_CREDENTIAL"] } } }
---

# Zoom Meeting Context

## What this is, and isn't

NetClaw for Zoom (spec 118) has two separate recognition paths — don't confuse them:

1. **Live in-meeting questions** ("Toronto lost its BGP sessions, what happened?") are recognized
   automatically, inside `zoom-rtms-mcp`'s own `extractor.py`, and routed straight to the Border's
   existing investigation path (`bgp/federation/zoom_channel.py`). This never invokes this skill.
2. **This skill** is for the historical-correlation half only (User Story 2): "didn't we see this
   before?" — searching the official Zoom Meetings MCP for a prior, real meeting and comparing what
   was discussed then against the network's actual current state.

## MCP Servers

- **`zoom-rtms-mcp`** (NetClaw-authored, spec 118) — `zoom_search_historical_meetings` is a thin
  pass-through to the official Zoom Meetings MCP; use it, not a direct connection of your own.
- **Zoom Meetings MCP** (official, Zoom-hosted) — remote/OAuth, no local vendoring. Credential shape
  is still being confirmed against Zoom's own connector setup flow (tracked in
  `specs/118-zoom-meeting-intelligence/research.md` R6 / `tasks.md` T030).
- Whatever Member Claw already answers the "what's true right now" half (pyATS, NetBox, Splunk,
  etc.) — reuse the existing routing path, don't build a second one.

## Workflow

1. Someone references a past meeting/incident by topic or approximate timeframe.
2. Call `zoom_search_historical_meetings(query, time_hint)`.
3. **If nothing relevant comes back, say so plainly.** Do not present an unrelated result as if it
   were the match — this is an explicit spec requirement (FR-010's "no matching past meeting" case),
   not a style preference.
4. If a relevant past meeting is found, summarize what was discussed/decided then.
5. Check the network's current actual state for the same location/technology (via the existing
   Member-Claw routing — the same path `zoom-rtms-mcp`'s live investigations use).
6. State plainly whether current state **matches** or **differs** from the historical discussion.
   Don't hedge past what the evidence actually shows.

## What this skill must never do

- Never fabricate a historical match when the search comes back empty.
- Never treat this skill as a path to execute a configuration change — it is read-only correlation.
  Any actual change request, however it's phrased, still goes through NetClaw's existing device-write
  approval gate (Constitution Principles I–III), unchanged by this skill's existence.

## Related

- `specs/118-zoom-meeting-intelligence/` — full spec/plan/research/data-model/contracts
- `mcp-servers/zoom-rtms-mcp/` — the live-listening half (extractor, panel feed, Border channel client)
- `docs/ZOOM-MEETING-INTELLIGENCE.md` — operator setup guide
