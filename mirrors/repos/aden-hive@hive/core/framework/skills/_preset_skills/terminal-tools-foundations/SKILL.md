---
name: hive.terminal-tools-foundations
description: Required reading whenever any shell_* tool is available. Teaches the foreground/background dichotomy (terminal_exec auto-promotes past 30s, returns a job_id you poll with terminal_job_logs), the standard envelope shape (exit_code, stdout, stdout_truncated_bytes, output_handle, semantic_status, warning, auto_backgrounded, job_id), output handle pagination via terminal_output_get, when to read semantic_status instead of raw exit_code (grep/rg/find/diff/test exit 1 is NOT an error), the destructive-warning surface (rm -rf, git push --force, DROP TABLE), tool preference (the terminal handles ALL file read/write/edit/search; use gcu-tools / hive_tools where they fit), and the bash-only-on-macOS policy. Skipping this leads to "tool returned no output" surprises, orphaned jobs, and panic over benign grep exit codes.
metadata:
  author: hive
  type: preset-skill
  version: "1.0"
---

# terminal-tools — foundations

These tools give you a real terminal: foreground exec with smart envelopes, background jobs with offset-based log streaming, persistent PTY shells, and filesystem search. Bash-only on POSIX.

## Tool preference (read first)

The terminal is your file system: reading, writing, editing, and searching files all go through terminal-tools. Reach for a higher-level tool only where it clearly fits (browser, web search). Terminal tools default their cwd/path to your **session workdir** when you omit it — relative paths Just Work; pass an absolute path to operate elsewhere.

- **Reading files** → `terminal_exec("cat PATH")` (page large output with `terminal_output_get`)
- **Editing files** → `terminal_exec("sed -i ...")` / awk, or rewrite the whole file with a heredoc
- **Writing files** → heredoc: `terminal_exec("cat > PATH <<'EOF' ... EOF")`
- **Searching** → `terminal_rg` (content / regex grep) and `terminal_glob` (find files by name)
- **Browser / web pages** → `gcu-tools.browser_*` for rendered pages — NOT `terminal_exec("curl ...")`
- **Web search** → `hive_tools.web_search` — NOT scraping
- **System operations** (process exec, jobs, PTYs) → terminal-tools. This is its territory.

## The standard envelope

Every spawn-style call (`terminal_exec`, the auto-promoted job state) returns this shape:

```jsonc
{
  "exit_code": 0,                    // null when auto-backgrounded or pre-spawn error
  "stdout": "...",                   // decoded, truncated to max_output_kb (default 256 KB)
  "stderr": "...",
  "stdout_truncated_bytes": 0,       // > 0 means more is in output_handle
  "stderr_truncated_bytes": 0,
  "runtime_ms": 42,
  "pid": 12345,
  "output_handle": null,             // "out_<hex>" when truncated — paginate with terminal_output_get
  "timed_out": false,
  "semantic_status": "ok",           // "ok" | "signal" | "error" — read THIS, not just exit_code
  "semantic_message": null,          // e.g. "No matches found" for grep exit 1
  "warning": null,                   // e.g. "may force-remove files" for rm -rf
  "auto_backgrounded": false,
  "job_id": null,                    // set when auto_backgrounded=true
  "shell_kind": "bash"               // interpreter that ran it: "bash" | "powershell" | "cmd" | "direct"
}
```

## Auto-promotion (the core mental model)

`terminal_exec` runs commands in the foreground until the **auto-background budget** (default 30s) elapses. Past that point, the process is silently transferred to a background job and the call returns immediately with:

```jsonc
{ "auto_backgrounded": true, "exit_code": null, "job_id": "job_<hex>", ... }
```

When you see `auto_backgrounded: true`, **pivot to polling**. The job is still running:

```
terminal_job_logs(job_id, since_offset=0, wait_until_exit=true, wait_timeout_sec=60)
  → blocks server-side until the job exits or the timeout, returns logs + status
```

You're not failing — you're freed up to do other work while the long task runs.

To force pure-foreground (kill on `timeout_sec`), pass `auto_background_after_sec=0`. Use this when you genuinely don't want a background job (small commands where promotion would surprise you).

## Semantic exit codes — read `semantic_status`, not raw `exit_code`

Several common commands use exit 1 for legitimate non-error states:

| Command | exit 0 | exit 1 |
|---|---|---|
| `grep` / `rg` | matches found | **no matches** (not an error) |
| `find` | success | **some dirs unreadable** (informational) |
| `diff` | identical | **files differ** (informational) |
| `test` / `[` | true | **false** (informational) |

For these, `semantic_status` will be `"ok"` even when `exit_code == 1`, with `semantic_message` describing why ("No matches found"). For everything else, `semantic_status` defaults to `"ok"` on 0 and `"error"` on nonzero.

**Rule**: always check `semantic_status` first. Only fall back to `exit_code` when you need the exact number (e.g. distinguishing `make` errors).

## Destructive warnings — re-read your command

The envelope's `warning` field is set when the command matches a known destructive pattern (`rm -rf`, `git push --force`, `git reset --hard`, `DROP TABLE`, `kubectl delete`, `terraform destroy`, etc.). The command **still ran** — the warning is informational. Use it as a "did I mean to do that?" prompt before trusting subsequent steps that depend on the side effect.

