---
name: network-platform-resources
description: Inventory of all network-accessible compute platforms, connection methods, credentials, and specs. Load this skill when a task could benefit from remote execution, offloading, or cross-platform deployment.
argument-hint: "[goal: connect|status|inventory|offload] [target: device-id|all]"
user-invocable: true
disable-model-invocation: false
---

# Network Platform Resources

## Purpose

Provide every AI agent session with an always-current inventory of reachable compute platforms, how to connect, what's installed, and when to offload work.

## Fleet Discovery

Fleet topology is **auto-detected** at runtime via `fleet-config.js`:
- IPs resolved from `.env` overrides or `tailscale status --json`
- Device metadata from `inventory/devices.json`
- Run `node scripts/global/fleet-config.js profile` for current state

## Platform Inventory

Devices are defined in `inventory/devices.json`. Key roles:

### Primary Dev Machine (local)
- Role: IDE host, agent execution, dashboard
- Constraints: Low memory — check mem-watchdog before heavy ops
- Crostini is NAT'd — cross-machine networking uses Tailscale

### SML Node (remote inference tier)
- Role: Lightweight local inference (routing, classification)
- Ollama with small models (≤1B params)
- Constraints: ~2-3 GB RAM, tiny models only

### Inference Host (remote compute)
- Role: Heavy compute, daemon hosting (OpenClaw Gateway)
- 16 GB RAM, runs 7B models via Ollama + LiteLLM
- Constraints: Check fleet-config profile before assuming reachable

## Connection Method

All cross-machine networking uses **Tailscale VPN mesh**:
- WireGuard encrypted, bypasses NAT/firewall
- SSH via ProxyCommand: `sudo tailscale nc %h %p`
- Auth: Ed25519 key pair (passwordless)
- SSH config references device alias from `inventory/devices.json`

### Quick Connect
```bash
ssh <device-id>
ssh <device-id> "<remote-command>"
scp -o ProxyCommand="sudo tailscale nc %h %p" file.txt $FLEET_SSH_USER@<ip>:<path>
```

### Prerequisites
1. Tailscale daemon running (start with `--tun=userspace-networking` on Crostini)
2. Tailscale on remote: system service (auto-start)
3. OpenSSH on remote: `sshd` service (auto-start)

### Troubleshooting

| Symptom | Fix |
|---------|-----|
| SSH timeout | Start tailscaled with `--tun=userspace-networking` |
| Tailscale logged out | `sudo tailscale up` → open URL in browser |
| SSH asks for password | Re-copy pubkey to remote authorized_keys |
| Ping works, SSH doesn't | Add firewall rule for port 22 |

## When to Offload

| Trigger | Action |
|---------|--------|
| Memory pressure (mem-watchdog) | Offload build/test to fleet |
| Long-running daemon (OpenClaw) | Always on inference host |
| Heavy npm install / build | Faster on fleet node |
| Playwright multi-browser | Offload to avoid OOM |

## When to Keep Local
| Scenario | Reason |
|----------|--------|
| IDE + Copilot sessions | Already here |
| Quick edits / git ops | Lower latency |
| Cloudflare deploys | Tokens configured locally |

## Adding New Platforms

1. Install Tailscale, authenticate with same account
2. Install OpenSSH server
3. Copy SSH pubkey to new machine's authorized_keys
4. Add `Host` entry in `~/.ssh/config`
5. Add device to `inventory/devices.json`
6. Optionally set `FLEET_IP_<DEVICE_ID>` in `.env`
7. Test: `ssh <new-alias> echo "OK"`
