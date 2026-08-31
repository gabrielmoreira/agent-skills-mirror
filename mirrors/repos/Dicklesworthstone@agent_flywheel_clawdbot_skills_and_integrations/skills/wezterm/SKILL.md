---
name: wezterm
description: >-
  Manage WezTerm mux servers for AI agent swarms on high-RAM servers (512GB+).
  Use when wezterm mux unresponsive, agent sessions need rescue, tuning scrollback,
  or configuring persistent remote sessions.
---

<!-- TOC: Quick Diagnosis | The Problem | Performance Tuning | Emergency Rescue | Mux Operations | Persistent Sessions | CLI Reference | Maintenance -->

# WezTerm — High-RAM Agent Swarm Management

> **Core Principle:** WezTerm mux replaces tmux. Leverage massive RAM (512GB+) for agent swarms. Never nest multiplexers.

---

## Quick Diagnosis

```bash
# One-liner status
echo "Mux: $(ps aux | grep -c '[w]ezterm-mux') procs | $(wezterm cli list --format json 2>/dev/null | jq length) panes | RSS: $(ps -eo rss,args | grep '[w]ezterm-mux' | awk '{sum+=$1} END {printf "%.1fGB", sum/1024/1024}')"

# Is mux running?
ps aux | grep wezterm-mux | grep -v grep

# Memory usage
ps -eo pid,rss,args | grep wezterm-mux | awk '{printf "%.1fGB\n", $2/1024/1024}'

# Recent logs
tail -20 /run/user/$(id -u)/wezterm/wezterm-mux-server-log-*.txt

# Connection test
wezterm cli list --format json | jq length

# Socket status
ls -la /run/user/$(id -u)/wezterm/sock
```

---

## The Agent Swarm Problem

When running 20+ AI agents (Claude Code, Codex, Gemini CLI), each agent produces continuous output, runs for hours, spawns subprocesses, and operates in parallel. This overwhelms WezTerm's defaults.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          THE FAILURE CASCADE                                  ┃
┃                                                                               ┃
┃  1. Output buffer fills        →  parser falls behind                         ┃
┃  2. Coalesce delay accumulates →  lag builds up                               ┃
┃  3. Caches thrash              →  CPU spikes on render                        ┃
┃  4. Socket buffers fill        →  connection hangs                            ┃
┃  5. You restart mux            →  ALL SESSIONS DIE (use reptyr first!)        ┃
┃                                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Default Assumptions vs Reality

| WezTerm Assumes | Reality with Agent Swarms |
|:----------------|:--------------------------|
| ~100 lines/sec | 1,000+ lines/sec across panes |
| Occasional scrollback access | Scrollback is primary debug tool |
| Few panes | 20+ panes, all active |
| Cache hits common | Rapid context switches = cache misses |

---

## Performance Tuning (High-RAM)

### THE EXACT PROMPT — Auto-Tune for Your RAM

```bash
# Auto-tune using linear interpolation (recommended)
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/misc_coding_agent_tips_and_scripts/main/wezterm-mux-tune.sh | bash

# Preview without applying
./wezterm-mux-tune.sh --dry-run

# Calculate for specific RAM
./wezterm-mux-tune.sh --ram 200

# Use exact fixed profile
./wezterm-mux-tune.sh --profile 512

# Restore from backup
./wezterm-mux-tune.sh --restore
```

### THE EXACT PROMPT — 512GB Manual Profile

Add to `~/.wezterm.lua` before `return config`:

```lua
-- 512GB HIGH-RAM PROFILE
config.scrollback_lines = 10000000
config.mux_output_parser_buffer_size = 16 * 1024 * 1024
config.mux_output_parser_coalesce_delay_ms = 1
config.ratelimit_mux_line_prefetches_per_second = 1000
config.shape_cache_size = 65536
config.line_state_cache_size = 65536
config.line_quad_cache_size = 65536
config.line_to_ele_shape_cache_size = 65536
config.glyph_cache_image_cache_size = 4096
```

### Settings Quick Reference

| Setting | Default | 512GB | Purpose |
|:--------|--------:|------:|:--------|
| `scrollback_lines` | 3,500 | 10M | History per pane |
| `mux_output_parser_buffer_size` | 128KB | 16MB | PTY batch buffer |
| `mux_output_parser_coalesce_delay_ms` | 3 | 1 | Parse latency |
| `ratelimit_mux_line_prefetches_per_second` | 50 | 1000 | Scroll speed |
| `shape_cache_size` | 1,024 | 65,536 | Font cache |
| `line_state_cache_size` | 1,024 | 65,536 | Line attr cache |
| `line_quad_cache_size` | 1,024 | 65,536 | GPU geometry |
| `glyph_cache_image_cache_size` | 256 | 4,096 | Rasterized glyphs |

### Profiles by RAM

| RAM | scrollback | buffer | caches | prefetch | Memory footprint |
|----:|-----------:|-------:|-------:|---------:|-----------------:|
| 64GB | 1M | 2MB | 8K | 500 | 3-8 GB |
| 128GB | 2M | 4MB | 16K | 750 | 5-15 GB |
| 256GB | 5M | 8MB | 32K | 500 | 8-25 GB |
| 512GB | 10M | 16MB | 64K | 1000 | 15-60 GB |

**After applying:** Restart mux to load new settings.

---

## Emergency Session Rescue

> **Scenario:** Mux unresponsive but agents still running. DON'T kill mux yet!

### THE EXACT PROMPT — reptyr Rescue Workflow

