---
name: python-debugpy
description: "Debugs Python with breakpoint()/pdb, python -m pdb, pytest --pdb, and debugpy DAP attach to long-lived processes. Use when a test value is wrong, a daemon misbehaves, or step-through inspection is required. Not for print/logging or pytest --showlocals that already explain the failure, nor the language-agnostic 4-phase loop (systematic-debugging)."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, python, pdb, debugpy, breakpoints, dap, post-mortem]
    related_skills: [systematic-debugging, node-inspect-debugger, debugging-hermes-tui-commands]
---

# Python Debugger (pdb + debugpy)

## Overview

Three tools, picked by situation:

| Tool | When |
|---|---|
| **`breakpoint()` + pdb** | Local, interactive, simplest. Add `breakpoint()` in the source, run normally, get a REPL at that line. |
| **`python -m pdb`** | Launch an existing script under pdb with no source edits. Useful for quick poking. |
| **`debugpy`** | Remote / headless / "attach to already-running process." Talks DAP, scriptable from terminal, works for long-lived processes (gateway, daemon, PTY children). |

**Start with `breakpoint()`.** It's the cheapest thing that works.

> **Windows host note:** PowerShell is the primary shell. Use `python -m pdb` (not `python3`). Path separators in commands use `\` on Windows, but pdb breakpoint locations like `b file:line` always use the OS-native path. On Windows, `ss`/`netstat` equivalents are `netstat -ano | findstr 5678`.

## When to Use

- A test fails and the traceback doesn't reveal why a value is wrong
- You need to step through a function and watch a collection mutate
- A long-running process (hermes gateway, tui_gateway) misbehaves and you can't restart it
- Post-mortem: an exception fired in prod-ish code and you want to inspect locals at the crash site
- A subprocess / child (Python `_SlashWorker`, PTY bridge worker) is the actual bug site

**Don't use for:** things `print()` / `logging.debug` solve in under a minute, or things `pytest -vv --tb=long --showlocals` already reveals.

## Prerequisites

- Python 3.10+ (3.13+ recommended for asyncio debugging in pdb)
- For debugpy remote: `pip install debugpy` in the target process's venv
- For remote-pdb: `pip install remote-pdb`
- On Windows: PowerShell terminal with `python` on `PATH`
- On Linux: `ptrace_scope` may need adjustment for PID-attach (see Pitfalls)

## pdb Quick Reference

Inside any pdb prompt (`(Pdb)`):

| Command | Action |
|---|---|
| `h` / `h cmd` | help |
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `unt N` | continue until line N |
| `j N` | jump to line N (same function only) |
| `l` / `ll` | list source around current line / full function |
| `w` | where (stack trace) |
| `u` / `d` | move up / down in the stack |
| `a` | print args of the current function |
| `p expr` / `pp expr` | print / pretty-print expression |
| `display expr` | auto-print expr on every stop |
| `b file:line` | set breakpoint |
| `b func` | break on function entry |
| `b file:line, cond` | conditional breakpoint |
| `cl N` | clear breakpoint N |
| `tbreak file:line` | one-shot breakpoint |
| `!stmt` | execute arbitrary Python (assignments included) |
| `interact` | drop into full Python REPL in current scope (Ctrl+D to exit) |
| `q` | quit |

The `interact` command is the most powerful — you can import anything, inspect complex objects, even call methods that mutate state. Locals are read-only by default; use `!x = 42` from the `(Pdb)` prompt to mutate.

## Procedure

### Recipe 1: Local breakpoint

Easiest. Edit the file:

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

Run the code normally. You land at the `breakpoint()` line with full access to locals.

**HARD RULE: Don't forget to remove `breakpoint()` before committing.** Use `git diff` or a pre-commit grep:

```bash
rg -n 'breakpoint\(\)' --type py
```

PowerShell equivalent:

```powershell
Select-String -Path "*.py" -Pattern "breakpoint\(\)" -Recurse
```

### Recipe 2: Launch a script under pdb (no source edits)

```bash
python -m pdb path/to/script.py arg1 arg2
# Lands at first line of script
(Pdb) b path/to/script.py:42
(Pdb) c
```

### Recipe 3: Debug a pytest test

Use pytest directly (or the project's runner if it is just a thin wrapper around pytest):

```bash
# Drop to pdb on failure (or on any raised exception):
python -m pytest tests/path/to/test_file.py::test_name --pdb

# Drop to pdb at the START of the test:
python -m pytest tests/path/to/test_file.py::test_name --trace

