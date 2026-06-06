# Port Registry — `.hi/deployment/dev-local/` Mode

> **Scope**: This port registry is authoritative only when `DEPLOY_MODE=dev-local`
>
> **Purpose**: Document all service ports for local development
>
> **Shared Registry**: Root-level `.hi/ports.md` provides defaults; this file overrides per-mode

---

## Development Services (dev-local)

| Service/Component | Port | Protocol | Notes |
|---|---|---|---|
| *Add your dev services here* | | | |

---

## Key Guidelines

1. **All ports use `localhost`** — no network exposure
2. **Use allocation ranges** from root `.hi/ports.md` (3000–3099 for APIs, etc.)
3. **No TLS needed** — HTTP only for simplicity
4. **Services start in order** — see `.hi/scripts/dev-launch.ps1` or equivalent
5. **Update root registry too** — this file supplements, not replaces `.hi/ports.md`

---

## Launch Commands

```powershell
# Validate this mode's port registry
python .hi/engine/port_validator.py . --report

# Start all services
pwsh .hi/scripts/dev-launch.ps1
```

---

## See Also

- [`.hi/ports.md`](../../../ports.md) — Root port registry
- [`.hi/agents/hia-ports.agent.md`](../../../agents/tier-2/specialists/hia-ports.agent.md) — Port manager agent
