# Quickstart: World Labs Fantastical Topology Visualization

## Prerequisites

- `WLT_API_KEY` set in `.env` (a World Labs account with credits — see
  `https://platform.worldlabs.ai/api-keys` and `.../billing`).
- `worldlabs-marble-mcp` registered in `config/openclaw.json` and installed
  (`python3 -m pip install --user --break-system-packages -r mcp-servers/worldlabs-marble-mcp/requirements.txt`).
- A topology snapshot from any existing source (CML, pyATS, or a freeform description), normalized
  into the same devices/links shape `topology-diagram-mcp` already accepts.

## 1. Free preview (no credits spent)

```
"Give me a fantastical world preview of the CML lab topology, floating-islands theme"
```

Expected flow:
1. NetClaw retrieves the topology snapshot.
2. Calls `topology-diagram-mcp/render_structural` — gets the authoritative reference PNG.
3. Runs `fantastical_prompt_builder.build_prompt(snapshot, theme="floating islands")` — no network
   call, instant.
4. Reports back: the reference diagram, the composed text prompt, and the required decorative-
   interpretation statement (FR-009). **No World Labs call is made. No credits are spent.**

## 2. Confirm and generate (spends credits)

```
"Yes, generate it"
```

Expected flow:
1. NetClaw explicitly states: "This will spend World Labs credits and take about 5 minutes. Proceed?"
2. Only on explicit "yes" does it call `worldlabs-marble-mcp/generate_world` with the reference PNG
   (base64) and the previously composed prompt.
3. Returns `operation_id` and `expires_at` — NetClaw keeps this in conversation context (no
   server-side state exists to fall back on).

## 3. Check status

```
"Is it done yet?"
```

Calls `worldlabs-marble-mcp/check_generation_status(operation_id)`. Reports in-progress, completed
(with `world_marble_url` and asset links, plus the FR-009 decorative statement again), or a
categorized failure (auth / insufficient-credits / rate-limited / generic).

## 4. If the operation record has expired

If step 3 returns `not_found_or_expired` but an earlier poll's `metadata` included a `world_id`,
NetClaw falls back to `worldlabs-marble-mcp/get_world(world_id)` instead of reporting a hard failure.

## Manual verification already performed (this session, not a re-runnable test)

A real `POST /marble/v1/worlds:generate` call with a rotated `WLT_API_KEY` returned HTTP 200 and a
genuine `operation_id`, proving credential + connectivity work end-to-end (research.md R2). This
satisfies FR-014/SC-006 for the plan; it does not need to be repeated to validate this plan, and
should not be repeated casually since it is a real, credit-spending action against the production
API.
