# Quickstart: ComfyUI Network Topology Visualization

## Enable it

During `./scripts/install.sh`, or later via the catalog installer, answer "y" to enabling
**ComfyUI Topology Visualization**. This clones and builds `comfyui-mcp`
(`https://github.com/shawnrushefsky/comfyui-mcp.git`) into `mcp-servers/comfyui-mcp/` and registers
it as `comfyui-mcp` in `config/openclaw.json`.

## Configure

Add to your `.env` (see `.env.example` for the documented, valueless entry):

```
COMFYUI_URL=http://127.0.0.1:8000
```

Use whatever host/port your own ComfyUI instance actually listens on. `comfyui-mcp`'s own defaults
are `8000` for ComfyUI Desktop installs and `8188` for manual installs — set this explicitly rather
than relying on either default, since the two are easy to mix up.

**If NetClaw cannot reach your `COMFYUI_URL`**: this is most commonly a WSL2 networking-mode issue
when ComfyUI runs on a separate Windows host. Check whether WSL2 mirrored networking is active
(`ip route show default` inside WSL2, then try `curl <your COMFYUI_URL>/system_stats` directly — if
that returns real ComfyUI JSON, you're reachable with no further changes needed). If it is not
reachable, start ComfyUI with a bind address reachable beyond Windows loopback (e.g. `--listen
0.0.0.0` for a manual ComfyUI install) and use the Windows host's LAN or WSL-visible IP in
`COMFYUI_URL` instead of `127.0.0.1`.

## Ask NetClaw

```
"Give me a stylized AI image of the CML lab topology"
"Render my GNS3 project as a ComfyUI image"
"Make a flashy image of this topology: a router r1 connected to a switch sw1"
```

NetClaw retrieves the topology from the named (or clarified) source, checks what image-generation
checkpoints ComfyUI has installed, and — if one is available — generates one image and tells you
where it was saved: `workspace/output/comfyui-topology-viz/<timestamp>-<request-id>.png` (plus a
sidecar JSON recording the prompt and checkpoint used).

## If you get "no usable model found"

This is expected on a fresh ComfyUI install with no checkpoints downloaded yet — it is not a NetClaw
bug. Install at least one Stable Diffusion 1.5, SDXL, or Flux checkpoint into ComfyUI's
`models/checkpoints` directory (ComfyUI Manager, or a manual download into that folder), then ask
again.

## Verifying this yourself (what Phase 0 research actually checked)

These are the exact live checks run against the current environment during planning
(2026-08-26), included here so you can re-run them yourself against your own instance:

```bash
# 1. Is ComfyUI actually reachable at the configured URL?
curl -sS "$COMFYUI_URL/system_stats"
# A real response looks like:
# {"system": {"os": "win32", "comfyui_version": "0.34.0", ...}, ...}

# 2. What checkpoints does it actually have installed?
curl -sS "$COMFYUI_URL/models/checkpoints"
# [] means zero — this is the "no usable model found" case above.
```

At planning time, check (1) succeeded (a real, live ComfyUI Desktop instance on a separate Windows
host, reachable from WSL2 with zero networking workaround) and check (2) returned `[]` — meaning the
very first real use of this feature is expected to hit the "no usable model found" path until a
checkpoint is installed. That is correct, verified behavior, not a defect.

## Known limitations (v1)

- **Stills only.** No video (traffic flybys, packet-tracing animations) and no stylized test-result
  cards — both explicitly out of scope for this spec (FR-016), likely follow-on specs.
- **One job at a time.** A second request while one is generating is rejected outright, not queued
  (FR-009a) — wait for the first to finish (or fail) and ask again.
- **No NetClaw-imposed timeout.** Generation time is whatever ComfyUI/your hardware takes; NetClaw
  tracks the job to ComfyUI's own completed/failed status rather than giving up on a slow-but-working
  job (Clarification session 2026-08-26).