# Show locals in tracebacks without pdb:
python -m pytest tests/path/to/test_file.py --showlocals --tb=long
```

**HARD RULE: pytest-xdist (`-n 4`) and pdb do NOT work together.** Always add `-p no:xdist` or run a single test with `-n 0`:

```bash
python -m pytest tests/foo_test.py::test_bar --pdb -p no:xdist
# or after activating the project venv:
python -m pytest tests/foo_test.py::test_bar --pdb
```

**HARD RULE: Hermetic test wrappers that strip credentials and set `HOME=<tmpdir>` will not reproduce bugs that depend on user config or real API keys.** Debug with raw `pytest` first to repro, then re-confirm under the wrapper.

### Recipe 4: Post-mortem on any exception

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

Or wrap a whole script:

```bash
python -m pdb -c continue script.py
# When it crashes, pdb catches it and you're in the frame of the exception
```

Or set a global hook in a repl/jupyter:

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```

### Recipe 5: Remote debug with debugpy (attach to running process)

For long-lived processes: Hermes gateway, tui_gateway, a daemon, a process that's already misbehaving and can't be restarted clean.

#### Setup

```bash
source .venv/bin/activate   # from the project checkout
pip install debugpy
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install debugpy
```

#### Pattern A: Source-edit — process waits for debugger at launch

Add near the top of the entry point (or inside the function you want to debug):

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # optional: pause immediately once attached
```

Start the process; it blocks on `wait_for_client()`.

#### Pattern B: No source edit — launch with `-m debugpy`

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```

Equivalent for module entry:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

#### Pattern C: Attach to an already-running process

Needs the PID and debugpy preinstalled in the target's environment:

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
# debugpy injects itself into the process. Then attach a client as below.
```

Some kernels/security configs block the ptrace-based injection (`/proc/sys/kernel/yama/ptrace_scope`). Fix with:

```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

#### Connecting a client from the terminal

**Option 1: `debugpy`'s own CLI REPL** — not an official feature, but a tiny DAP client script:

```python
# /tmp/dap_client.py
import socket, json, itertools, time, sys

HOST, PORT = "127.0.0.1", 5678
s = socket.create_connection((HOST, PORT))
seq = itertools.count(1)

def send(msg):
    msg["seq"] = next(seq)
    body = json.dumps(msg).encode()
    s.sendall(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)

def recv():
    header = b""
    while b"\r\n\r\n" not in header:
        header += s.recv(1)
    length = int(header.decode().split("Content-Length:")[1].split("\r\n")[0].strip())
    body = b""
    while len(body) < length:
        body += s.recv(length - len(body))
    return json.loads(body)

send({"type": "request", "command": "initialize", "arguments": {"adapterID": "python"}})
print(recv())
send({"type": "request", "command": "attach", "arguments": {}})
print(recv())
send({"type": "request", "command": "setBreakpoints",
      "arguments": {"source": {"path": sys.argv[1]},
                    "breakpoints": [{"line": int(sys.argv[2])}]}})
print(recv())
send({"type": "request", "command": "configurationDone"})
# ... loop reading events and sending continue/stepIn/etc.
```

This is fine for one-off automation but painful as an interactive UX.

**Option 2: Attach from VS Code / Cursor / Zed** — if the user has one open, they can add a `launch.json`:

```json
{
  "name": "Attach to Hermes",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 },
  "justMyCode": false,
  "pathMappings": [
    { "localRoot": "${workspaceFolder}", "remoteRoot": "/path/to/project" }
  ]
}
```

**Option 3: Ditch DAP, use `remote-pdb`** — usually what you actually want from a terminal agent:

```bash
pip install remote-pdb
```

In your code:

```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # blocks until connection
```

Then from the terminal:

```bash
nc 127.0.0.1 4444
# You get a (Pdb) prompt exactly as if debugging locally.
```

Windows PowerShell (no `nc`):

```powershell
# Use Python as a TCP client:
python -c "import socket; s=socket.create_connection(('127.0.0.1',4444));
[print(s.recv(4096).decode(),end='') for _ in iter(int,1)]"
# Or install ncat via chocolatey: choco install nmap
```

`remote-pdb` is the cleanest agent-friendly choice when `debugpy`'s DAP protocol is overkill. Use `debugpy` only when you actually need IDE integration.

### Debugging Hermes-specific Processes

#### Tests
See Recipe 3. Always add `-p no:xdist` or run single tests without xdist.

#### `run_agent.py` / CLI — one-shot
Easiest: add `breakpoint()` near the suspect line, then run `hermes` normally. Control returns to your terminal at the pause point.

#### `tui_gateway` subprocess (spawned by `hermes --tui`)
The gateway runs as a child of the Node TUI. Options:

**A. Source-edit the gateway:**

```python
# tui_gateway/server.py near the top of serve()
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```

Start `hermes --tui`. The TUI will appear frozen (its backend is waiting). Attach a client; execution resumes when you `continue`.

**B. Use `remote-pdb` at a specific handler:**

```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)   # in the RPC handler you want to trap
```

Trigger the matching slash command from the TUI, then `nc 127.0.0.1 4444` in another terminal.

#### `_SlashWorker` subprocess
Same pattern — `remote-pdb` with `set_trace()` inside the worker's `exec` path. The worker is persistent across slash commands, so the first trigger blocks until you connect; subsequent slash commands pass through normally unless you re-arm.