If a `warning` appears unexpectedly, stop and verify: was the destructive action intended, or did a path/glob slip in?

## Output handles — never lose output

When `stdout_truncated_bytes > 0` or `stderr_truncated_bytes > 0`, the inline output was capped at `max_output_kb` (default 256 KB). The full bytes are stashed under `output_handle` for **5 minutes**. Paginate with:

```
terminal_output_get(output_handle, since_offset=0, max_kb=64)
  → { data, offset, next_offset, eof, expired }
```

Track `next_offset` across calls. If `expired: true`, re-run the command (the handle's TTL has lapsed).

The store has a 64 MB cap with LRU eviction. For huge outputs, prefer `terminal_job_start` + `terminal_job_logs` polling (4 MB ring buffer per stream, infinite total throughput).

## Bash, not zsh — even on macOS

On POSIX, `terminal_exec` and `terminal_pty_open` always invoke `/bin/bash` (on Windows see the section below). The user's `$SHELL` is ignored. Explicit `shell="/bin/zsh"` is **rejected** with a clear error. This is a deliberate security stance, not aesthetic — zsh has command/builtin classes (`zmodload`, `=cmd` expansion, `zpty`, `ztcp`, `zf_*`) that bypass bash-shaped checks. The `terminal-tools-pty-sessions` skill explains the implications for PTY sessions specifically.

`ZDOTDIR` and `ZSH_*` env vars are stripped before exec to prevent zsh dotfiles leaking in. Bash dotfiles still apply when invoked interactively (e.g. PTY sessions use `bash --norc --noprofile` to keep things predictable).

## Windows — check `shell_kind` before assuming bash

On Windows the shell is resolved in priority order: **Git Bash → PowerShell → cmd**. Which one ran your command is reported in the envelope's `shell_kind` field. Bash is only available if Git for Windows is installed; otherwise you land in PowerShell (or cmd as the floor). **Read `shell_kind` and adapt** — bash idioms silently break in the others:

| You wrote | `bash` | `powershell` | `cmd` |
|---|---|---|---|
| `cat` / `ls` | ✓ | ✓ (aliases) | ✗ (`type` / `dir`) |
| `grep` / `sed` / GNU `find` | ✓ | ✗ | ✗ |
| `a && b` | ✓ | ✗ in PS 5.1 (use `;`) | ✓ |
| `2>/dev/null` | ✓ | `2>$null` | `2>nul` |
| single-quoted `'args'` | ✓ | ✓ | ✗ (use `"..."`) |

Practical rule: if `shell_kind != "bash"`, prefer commands that are portable (a bare program name + args, e.g. `node x.js`, `python -m pip install ...`) or write the PowerShell/cmd-native form. Don't assume coreutils. PTY sessions (`terminal_pty_*`) are POSIX-only and return an "unsupported on Windows" error.

**Paths under `shell_kind: "bash"` on Windows (Git Bash):** backslashes are escape characters, so a Windows path passed verbatim gets mangled (`cat C:\Users\me\x` → bash reads `C:Usersmex`). Use forward slashes (`C:/Users/me/x`, which Git Bash accepts) or the MSYS form (`/c/Users/me/x`). Quoting a backslash path in single quotes also preserves it (`cat 'C:\Users\me\x'`).

## Pipelines and complex commands

Pipes (`|`), redirects (`>`, `<`, `>>`), conditionals (`&&`, `||`, `;`), and globs (`*`, `?`, `[`) are detected automatically. You can pass them with the default `shell=False` and the runtime will transparently route through `/bin/bash -c` and surface `auto_shell: true` in the envelope:

```
terminal_exec("ps aux | sort -k3 -rn | head -40")
  → { exit_code: 0, stdout: "...", auto_shell: true, ... }
```

For simple argv commands (no metacharacters) `shell=False` is faster and direct-execs the binary. For commands with shell features but no metacharacters that the detector catches (rare — exotic bash builtins, here-strings), pass `shell=True` explicitly:

```
terminal_exec("set -e; complicated bash logic", shell=True)
```

Quoted strings work either way — the detector uses `shlex.split` which handles `"quoted args with spaces"` correctly.

## When to use what (cheat sheet)

| Need | Tool |
|---|---|
| One-shot command, ≤30s | `terminal_exec` |
| One-shot command, might be longer | `terminal_exec` (auto-promotes) |
| Long-running job from the start | `terminal_job_start` |
| State across calls (cd, env, REPL) | `terminal_pty_open` + `terminal_pty_run` |
| Search file contents (any path) | `terminal_rg` |
| Find files by name/glob (any path) | `terminal_glob` |
| Retrieve truncated output | `terminal_output_get` |
| Tree / stat / du | `terminal_exec("ls -la"/"stat foo"/"du -sh path")` |
| HTTP / DNS / ping / archives | `terminal_exec("curl ..."/"dig ..."/"tar xzf ...")` |

See `references/exit_codes.md` for the full POSIX + signal-induced + semantic catalog.
