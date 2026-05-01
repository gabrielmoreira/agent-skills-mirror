---
name: mem-watchdog-ops
description: Operate and tune Crostini Mem Watchdog for low-memory development sessions. Use for status triage, log interpretation, and safe threshold tuning.
argument-hint: "[goal: status|logs|tune|preflight] [profile: balanced|conservative|playwright]"
user-invocable: true
disable-model-invocation: false
---

# Mem Watchdog Ops Skill

Use this skill when working in constrained Crostini environments where VS Code, Chrome/Playwright, and extension host memory spikes can trigger OOM.

## Ground Rules

- Never read or reason from `SwapFree` values on Crostini.
- Prefer `systemctl --user` only — never `sudo systemctl`.
- Treat the mem-watchdog daemon as independent runtime authority.
- For tuning, use extension settings (`memWatchdog.*`) so the extension writes config and restarts service safely.

## Fast Workflows

1. **Status snapshot**
   - Use chat participant command: `/memwatchdog status`
   - Or run helper: `~/.copilot/skills/mem-watchdog-ops/watchdog-snapshot.sh`

2. **Recent actions / diagnosis**
   - `/memwatchdog logs`
   - Look for action markers in journal:
     - `ACTION(SIGTERM):`
     - `ACTION(SIGKILL):`
     - `RECOVERY(SIGTERM):`

3. **Apply tuning profile**
   - `/memwatchdog tune balanced` — general dev use (warn 3.4 GB, emerg 3.8 GB)
   - `/memwatchdog tune conservative` — earlier intervention (warn 3.0 GB, emerg 3.4 GB)
   - `/memwatchdog tune playwright` — more headroom for automation (warn 3.8 GB, emerg 4.2 GB)

4. **Manual protective action**
   - `/memwatchdog act kill chrome`
   - `/memwatchdog act restart service`

## Tuning Guidance

- **balanced**: general dev use — recommended for Copilot Chat multi-agent workloads that peak at 3.0–3.5 GB
- **conservative**: earlier intervention, safer on tight RAM — may cause more Chrome kills
- **playwright**: more headroom for headed browser automation sessions

When recommending profile changes, explain expected trade-off between stability and interruption frequency.

## Kill Hierarchy (daemon v20260329.1+)

| Condition | Action |
|---|---|
| `MemAvailable ≤ 15%` | SIGKILL Chrome/Playwright |
| `MemAvailable ≤ 25%` | SIGTERM Chrome/Playwright (deferred if Playwright active) |
| PSI full avg10 > 25% | SIGTERM Chrome (deferred if Playwright active) |
| VS Code RSS ≥ 3.8 GB | SIGKILL Chrome (always — even during Playwright sessions); if none → kill_vscode_main() |
| VS Code RSS ≥ 3.4 GB | SIGTERM Chrome (deferred if Playwright active); if none → kill helper (Shared Process, File Watcher, Network Service); if none → cgroup throttle/reclaim |
| RSS velocity spike | Kill lowest-value helper — never a language server or Extension Host at normal severity |
| Chrome PIDs > 3 | SIGKILL oldest excess (skipped when Playwright is active) |

## Playwright Awareness (daemon v20260329.1+, Issue #109)

The daemon detects active Playwright sessions via `pgrep -f 'node.*playwright'`.

**When Playwright is active:**
- `CHROME-EXCESS` cap enforcement is skipped — Playwright legitimately spawns 5-10 Chrome PIDs
- Non-critical Chrome kills (WARN, ACCEL, Stage 2-3) are deferred — callers fall through to helper kills or cgroup throttle/reclaim
- EMERGENCY and Stage 4 **always** kill Chrome regardless — genuine OOM must be prevented

**Before launching Playwright automation:**
1. Check memory status: `/memwatchdog status`
2. If RSS is already above 3.0 GB, consider applying the playwright profile: `/memwatchdog tune playwright`
3. Close any idle Chrome browsers from previous sessions

**If the watchdog kills Playwright Chrome during automation:**
- This only happens at EMERGENCY level (≥3.8 GB RSS or ≤15% free memory)
- Consider: closing other VS Code windows, reducing open editor tabs, or restarting the Extension Host to reclaim memory before retrying

## Key Repo References

- [Daemon logic](../../mem-watchdog.sh)
- [Extension activation](../../extension.js)
- [Dashboard/actions](../../commands.js)
- [Config bridge](../../configWriter.js)
- [System stability doc](../../../../docs/technical/system-stability.md)
