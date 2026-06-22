---
name: fleet-portable-config
description: Adapt the Megingjord harness to a new operator's fleet topology without hand-editing inventory files. Use when first activating the harness on a new host or onboarding a new fleet.
argument-hint: ""
user-invocable: true
disable-model-invocation: false
type: skill
---

# Fleet Portable Configuration

The harness ships **generic** `inventory/*.example.json` templates. Operator-specific topology lives in `~/.megingjord/` overlays merged by `scripts/global/resolve-inventory.js`.

## Workflow

```
1. Install Tailscale + authenticate:
     tailscale up

2. Run discovery (IT-allowed):
     bash scripts/global/fleet-discover.sh
   → writes ~/.megingjord/devices.json

3. Verify merged inventory:
     node scripts/global/fleet-config.js fleet
   → resolveInventory: example → overlay → FLEET_IP_* env

4. Bootstrap + doctor:
     npm run harness:setup
     npm run harness:doctor

5. Dashboard Fleet Setup wizard (Fleet view):
     /api/fleet/setup/* — credentials to keychain or .env (never localStorage)

6. (Optional) Cloud + probe:
     npm run capability:probe
```

## Reference files

- `inventory/devices.example.json` — generic 2-node template (committed)
- `~/.megingjord/devices.json` — operator overlay (never committed)
- `docs/howto/fleet-it-setup.md` — IT runbook (#3175)

## Related skills

- `network-platform-resources` — compute platform inventory; local overlay at `~/.megingjord/`
- `openrouter-free-failover` — OpenRouter cloud fallback