```bash
# 1. Connect via plain SSH (bypass broken mux)
ssh user@host

# 2. Setup
sudo apt-get install -y reptyr
sudo sysctl -w kernel.yama.ptrace_scope=0

# 3. Create rescue session
tmux new-session -d -s rescue -x 200 -y 50

# 4. Find agents
ps -eo pid,args | grep -E 'claude --dangerously|codex --dangerously' | grep -v grep

# 5. Migrate each agent
for pid in $(ps -eo pid,args | grep -E 'claude --dangerously|codex --dangerously' | grep -v grep | awk '{print $1}'); do
  tmux new-window -t rescue -n "agent-$pid"
  tmux send-keys -t "rescue:agent-$pid" "reptyr -T $pid" Enter
  sleep 0.5
done

# 6. Verify migrations
for win in $(tmux list-windows -t rescue -F "#{window_name}" | grep agent); do
  tmux capture-pane -t "rescue:$win" -p | grep -qE "bypass|Claude" && echo "✓ $win" || echo "✗ $win"
done

# 7. NOW safe to kill mux
pkill -9 -f wezterm-mux

# 8. Restore security
sudo sysctl -w kernel.yama.ptrace_scope=1

# 9. Restart mux
wezterm-mux-server --daemonize

# 10. Access rescued agents
tmux attach -t rescue  # Ctrl-b w to browse
```

### reptyr Failure Modes

| Error | Cause | Fix |
|:------|:------|:----|
| "Operation not permitted" | ptrace blocked | `sudo sysctl -w kernel.yama.ptrace_scope=0` |
| "shares process group" | Process has children | Use `reptyr -T` (not plain `reptyr`) |
| "Unable to attach" | Additional protections | Cannot migrate; will be lost |

**Success rate:** 50-70%. Older/idle sessions migrate better than active ones with many subprocesses.

---

## Mux Server Operations

### Start/Stop

```bash
# Start (daemonized)
wezterm-mux-server --daemonize

# Stop gracefully
pkill -f wezterm-mux-server

# Force stop (kills sessions!)
pkill -9 -f wezterm-mux-server

# Restart (loses sessions unless rescued first)
pkill -9 -f wezterm-mux; wezterm-mux-server --daemonize

# Restart via systemd (if configured)
systemctl --user restart wezterm-mux-server
```

### Kill Stuck Proxy Processes

Safe to kill — won't affect mux sessions:

```bash
pkill -f 'wezterm cli.*proxy'
```

### Why Mux Degrades Over Time

| Cause | Symptom | Fix |
|:------|:--------|:----|
| Buffer overflow | Connection timeout | Increase `mux_output_parser_buffer_size` |
| Cache thrashing | High CPU on scroll | Increase cache sizes |
| Session accumulation | Memory bloat | Periodic mux restart |
| Scrollback buildup | GB of RAM usage | Lower `scrollback_lines` or restart |

---

## Persistent Sessions Setup

### Remote Server (one-time)

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/wezterm-mux-server.service << 'EOF'
[Unit]
Description=WezTerm Mux Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/wezterm-mux-server --daemonize=false
Restart=on-failure
RestartSec=5
Environment=WEZTERM_LOG=warn

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now wezterm-mux-server
sudo loginctl enable-linger $USER
```

### Local Config (SSH domain)

```lua
config.ssh_domains = {
  {
    name = 'myserver',
    remote_address = '10.0.0.1',
    username = 'ubuntu',
    multiplexing = 'WezTerm',  -- Key setting
    assume_shell = 'Posix',
  },
}
```

---

## CLI Quick Reference

| Task | Command |
|:-----|:--------|
| List panes | `wezterm cli list` |
| List panes (JSON) | `wezterm cli list --format json` |
| Split right | `wezterm cli split-pane --right` |
| Split bottom | `wezterm cli split-pane --bottom` |
| Send text | `wezterm cli send-text --pane-id N "cmd\n"` |
| New tab | `wezterm cli spawn` |
| New tab in domain | `wezterm cli spawn --domain-name SSH:host` |
| Connect to mux | `wezterm connect unix` |
| Zoom toggle | `wezterm cli zoom-pane --toggle` |

---

## Maintenance Checklist

- [ ] **Weekly:** Check mux memory, consider restart if > 50GB RSS
- [ ] **Before restart:** Check for active agents (use reptyr if needed)
- [ ] **After tuning:** Restart mux to apply new settings
- [ ] **Version mismatch:** Client/server MUST match exactly

```bash
# Check version match
wezterm --version                    # local
ssh host 'wezterm --version'         # remote

# Check mux memory
ps -eo rss,args | grep '[w]ezterm-mux' | awk '{printf "RSS: %.1fGB\n", $1/1024/1024}'
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|:--------|:------|:----|
| Connection timeout | Buffer overflow | Increase `mux_output_parser_buffer_size` |
| Laggy scrolling | Low prefetch rate | Increase `ratelimit_mux_line_prefetches_per_second` |
| High CPU on render | Cache thrashing | Increase all cache sizes |
| Truncated history | Small scrollback | Increase `scrollback_lines` |
| "Broken pipe" in logs | Client disconnect | Check network stability |
| "Checking server version" hangs | Mux overloaded | Rescue sessions, restart mux |
| Version mismatch error | Client/server differ | Update both to same version |

### Log Locations

```bash
# Mux server log
/run/user/$(id -u)/wezterm/wezterm-mux-server-log-*.txt

# Socket path
/run/user/$(id -u)/wezterm/sock
```

---

## References

| Topic | File |
|:------|:-----|
| Full CLI commands | [COMMANDS.md](references/COMMANDS.md) |
| Persistent sessions deep-dive | [PERSISTENT-SESSIONS.md](references/PERSISTENT-SESSIONS.md) |
| Performance tuning deep-dive | [PERFORMANCE-TUNING.md](references/PERFORMANCE-TUNING.md) |
