---
name: loop
description: "Arms a Cursor-session interval loop: parse /loop [interval] <prompt>, emit AGENT_LOOP_TICK sentinels from a monitored PowerShell/bash shell, run the prompt on each tick, and stop by PID. Use when the user says /loop, every 5m, or keep checking. Not for /goal-loop GOAL.md autonomy, OS crontab, or one-shot tasks."
version: 1.0.1
---

# Loop

Run a prompt or skill in this session on a recurring or variable interval. The agent arms a monitored background shell loop that emits a sentinel line on each tick; Cursor's `notify_on_output` wakes the agent, which reads the latest payload and executes the prompt.

## When to Use

- User types `/loop [interval] <prompt>` or says "run X every 5 minutes", "repeat /foo", "keep checking Y".
- User wants recurring local work (check deploy status, poll a log, re-run tests) without OS cron.
- User wants the agent to self-pace based on observable events (git ref advance, log line, file change, CI completion).

Do **not** use for one-shot tasks — just run the prompt directly.

## Prerequisites

- A monitored shell with `notify_on_output` support (Cursor integrated terminal).
- Windows host is primary (PowerShell). Adapt loop syntax to the user's shell. The bash examples below are illustrative; use PowerShell equivalents on Windows.
- No external dependencies beyond the shell.

## Procedure

### 1. Parse the command

Accept `/loop [interval] <prompt>`.

| Input form | Example | Meaning |
|---|---|---|
| Leading interval | `5m /foo` | Fixed schedule, 5-minute cadence |
| Leading interval (words) | `30s check status` | Fixed schedule, 30-second cadence |
| Trailing interval | `check deploy every 5m` | Fixed schedule, 5-minute cadence |
| Trailing interval (words) | `run tests every 10 minutes` | Fixed schedule, 10-minute cadence |
| No interval | `check CI status` | Dynamic mode; agent chooses next delay after each run |
| Empty prompt | `/loop` | Show `Usage: /loop [interval] <prompt>` and stop |

Convert unit words to short units: `seconds`→`s`, `minutes`→`m`, `hours`→`h`, `days`→`d`. Use intervals like `30s`, `5m`, `2h`, `1d`.

### 2. Fixed Schedule

Arm one background shell loop with `notify_on_output`.

**Bash (illustrative):**

```bash
while true; do
  sleep <seconds>
  echo 'AGENT_LOOP_TICK_<purpose> {"prompt":"<prompt>"}'
done
```

**PowerShell (Windows primary):**

```powershell
while ($true) {
  Start-Sleep -Seconds <seconds>
  Write-Output 'AGENT_LOOP_TICK_<purpose> {"prompt":"<prompt>"}'
}
```

Steps:

1. Check existing terminals for an already-running matching loop. Do not create duplicate fixed loops.
2. Start one background shell loop with `notify_on_output` enabled.
3. Use a unique sentinel per loop and a regex such as `^AGENT_LOOP_TICK_<purpose>`. Replace `<purpose>` with a short unique tag (e.g. `deploycheck`).
4. Smoke-check once to confirm clean startup (no syntax error, no immediate crash).
5. Run the prompt **once immediately** after arming the loop — the first sentinel arrives only after the initial sleep, so startup does not double-run.
6. Track the PID so the agent can stop the loop if asked.
7. Confirm to the user: the interval, that the prompt already ran once, when the first tick will arrive, and that the loop fires on each tick until stopped.

On later ticks: give a short update of what changed since the last tick.

On stop: kill the tracked PID, await the shell task so its completion notification is consumed, and say the loop has stopped and why.

### 3. Dynamic Schedule

The user wants the agent to self-pace. Decide what makes the next iteration worth running — passage of time or an observable event.

1. **Run the prompt now.**
2. **If the next run is gated on an event** (git ref advancing, log line matching, file changing, CI check completing), arm a background watcher that emits the sentinel only when the event fires, with `notify_on_output` on `^AGENT_LOOP_WAKE_<purpose>`. Arm once; skip on later ticks if it's still running.

   Example watcher (bash):

   ```bash
   while true; do
     if <event-test-command>; then
       echo 'AGENT_LOOP_WAKE_<purpose> {"prompt":"<prompt>"}'
       break
     fi
     sleep 10
   done
   ```

