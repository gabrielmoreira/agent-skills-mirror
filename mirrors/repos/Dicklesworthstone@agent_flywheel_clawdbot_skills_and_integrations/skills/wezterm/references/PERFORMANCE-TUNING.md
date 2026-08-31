# WezTerm Performance Tuning — Reference

## Table of Contents
- [The Agent Swarm Problem](#the-agent-swarm-problem)
- [Settings Explained](#settings-explained)
- [Configuration Profiles](#configuration-profiles)
- [Auto-Tuning Script](#auto-tuning-script)
- [Installation](#installation)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## The Agent Swarm Problem

When running 20+ AI agents (Claude Code, Codex, Gemini CLI), each agent:

| Behavior | Impact |
|:---------|:-------|
| Produces continuous output | Tool calls, code diffs, test results |
| Runs for hours | Accumulates massive scrollback |
| Spawns subprocesses | Tests, builds, linters |
| Operates in parallel | 20+ simultaneous output streams |

### Default Assumptions vs Reality

| WezTerm Assumes | Reality with Agent Swarms |
|:----------------|:--------------------------|
| ~100 lines/sec | 1,000+ lines/sec across panes |
| Occasional scrollback access | Scrollback is primary debug tool |
| Few panes | 20+ panes, all active |
| Cache hits common | Rapid context switches = cache misses |

### The Failure Cascade

```
1. Output buffer fills        →  parser falls behind
2. Coalesce delay accumulates →  lag builds up
3. Caches thrash              →  CPU spikes on render
4. Socket buffers fill        →  connection hangs
5. You restart mux            →  ALL SESSIONS DIE
```

**Prevention:** Tune settings for your RAM. **Mitigation:** Use reptyr rescue before killing mux.

---

## Settings Explained

### `scrollback_lines`

| | |
|:--|:--|
| **Default** | 3,500 |
| **Purpose** | Maximum history lines per pane |
| **Problem** | A single `cargo build` produces 10,000+ lines |

**By RAM:**

| RAM | Value | Memory Headroom |
|----:|------:|----------------:|
| 64 GB | 1,000,000 | ~6 GB |
| 128 GB | 2,000,000 | ~12 GB |
| 256 GB | 5,000,000 | ~30 GB |
| 512 GB | 10,000,000 | ~60 GB |

**Memory math:** ~6 bytes/line × lines × panes. 10M lines × 20 panes = ~1.2GB base + attribute overhead.

---

### `mux_output_parser_buffer_size`

| | |
|:--|:--|
| **Default** | 128 KB |
| **Purpose** | Buffer for raw PTY output before parsing |
| **Problem** | Small buffer forces frequent small parses |

**By RAM:**

| RAM | Value | Handles |
|----:|------:|:--------|
| 64 GB | 2 MB | Moderate bursts |
| 128 GB | 4 MB | Large diffs |
| 256 GB | 8 MB | Test suite output |
| 512 GB | 16 MB | Anything |

**Why it matters:** Large bursts (cargo build, test output) need room. Small buffer = parser bottleneck = lag cascade.

---

### `mux_output_parser_coalesce_delay_ms`

| | |
|:--|:--|
| **Default** | 3 ms |
| **Purpose** | Wait time to batch fragmented writes |
| **Problem** | 3ms × 1,000 chunks/sec = 3 sec accumulated lag |

**By use case:**

| Use Case | Value | Rationale |
|:---------|------:|:----------|
| TUI-heavy (vim, htop) | 3 ms | Smoother rendering |
| Agent swarms | 1 ms | Minimize lag |
| Benchmarking | 0 ms | Raw throughput |

**Trade-off:** Lower = less lag but more CPU. Higher = batches better but accumulates delay under load.

---

### `ratelimit_mux_line_prefetches_per_second`

| | |
|:--|:--|
| **Default** | 50 |
| **Purpose** | Scroll prefetch rate |
| **Problem** | At 50/sec, scrolling 10,000 lines takes 200 seconds |

**Recommended:** 500-1000 for all systems.

**Why:** Agent output debugging requires fast scrollback. Default is painfully slow for large histories.

---

### Cache Settings

WezTerm maintains several caches to avoid expensive recomputation:

| Cache | Default | Purpose |
|:------|--------:|:--------|
| `shape_cache_size` | 1,024 | Font shaping results |
| `line_state_cache_size` | 1,024 | Line colors/attributes |
| `line_quad_cache_size` | 1,024 | GPU render geometry |
| `line_to_ele_shape_cache_size` | 1,024 | Line-to-element mapping |
| `glyph_cache_image_cache_size` | 256 | Rasterized glyphs |

**By RAM:**

| RAM | shape | line_state | line_quad | line_to_ele | glyph |
|----:|------:|-----------:|----------:|------------:|------:|
| 64 GB | 8,192 | 8,192 | 8,192 | 8,192 | 512 |
| 128 GB | 16,384 | 16,384 | 16,384 | 16,384 | 1,024 |
| 256 GB | 32,768 | 32,768 | 32,768 | 32,768 | 2,048 |
| 512 GB | 65,536 | 65,536 | 65,536 | 65,536 | 4,096 |

**Why:** Rapid pane switching = cache misses. Larger caches = fewer recomputations = less CPU.

---

## Configuration Profiles

### 64GB RAM (Conservative)

Memory footprint: **3-8 GB** under load.

```lua
-- ============================================================
-- PERFORMANCE TUNING (64GB system)
-- ============================================================
config.scrollback_lines = 1000000
config.mux_output_parser_buffer_size = 2 * 1024 * 1024
config.mux_output_parser_coalesce_delay_ms = 2
config.ratelimit_mux_line_prefetches_per_second = 500
config.shape_cache_size = 8192
config.line_state_cache_size = 8192
config.line_quad_cache_size = 8192
config.line_to_ele_shape_cache_size = 8192
config.glyph_cache_image_cache_size = 512
```

---

### 128GB RAM (Moderate)

Memory footprint: **5-15 GB** under load.

```lua
-- ============================================================
-- PERFORMANCE TUNING (128GB system)
-- ============================================================
config.scrollback_lines = 2000000
config.mux_output_parser_buffer_size = 4 * 1024 * 1024
config.mux_output_parser_coalesce_delay_ms = 1
config.ratelimit_mux_line_prefetches_per_second = 750
config.shape_cache_size = 16384
config.line_state_cache_size = 16384
config.line_quad_cache_size = 16384
config.line_to_ele_shape_cache_size = 16384
config.glyph_cache_image_cache_size = 1024
```

---

### 256GB RAM (Aggressive)

Memory footprint: **8-25 GB** under load.

```lua
-- ============================================================
-- HIGH-RAM PERFORMANCE TUNING (256GB system)
-- ============================================================
config.scrollback_lines = 5000000
config.mux_output_parser_buffer_size = 8 * 1024 * 1024
config.mux_output_parser_coalesce_delay_ms = 1
config.ratelimit_mux_line_prefetches_per_second = 500
config.shape_cache_size = 32768
config.line_state_cache_size = 32768
config.line_quad_cache_size = 32768
config.line_to_ele_shape_cache_size = 32768
config.glyph_cache_image_cache_size = 2048
```

---

### 512GB RAM (Maximum)

Memory footprint: **15-60 GB** under load.

```lua
-- ============================================================
-- HIGH-RAM PERFORMANCE TUNING (512GB system)
-- ============================================================
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

---

## Auto-Tuning Script

The `wezterm-mux-tune.sh` script uses **linear interpolation** to calculate optimal settings for any RAM amount.

### Usage

```bash
# Auto-detect RAM, interpolate settings
curl -fsSL https://raw.githubusercontent.com/Dicklesworthstone/misc_coding_agent_tips_and_scripts/main/wezterm-mux-tune.sh | bash

# Preview without applying
./wezterm-mux-tune.sh --dry-run

# Calculate for specific RAM
./wezterm-mux-tune.sh --ram 200

# Use exact fixed profile
./wezterm-mux-tune.sh --profile 256

# Restore from backup
./wezterm-mux-tune.sh --restore
```

### Interpolation Anchor Points

| RAM | scrollback | buffer | caches | prefetch |
|----:|-----------:|-------:|-------:|---------:|
| 64 GB | 1M | 2 MB | 8K | 500 |
| 128 GB | 2M | 4 MB | 16K | 750 |
| 256 GB | 5M | 8 MB | 32K | 500 |
| 512 GB | 10M | 16 MB | 64K | 1000 |

Values extrapolate linearly beyond this range (e.g., 768GB gets ~15M scrollback, 24MB buffer).

### How Interpolation Works

For a 200GB system (between 128GB and 256GB anchors):

```
fraction = (200 - 128) / (256 - 128) = 0.5625
scrollback = 2M + 0.5625 × (5M - 2M) = 3.69M
```

This provides smooth scaling rather than hard tiers.

---

## Installation

### Step 1: Backup

```bash
cp ~/.wezterm.lua ~/.wezterm.lua.backup
```

### Step 2: Add Profile

Edit `~/.wezterm.lua` and add the appropriate profile **before** `return config`.

### Step 3: Restart Mux

```bash
pkill -9 -f wezterm-mux && wezterm-mux-server --daemonize
```

### Step 4: Reconnect

Your wezterm client will auto-reconnect, or manually:

```bash
wezterm connect unix
```

---

## Monitoring

### Mux Server Health

```bash
# Is it running?
ps aux | grep wezterm-mux | grep -v grep

# Memory usage (RSS)
ps -eo pid,rss,args | grep wezterm-mux | awk '{printf "RSS: %.1fMB\n", $2/1024}'

# Memory usage (GB)
ps -eo rss,args | grep '[w]ezterm-mux' | awk '{printf "RSS: %.2fGB\n", $1/1024/1024}'

# Recent logs
tail -20 /run/user/$(id -u)/wezterm/wezterm-mux-server-log-*.txt

# Socket status
ls -la /run/user/$(id -u)/wezterm/sock

# Pane count
wezterm cli list --format json | jq length
```

### Live Monitoring

```bash
# Watch memory usage
watch -n5 'ps aux | grep wezterm-mux | grep -v grep | awk "{print \"RSS: \" \$6/1024 \"MB\"}"'

# One-liner status
watch -n5 'echo "Mux: $(ps aux | grep -c "[w]ezterm-mux") procs | $(wezterm cli list --format json 2>/dev/null | jq length) panes | RSS: $(ps -eo rss,args | grep "[w]ezterm-mux" | awk "{sum+=\$1} END {printf \"%.1fGB\", sum/1024/1024}")"'
```

### System Resources

```bash
# Load vs cores
echo "Load: $(uptime | awk -F'load average:' '{print $2}') / $(nproc) cores"

# Memory
free -h | awk '/Mem:/{print "Memory: " $7 " available of " $2}'

# File descriptors
cat /proc/sys/fs/file-nr | awk '{print "FDs: " $1 "/" $3}'
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
| "Checking server version" hangs | Mux overloaded | Rescue sessions, then restart |
| Settings not applying | Didn't restart mux | `pkill -9 -f wezterm-mux && wezterm-mux-server --daemonize` |
| Memory keeps growing | Scrollback accumulation | Consider periodic mux restart |

### After Applying Settings

```bash
# Restart mux to apply
pkill -9 -f wezterm-mux; wezterm-mux-server --daemonize

# Reconnect your client
# (usually auto-reconnects, or: wezterm connect unix)
```

### Version Mismatch

Client and server WezTerm versions must match exactly:

```bash
# Local version
wezterm --version

# Remote version
ssh host 'wezterm --version'
```

If they differ, update the older one.

---

## See Also

- [WezTerm Multiplexing Docs](https://wezterm.org/multiplexing.html)
- [WezTerm Scrollback Docs](https://wezterm.org/scrollback.html)
- [Full Guide](https://github.com/Dicklesworthstone/misc_coding_agent_tips_and_scripts/blob/main/WEZTERM_MUX_PERFORMANCE_TUNING_FOR_AGENT_SWARMS.md)
