---
name: fleet-portable-config
description: Adapt the Megingjord harness to a new operator's fleet topology without hand-editing inventory files. Use when first activating the harness on a new host or onboarding a new fleet.
argument-hint: ""
user-invocable: true
disable-model-invocation: false
type: skill
---

# Fleet Portable Configuration

The harness ships with `inventory/devices.json` describing Curtis's specific
4-node fleet. New operators with different hardware should NOT edit that file
directly. Use this skill to discover their own tailnet and produce an overlay.

## Workflow

```
1. Install Tailscale + authenticate:
     tailscale up

2. Run discovery:
     bash scripts/global/fleet-discover.sh
   → writes ~/.megingjord/devices.json (operator overlay)

3. Verify:
     node scripts/global/fleet-config.js fleet
   → fleet-config reads operator overlay first, repo file second

4. (Optional) Register Cloudflare AI free tier:
     export CLOUDFLARE_API_TOKEN=...
     export CLOUDFLARE_ACCOUNT_ID=...
   → substrate-health.js will probe CF AI on next run

5. (Optional) Activate IDE proxy:
     bash scripts/global/ide-proxy-control.sh start
   → see instructions/ide-proxy.instructions.md
```

## Inputs the harness needs

- Tailscale tailnet membership (free plan works).
- One node running Ollama for fleet routing (any host with ≥4GB RAM).
- Optional: Cloudflare account for free 10K Neurons/day AI catalog.

## Inputs the harness does NOT require

- Specific hostnames (`36gbwinresource`, `windows-laptop`, etc.).
- Specific GPU class.
- Specific OS (Linux/macOS/Windows all supported via Tailscale).

## Reference files

- `inventory/devices.example.json` — generic 2-node example.
- `inventory/devices.json` — Curtis's specific topology (DO NOT edit).
- `~/.megingjord/devices.json` — operator-specific overlay (auto-generated).

## Related skills

- `network-platform-resources` — full inventory of compute platforms.
- `openclaw-availability-utilization` — OpenClaw gateway operations.
- `openrouter-free-failover` — OpenRouter cloud fallback.