3. **At the end of the turn, arm a one-shot time-based wake:**

   ```bash
   sleep <seconds>
   echo 'AGENT_LOOP_WAKE_<purpose> {"prompt":"<prompt>"}'
   ```

   - With a watcher armed: this is the **fallback heartbeat** — lean long so idle ticks aren't pure overhead.
   - Without a watcher: this is the **cadence** — pick a delay based on when the result is worth checking again.

4. **On wake:** read the latest matching payload line, execute its `prompt`, then re-arm the next heartbeat (and re-arm the watcher only if it exited). If both an output wake and a completion notification arrive, act on the output and ignore the completion.
5. **To stop:** kill any watcher PID and don't arm the next heartbeat.
6. Confirm to the user: that you're self-pacing, whether a watcher is the primary wake signal, what fallback delay you picked, and that the prompt already ran.

### 4. Prompt Payload

Wake notifications include an output file path, not a submitted prompt. Put the prompt beside the sentinel, preferably as JSON:

```
AGENT_LOOP_TICK_<purpose> {"prompt":"<actual prompt text>"}
```

On wake, read the latest matching line and act on its `prompt`. The prompt may vary by tick — the agent can update it between iterations.

### 5. Stop

When the user asks to stop:

1. Kill any tracked loop/sleeper PID.
2. Await the shell task so its completion notification is consumed and does not wake the agent later.
3. Do not schedule another dynamic wake.
4. Say the loop has stopped and why.

## Pitfalls

- **Duplicate loops:** Always check existing terminals for an already-running matching loop before arming a new one. Do not create duplicate fixed loops or dynamic sleepers.
- **Double-run on startup:** The first sentinel arrives only after the initial sleep. Run the prompt once immediately after arming, not on the first tick.
- **Sentinel collisions:** Use a unique sentinel per loop (`<purpose>` tag) so unrelated output does not trigger notifications.
- **Noisy commands inside the loop:** Avoid commands that produce output other than the sentinel — extra lines can cause spurious wake notifications.
- **Completion notification after stop:** If you kill a loop but don't await the shell task, Cursor's completion notification may wake the agent later. Always await the task after killing.
- **Watcher already running:** On dynamic ticks, if the watcher is still running, skip re-arming it — only re-arm if it exited.
- **Conflicting wake signals:** If both an output wake and a completion notification arrive, act on the output and ignore the completion.
- **Shell syntax:** Adapt loop syntax to the user's shell. The bash examples are illustrative; on Windows use PowerShell `while ($true) { ... Start-Sleep }`.

## Verification

1. **Startup smoke check:** After arming, confirm the shell task is running without immediate error.

   PowerShell:
   ```powershell
   Get-Process -Id <PID> | Select-Object Id,ProcessName,StartTime
   ```

   Bash:
   ```bash
   ps -p <PID> -o pid,comm,start
   ```

   Expected: process exists and is running.

2. **Sentinel regex:** Confirm `notify_on_output` is armed on `^AGENT_LOOP_TICK_<purpose>` (fixed) or `^AGENT_LOOP_WAKE_<purpose>` (dynamic).

3. **First tick timing:** The first sentinel should arrive after `<seconds>`, not immediately. If it arrives immediately, the loop body ran before the sleep — fix the ordering.

4. **Stop verification:** After killing the PID and awaiting the task, confirm no further wake notifications arrive for that sentinel.

   PowerShell:
   ```powershell
   Get-Process -Id <PID> 2>$null
   ```

   Expected: "No such process" or empty — the loop is fully stopped.

## Guidance

- Title shell commands as `Loop <schedule>: <prompt>` (e.g. `Loop every 5m: check deploy status`).
- Prefer monitored shell output over OS cron when the agent needs wake notifications; stdout stays attached to the monitored task.
- Use a unique sentinel per loop so unrelated output does not trigger notifications.
- Avoid noisy commands inside the loop — only the sentinel line should be emitted.
- On later fixed-schedule ticks, give a short update of what changed since the last tick, not a full re-run summary.
- On dynamic ticks, state the chosen fallback delay and whether the watcher is the primary signal.

## Related skills

- None. This is a self-contained scheduling primitive.