#### Gateway (`gateway/run.py`)
Long-lived. Use `remote-pdb` at a handler, or `debugpy` with `--wait-for-client` if you're restarting the gateway anyway.

## Examples

### "Why is this dict missing a key?"

```python
# add above the KeyError site
breakpoint()
# then in pdb:
(Pdb) pp d
(Pdb) pp list(d.keys())
(Pdb) w                # how did we get here
```

### "This test passes in isolation but fails in the suite."

```bash
python -m pytest tests/the_test.py --pdb -p no:xdist
# But if it only fails WITH other tests:
python -m pytest tests/ -x --pdb -p no:xdist
# Now it pdb-traps at the exact failing test after state accumulated.
```

### "My async handler deadlocks."

```python
# Add at handler entry
import remote_pdb; remote_pdb.set_trace(host="127.0.0.1", port=4444)
```

Trigger the handler. `nc 127.0.0.1 4444`, then `w` to see the suspended frame, `!import asyncio; asyncio.all_tasks()` to see what else is pending.

### "Post-mortem on a crash in an Ink child process / subprocess."

```bash
PYTHONFAULTHANDLER=1 python -m pdb -c continue path/to/entrypoint.py
# On crash, pdb lands at the frame of the exception with full locals
```

## Pitfalls

1. **pdb under pytest-xdist silently does nothing.** You won't see the prompt, the test just hangs. Always use `-p no:xdist` or `-n 0`.

2. **`breakpoint()` in CI / non-TTY contexts hangs the process.** Safe locally; never commit it. Add a pre-commit grep as a safety net.

3. **`PYTHONBREAKPOINT=0`** disables all `breakpoint()` calls. Check the env if your breakpoint isn't hitting:
   ```bash
   echo $PYTHONBREAKPOINT
   ```
   PowerShell:
   ```powershell
   $env:PYTHONBREAKPOINT
   ```

4. **`debugpy.listen` blocks only if you also call `wait_for_client()`.** Without it, execution continues and your first breakpoint may fire before the client is attached.

5. **Attach to PID fails on hardened kernels.** `ptrace_scope=1` (Ubuntu default) allows only same-user ptrace of child processes. Workaround: `echo 0 > /proc/sys/kernel/yama/ptrace_scope` (needs root) or launch under `debugpy` from the start.

6. **Threads.** `pdb` only debugs the current thread. For multithreaded code, use `debugpy` (thread-aware DAP) or set `threading.settrace()` per thread.

7. **asyncio.** `pdb` works in coroutines but `await` inside pdb requires Python 3.13+ or `await` from `interact` mode on older versions. For 3.11/3.12, use `asyncio.run_coroutine_threadsafe` tricks or `!stmt`-based awaits via `asyncio.ensure_future`.

8. **Hermetic test wrappers that strip credentials and set `HOME=<tmpdir>`.** If your bug depends on user config or real API keys, it won't reproduce under the wrapper. Debug with raw `pytest` first to repro, then re-confirm under the wrapper.

9. **Forking / multiprocessing.** pdb does not follow forks. Each child needs its own `breakpoint()` or `set_trace()`. For Hermes subagents, debug one process at a time.

10. **Windows `nc` not available.** Use `python -c` TCP client or install `nmap` (`choco install nmap`) for `ncat`. The `remote-pdb` server side works identically on Windows.

11. **Port 5678 already in use.** If a previous debugpy session didn't clean up, the port stays bound. Kill the stale process or use a different port (e.g., `5679`).

## Verification

1. **Confirm debugpy installed:**
   ```bash
   python -c "import debugpy; print(debugpy.__version__)"
   ```
   Expected: a version string like `1.8.0` or similar.

2. **Confirm remote debug port is listening (Linux/macOS):**
   ```bash
   ss -tlnp | grep 5678
   ```
   Windows PowerShell:
   ```powershell
   netstat -ano | findstr 5678
   ```

3. **Confirm first breakpoint actually hits.** If it doesn't, check:
   - `PYTHONBREAKPOINT` is not set to `0`
   - You're not running under xdist (add `-p no:xdist`)
   - Execution didn't finish before client attached (use `wait_for_client()`)

4. **Confirm stack trace is expected:**
   ```
   (Pdb) w
   ```
   Should show the call stack leading to your breakpoint line.

5. **Post-debug cleanup — no stray debugger calls in committed code:**
   ```bash
   rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
   ```
   PowerShell:
   ```powershell
   Get-ChildItem -Recurse -Filter *.py | Select-String -Pattern "breakpoint\(\)|set_trace\(|debugpy\.listen"
   ```
   Expected: no output (clean working tree).

## Related skills

- **systematic-debugging** — general debugging methodology and root-cause analysis workflow
- **node-inspect-debugger** — equivalent patterns for Node.js / TypeScript debugging
- **debugging-hermes-tui-commands** — Hermes-specific TUI and gateway debugging context
