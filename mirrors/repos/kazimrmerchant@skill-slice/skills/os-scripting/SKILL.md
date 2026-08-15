---
name: os-scripting
version: 1.2.1
description: "Hardens production Bash on Linux and macOS: ShellCheck 0.9+, Bats 1.9+, `set -euo pipefail`, quoted expansions, and systemd timers instead of bare cron. Use when a script fails only in CI or a host needs CPU, disk, or unit triage. Never treat this as PowerShell-first Windows automation or as an application runtime in Python."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# OS/Shell Scripting Troubleshooting Workflow

## Overview

This skill is a working method for diagnosing system problems and writing shell automation that survives contact with production. Most shell incidents trace back to the same small set of causes: unquoted expansions, ignored exit codes, missing tools, and environment drift between a laptop and CI. Each phase below targets one of those causes directly.

The tooling baseline matters: when everyone runs the same linter and test-runner versions, "works on my machine" disappears as a class of bug. This skill pins **ShellCheck ≥ 0.9.0** (added security-focused lint rules), **Bats-core ≥ 1.9.0** (added `bats_require_minimum_version` and `run -N` status assertions), and wires both into **GitHub Actions** so the gate runs on every push. The security defaults — `set -euo pipefail`, read-only constants, and systemd sandboxing — convert silent corruption into a loud, early, recoverable failure.

**Host note:** The primary development host is Windows (PowerShell). When working on the Windows host, use PowerShell equivalents for environment probes and path references. All Bash/Linux commands below are for target systems (Linux, macOS, containers). On Windows, adapt paths to the working tree; do not assume a publisher library layout.

## When to Use

Reach for this workflow when the failure mode is "a shell script or a host is behaving unexpectedly and I need a repeatable way to find out why." Concretely:

- **Debugging shell script errors** — when a script fails intermittently or only in CI, the structured tracing in Phase 3 surfaces *where* and *with what state*.
- **Creating production-ready Bash scripts** — when a one-off snippet is about to become a scheduled job that others depend on, Phase 4 gives it validation and error handling so it fails safely.
- **Troubleshooting system issues** — high CPU, memory pressure, disk exhaustion, or a service that will not start (Phases 1 and 6).
- **Automating administrative tasks** — turning a manual runbook into an idempotent, scheduled, observable job (Phase 7).
- **Managing processes and services** — inspecting, tracing, and restarting units.
- **Configuring system resources** — and verifying the change actually took effect.
- **Meeting hardening requirements** (e.g., CIS Benchmarks): the conventions here map onto common controls (least privilege, no plaintext secrets, audited scheduling).

## Prerequisites

- **ShellCheck ≥ 0.9.0** — install via `sudo apt-get install -y shellcheck` (Debian/Ubuntu) or `brew install shellcheck` (macOS). Verify the floor before trusting results.
- **Bats-core ≥ 1.9.0** — required for `bats_require_minimum_version` and `run -N` status assertions.
- **GitHub Actions** — for CI gate integration (optional but recommended).
- **jq** — optional but recommended for JSON-safe logging; a pure-bash fallback is provided in all templates.
- On the Windows host: PowerShell 5.1+ or PowerShell 7+ for local environment probes.

## Procedure

### Anti-Patterns to Avoid

These are recurring root causes of real incidents, paired with safer alternatives:

1. **Deprecated arithmetic and unquoted `source`.** Avoid `let x=1+2` and `` x=`expr 1 + 2` `` for math; use `(( x = a + b ))` or `$(( a + b ))`. `$(())` is POSIX arithmetic that runs in-process (no `fork`/subshell) and is immune to word-splitting and globbing. Always quote sourced paths (`source "${conf}"`), because an unquoted path containing spaces silently sources the wrong file or nothing at all.

2. **`eval` on dynamic or user-influenced data.** `eval` executes whatever it is handed, so a value like `"; rm -rf ~"` becomes command injection. When you must build a command dynamically, use an array: `cmd=(rsync -a -- "${src}" "${dst}"); "${cmd[@]}"`. Reserve `eval` for trusted, static strings you fully control, and prefer not to use it at all.

3. **Hard-coded secrets.** Secrets in a script leak through `ps`, shell history, the process environment, backups, and version control — all places you cannot fully scrub later. Pull them at runtime from a secrets manager (HashiCorp Vault, AWS Secrets Manager, SOPS) or injected environment variables. Prefer `--password-stdin`/credential files over passing secrets as arguments.

4. **Unvalidated input to privileged commands.** Anything that runs as root and trusts caller-supplied data is one crafted value away from full compromise. Validate against an explicit allowlist (regex or a fixed set), reject anything unexpected, and quote every expansion.

5. **`netstat` on modern hosts.** Deprecated, frequently absent on current distros, and slower than `ss`. Prefer `ss`; keep a `netstat` fallback only for legacy machines where `ss` is unavailable.

6. **`cron` without an explicit environment.** Cron runs with a minimal `PATH` and no mail routing, so jobs that work in your shell fail silently under cron. Prefer **systemd timers** (journald logging, sandboxing, missed-run catch-up); if cron is mandatory, set `PATH` and `MAILTO` explicitly at the top of the crontab.

7. **Unpinned tool versions in CI.** Floating ShellCheck/Bats versions cause local-vs-CI drift and miss newer security lints. Pin **ShellCheck ≥ 0.9.0** and **Bats-core ≥ 1.9.0** and verify the floor at runtime.

### Scripting Conventions

Bash has no static type system, but it does have *declared intent*. Using it consistently makes scripts predictable:

- `declare -r MAX_RETRIES=5` / `local -r name="$1"` for constants and inputs — marks a value read-only so accidental re-assignment is rejected by the shell.
- `declare -i count=0` / `local -i count=0` for counters — forces arithmetic-evaluation context on assignment. Does **not** reject non-numeric input (`declare -i x=abc` yields `0`), so always pair with a regex guard (`[[ "$v" =~ ^[0-9]+$ ]]`) at the boundary.
- `declare -a list=()` / `declare -A map=()` for collections — arrays iterate safely with `"${list[@]}"` and avoid word-splitting and globbing hazards of space-delimited strings.
- Quote every expansion and set `IFS=$'\n\t'` in scripts — the default `IFS` splits on spaces, so an unquoted `$path` containing a space becomes two arguments.
- Validate at the boundary (argument parsing, config load), then let the core logic assume well-formed data — one validation layer is easier to audit than defensive checks scattered through every function.
- `set -euo pipefail` plus an `ERR` trap — together they turn an ignored exit code or an unset variable into an immediate, located failure rather than silent data loss.

### Phase 1: Environment Assessment

Start here because almost every later step depends on facts you do not yet know: which OS and version, which tools exist, what privileges you hold, and where the pressure is. Probing first (rather than assuming) is what makes the rest of the workflow portable across Linux, macOS, and stripped-down containers.

**Skills to invoke:** `bash-linux`, `bash-pro`, `bash-defensive-patterns`

**Actions:**
1. Identify the operating system and version (so you pick the right tool flags).
2. Check which tools and commands are actually available (containers ship little).
3. Verify your permissions and access (root vs. user changes what you can see).
4. Assess system resources (CPU, memory, disk, I/O) to localize the pressure.
5. Review logs and error messages for the first concrete symptom.

**Diagnostic commands:**

```bash
#!/usr/bin/env bash
# Phase 1 — read-only environment probes. These never mutate state, so they are
# safe to run first on an unfamiliar host.
#
# Note: -e is intentionally omitted here. During assessment, a missing *optional*
# tool should skip that probe, not abort the whole survey.
set -uo pipefail

# have <command> — true when an executable is on PATH.
have() { command -v "$1" >/dev/null 2>&1; }

# --- Operating system and kernel identity ---
uname -a                                           # kernel, arch, host (portable)
[[ -r /etc/os-release ]] && cat /etc/os-release    # Linux distro metadata
have hostnamectl && hostnamectl                    # systemd hosts only
have sw_vers     && sw_vers                         # macOS product/build version
have lsb_release && lsb_release -a 2>/dev/null      # Debian/Ubuntu family

# --- Resource usage (flags differ by platform, so branch explicitly) ---
if have top; then
    case "$(uname -s)" in
        Linux)  top -b -n1 | head -n 20 ;;          # GNU batch mode
        Darwin) top -l 1   | head -n 20 ;;          # BSD/macOS one-shot
    esac
fi
if have df; then df -hT 2>/dev/null || df -h; fi    # -T (fs type) is GNU-only
have free    && free -m                             # Linux memory summary
have vm_stat && vm_stat                             # macOS memory summary

# --- Process information ---
ps aux | sort -rk3 | head -n 20                     # top CPU consumers (portable)
have pgrep && pgrep -fl sshd                        # example: locate the ssh daemon
have lsof  && lsof -iTCP -sTCP:LISTEN -P -n         # listening TCP sockets

# --- Network status (prefer ss; fall back to legacy tools only if needed) ---
if have ss; then
    ss -tulnp
elif have netstat; then
    netstat -tulnp                                  # legacy fallback
fi
if have ip; then ip -br addr; else ifconfig -a; fi  # ip(8) on Linux, ifconfig on BSD
```

**Copy-paste prompt:**
```
Use @bash-linux to diagnose system performance issues
```

### Phase 2: Script Analysis

A script can be syntactically valid and still be dangerous: the shell parser does not warn about unquoted expansions, accidental word-splitting, or ignored failures. ShellCheck encodes that hard-won knowledge as lint rules, which is why it runs before you trust any script.

**Skills to invoke:** `bash-defensive-patterns`, `shellcheck-configuration`, `bats-testing-patterns`

**Actions:**
1. Run ShellCheck (use `--format gcc` so CI log parsers can read the output).
2. Read the script's structure: are responsibilities split into named functions?
3. Identify likely failure points (subshells, pipelines, external commands).
4. Check that exit codes are handled rather than ignored.
5. Verify variable usage and quoting — the single most common bug source.

**ShellCheck usage:**

```bash
#!/usr/bin/env bash
set -euo pipefail

# --- Install a known-good version ---
# Debian/Ubuntu:
sudo apt-get update && sudo apt-get install -y shellcheck
# macOS (Homebrew):
brew install shellcheck

# --- Verify the version meets the floor BEFORE trusting any results ---
required="0.9.0"
installed="$(shellcheck --version | awk '/^version:/ {print $2}')"
if [[ "$(printf '%s\n%s\n' "$required" "$installed" | sort -V | head -n1)" != "$required" ]]; then
    printf 'ShellCheck %s is older than the required %s\n' "$installed" "$required" >&2
    exit 1
fi

# --- Run it ---
shellcheck -x script.sh                 # -x: follow `source`d files
shellcheck -f gcc -e SC2034 script.sh   # gcc format parses cleanly in CI logs

# --- Apply ShellCheck's own fixes, but verify the patch first ---
# Why -p1 (not -p0): `shellcheck -f diff` emits a git-style diff with a/ b/
# prefixes, so one leading path component must be stripped.
if shellcheck -f diff script.sh > /tmp/shellcheck.patch && [[ -s /tmp/shellcheck.patch ]]; then
    if patch -p1 --dry-run < /tmp/shellcheck.patch; then
        patch -p1 < /tmp/shellcheck.patch
    else
        printf 'ShellCheck patch did not apply cleanly; review /tmp/shellcheck.patch by hand\n' >&2
    fi
fi
```

**CI integration (GitHub Actions):**

```yaml
# .github/workflows/shellcheck.yml
name: shellcheck
on:
  push:
    paths: ['**.sh', '**.bash']
  pull_request:
    paths: ['**.sh', '**.bash']
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run ShellCheck
        uses: ludeeus/action-shellcheck@master
        env:
          SHELLCHECK_OPTS: -x -e SC2034
        with:
          severity: warning
```

**Copy-paste prompt:**
```
Use @shellcheck-configuration to lint and fix shell scripts
```

### Phase 3: Debugging

When a script misbehaves, the question is always "where, and with what state?" Default Bash answers neither — it keeps going after errors and prints bare `+` lines under `set -x`. This phase fixes both: strict mode makes failures stop at the source, a rich `PS4` turns the trace into a readable log, and an `ERR` trap prints the call stack that led to the failure.

**Skills to invoke:** `systematic-debugging`, `debugger`, `error-detective`

**Actions:**
1. Enable strict mode (`set -euo pipefail`) so the first failure is the last.
2. Add structured (JSON) logging so logs are both greppable and machine-parseable.
3. Enrich the execution trace via `PS4` (timestamp, file, line, function).
4. Isolate the failing region behind a function and an `ERR` trap.
5. Test components individually until the faulty one is obvious.

**Debug techniques:**

```bash
#!/usr/bin/env bash
set -euo pipefail
#  -e            exit on any unhandled non-zero command
#  -u            treat an unset variable as an error (catches typos)
#  -o pipefail   a pipeline fails if ANY stage fails, not just the final one

export PS4='+ $(date "+%Y-%m-%dT%H:%M:%S%z") ${BASH_SOURCE[0]##*/}:${LINENO}:${FUNCNAME[0]:-main}() '

json_escape() {
    local -r raw="${1-}"
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$raw" | jq -Rs .
        return 0
    fi
    local out="$raw"
    out="${out//\\/\\\\}"
    out="${out//\"/\\\"}"
    out="${out//$'\n'/\\n}"
    out="${out//$'\r'/\\r}"
    out="${out//$'\t'/\\t}"
    printf '"%s"' "$out"
}

log() {
    if (( $# < 2 )); then
        printf 'log: usage: log <level> <message...>\n' >&2
        return 2
    fi
    local -r level="$1"; shift
    local -r message="$*"
    printf '{"timestamp":%s,"level":%s,"message":%s}\n' \
        "$(json_escape "$(date -u +"%Y-%m-%dT%H:%M:%SZ")")" \
        "$(json_escape "$level")" \
        "$(json_escape "$message")" >&2
}

on_error() {
    local -ri exit_code=$?
    local -ri failed_line=$1
    log ERROR "command failed (exit ${exit_code}) at line ${failed_line}: ${BASH_COMMAND}"
    local -i frame=0
    while caller "$frame" >/dev/null 2>&1; do
        log ERROR "  called from: $(caller "$frame")"
        (( frame += 1 ))
    done
    exit "$exit_code"
}
trap 'on_error "$LINENO"' ERR

# Static and dynamic checks:
bash -n script.sh    # parse only — catches syntax errors with zero side effects
bash -x script.sh    # full execution trace, formatted by the PS4 above
```

**Copy-paste prompt:**
```
Use @systematic-debugging to trace and fix shell script errors
```

### Phase 4: Script Development

The moment a snippet becomes something other people or a scheduler depend on, it needs three things: validated inputs (so bad data fails fast and clearly), error handling (so a partial run cleans up after itself), and explicit typing (so intent is visible and accidental mutation is rejected).

**Skills to invoke:** `bash-pro`, `bash-defensive-patterns`, `linux-shell-scripting`

**Actions:**
1. Design the script as small, named functions with one job each.
2. Implement error handling and cleanup with traps (EXIT/INT/TERM).
3. Validate inputs at the boundary using `getopts`-style parsing plus regex guards.
4. Document usage, version, and license so operators can self-serve.
5. Emit structured logs (and a machine-readable result on stdout).

**Script template (backup.sh):**

```bash
#!/usr/bin/env bash
#
# backup.sh — create a compressed, timestamped backup of a directory and prune
#             archives older than a retention window.
#
# SPDX-License-Identifier: MIT
# Author:  Platform Engineering <platform@example.com>
# Version: 1.0.0

set -euo pipefail
IFS=$'\n\t'   # split only on newline/tab, never on spaces

# --- Immutable constants -----------------------------------------------------
declare -r  SCRIPT_NAME="${BASH_SOURCE[0]##*/}"
declare -r  SCRIPT_VERSION="1.0.0"
declare -r  DEFAULT_LOG="/var/log/${SCRIPT_NAME%.sh}.log"
declare -ra REQUIRED_CMDS=(tar gzip find date mktemp basename dirname)

# --- Mutable, explicitly-typed configuration (populated by parse_args) -------
declare    LOG_FILE="${DEFAULT_LOG}"
declare    SOURCE_DIR=""
declare    TARGET_DIR=""
declare -i RETENTION_DAYS=7
declare    VERBOSE="false"
declare    WORKDIR=""        # temp dir; removed by the EXIT trap

# --- JSON-safe structured logging --------------------------------------------
json_escape() {
    local -r raw="${1-}"
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$raw" | jq -Rs .
        return 0
    fi
    local out="$raw"
    out="${out//\\/\\\\}"; out="${out//\"/\\\"}"
    out="${out//$'\n'/\\n}"; out="${out//$'\r'/\\r}"; out="${out//$'\t'/\\t}"
    printf '"%s"' "$out"
}

log() {
    if (( $# < 2 )); then
        printf 'log: usage: log <level> <message...>\n' >&2
        return 2
    fi
    local -r level="$1"; shift
    local -r message="$*"
    local -r line="$(printf '{"timestamp":%s,"level":%s,"message":%s}' \
        "$(json_escape "$(date -u +"%Y-%m-%dT%H:%M:%SZ")")" \
        "$(json_escape "$level")" \
        "$(json_escape "$message")")"
    printf '%s\n' "$line" >&2
}

# --- Cleanup trap ------------------------------------------------------------
cleanup() {
    if [[ -n "${WORKDIR:-}" && -d "${WORKDIR:-}" ]]; then
        rm -rf -- "${WORKDIR}"
    fi
}
trap cleanup EXIT INT TERM

# --- Argument parsing with validation at the boundary -----------------------
usage() {
    cat <<EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Options:
  -s, --source DIR      Directory to back up (required)
  -t, --target DIR      Backup destination (required)
  -r, --retention DAYS   Retention period in days (default: 7)
  -l, --log FILE         Log file path (default: ${DEFAULT_LOG})
  -v, --verbose          Enable verbose output
  -h, --help             Show this help message
  -V, --version          Show version
EOF
}

parse_args() {
    while (( $# > 0 )); do
        case "$1" in
            -s|--source)    SOURCE_DIR="$2"; shift 2 ;;
            -t|--target)    TARGET_DIR="$2"; shift 2 ;;
            -r|--retention)
                RETENTION_DAYS="$2"
                if ! [[ "$RETENTION_DAYS" =~ ^[0-9]+$ ]]; then
                    log ERROR "retention must be a positive integer, got: ${RETENTION_DAYS}"
                    exit 2
                fi
                shift 2
                ;;
            -l|--log)      LOG_FILE="$2"; shift 2 ;;
            -v|--verbose)   VERBOSE="true"; shift ;;
            -h|--help)      usage; exit 0 ;;
            -V|--version)   printf '%s %s\n' "$SCRIPT_NAME" "$SCRIPT_VERSION"; exit 0 ;;
            *)
                log ERROR "unknown argument: $1"
                usage >&2
                exit 2
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$SOURCE_DIR" ]]; then
        log ERROR "--source is required"
        usage >&2
        exit 2
    fi
    if [[ -z "$TARGET_DIR" ]]; then
        log ERROR "--target is required"
        usage >&2
        exit 2
    fi
    if [[ ! -d "$SOURCE_DIR" ]]; then
        log ERROR "source directory does not exist: ${SOURCE_DIR}"
        exit 2
    fi
}

# --- Verify required commands exist ------------------------------------------
check_dependencies() {
    local missing=()
    for cmd in "${REQUIRED_CMDS[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done
    if (( ${#missing[@]} > 0 )); then
        log ERROR "missing required commands: ${missing[*]}"
        exit 3
    fi
}

# --- Main backup logic -------------------------------------------------------
do_backup() {
    WORKDIR="$(mktemp -d)"
    local -r timestamp="$(date +%Y%m%dT%H%M%SZ)"
    local -r archive_name="${SCRIPT_NAME%.sh}_${timestamp}.tar.gz"
    local -r archive_path="${TARGET_DIR}/${archive_name}"

    log INFO "starting backup: source=${SOURCE_DIR} target=${TARGET_DIR} retention=${RETENTION_DAYS}d"

    mkdir -p -- "$TARGET_DIR"
    tar -czf -- "$archive_path" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"
    log INFO "archive created: ${archive_path}"

    # Prune old archives
    find "$TARGET_DIR" -name "${SCRIPT_NAME%.sh}_*.tar.gz" -mtime +"$RETENTION_DAYS" -delete
    log INFO "pruned archives older than ${RETENTION_DAYS} days"
}

# --- Entry point -------------------------------------------------------------
main() {
    parse_args "$@"
    check_dependencies
    do_backup
    log INFO "backup completed successfully"
}

main "$@"
```

**Copy-paste prompt:**
```
Use @bash-pro to create a production-ready shell script with error handling
```

### Phase 5: Testing

**Skills to invoke:** `bats-testing-patterns`, `test-automation`

**Actions:**
1. Write Bats-core tests (≥ 1.9.0) covering success paths, error paths, and side effects.
2. Use `bats_require_minimum_version` to enforce the floor at runtime.
3. Use `run -N` status assertions for negative tests.
4. Mock external commands in `setup`/`teardown` to isolate the unit under test.
5. Wire tests into CI alongside ShellCheck.

**Bats example:**

```bash
#!/usr/bin/env bats

bats_require_minimum_version 1.9.0

setup() {
    export TEST_DIR="$(mktemp -d)"
    export SOURCE_DIR="${TEST_DIR}/source"
    export TARGET_DIR="${TEST_DIR}/target"
    mkdir -p "$SOURCE_DIR" "$TARGET_DIR"
    echo "test data" > "${SOURCE_DIR}/file.txt"
}

teardown() {
    rm -rf -- "$TEST_DIR"
}

@test "backup creates a compressed archive" {
    run /usr/local/bin/backup.sh --source "$SOURCE_DIR" --target "$TARGET_DIR" --retention 1
    [ "$status" -eq 0 ]
    [ "$(find "$TARGET_DIR" -name '*.tar.gz' | wc -l)" -eq 1 ]
}

@test "backup fails when source does not exist" {
    run /usr/local/bin/backup.sh --source "/nonexistent" --target "$TARGET_DIR"
    [ "$status" -eq 2 ]
}

@test "backup prunes old archives" {
    # Create an old archive (backdated)
    old_archive="${TARGET_DIR}/backup_20200101T000000Z.tar.gz"
    tar -czf "$old_archive" -C "$SOURCE_DIR" .
    touch -d "2020-01-01" "$old_archive"

    run /usr/local/bin/backup.sh --source "$SOURCE_DIR" --target "$TARGET_DIR" --retention 1
    [ "$status" -eq 0 ]
    # The old archive should be pruned; only the new one remains
    [ "$(find "$TARGET_DIR" -name '*.tar.gz' | wc -l)" -eq 1 ]
}
```

### Phase 6: System Troubleshooting

**Skills to invoke:** `devops-troubleshooter`, `incident-responder`

**Actions:**
1. Check service status and recent logs.
2. Inspect resource utilization (CPU, memory, disk, I/O).
3. Trace network connectivity layer by layer (L3 → L7).
4. Inspect specific service processes (strace, lsof).
5. Check disk and I/O health (iostat, smartctl).

**Diagnostic commands:**

```bash
# --- Service logs (journald) ---
journalctl -u service-name.service -n 100 --no-pager
journalctl -u service-name.service --since "1 hour ago" --no-pager
journalctl -u service-name.service -o json -c 'select((.PRIORITY // "7" | tonumber) <= 3)'

# --- Connectivity, layered from L3 (reachability) up to L7 (application) ---
ping -c 4 example.com                                   # L3: is the host routable?
have traceroute && traceroute -n example.com            # where does the path break?
curl -fsS --max-time 10 -o /dev/null -w 'http_status=%{http_code}\n' \
     https://example.com                                 # L7: does the app answer?
have http && http --check-status --timeout=10 https://example.com   # HTTPie alt

# --- Inspect a service by name, deriving its PID at runtime ---
svc="nginx"
pid="$(pgrep -f "${svc}" | head -n1 || true)"
if [[ -n "${pid}" ]]; then
    have strace && strace -f -p "${pid}" -o "/tmp/${svc}.strace" &   # syscall trace
    have lsof   && lsof -p "${pid}"                                  # open fds/sockets
else
    printf 'WARN: no running process matched %q\n' "${svc}" >&2
fi

# --- Disk and I/O health ---
have iostat   && iostat -xz 1 3                 # per-device utilisation and await
have smartctl && sudo smartctl -H /dev/sda      # SMART overall-health assessment
```

**Copy-paste prompts:**
```
Use @devops-troubleshooter to diagnose server connectivity issues
```
```
Use @incident-responder to investigate system outage
```

### Phase 7: Automation

Automating a task is where reliability stops being optional: a job that runs unattended at 2 a.m. has no human to notice it failed. Goals: idempotency (re-running is safe), observability (failures are logged and alert), and least privilege (a compromised job has a small blast radius). systemd timers are preferred over cron because they deliver the first two for free.

**Skills to invoke:** `workflow-automation`, `cicd-automation-workflow-automate`, `linux-shell-scripting`

**Actions:**
1. Identify repeatable tasks worth automating (and the cost of them failing).
2. Make the script idempotent and strict (`set -euo pipefail`, see Phase 4).
3. Schedule with systemd timers (preferred) or cron with an explicit environment.
4. Add health checks and alerting (e.g., Prometheus node exporter + Grafana alerts).
5. Monitor the automation itself and rotate its logs.

**Systemd timer example (preferred over cron):**

The sandboxing directives below shrink what a compromised job can touch, which is the whole reason to prefer this over cron.

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Daily backup service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh --source /var/www --target /mnt/backups --retention 30
StandardOutput=journal
StandardError=journal
ProtectSystem=full              # /usr, /boot, /etc mounted read-only
ProtectHome=true                # /home, /root hidden from the job
PrivateTmp=true                 # private /tmp, cleaned up on exit
NoNewPrivileges=true            # cannot gain privileges via setuid binaries

# /etc/systemd/system/backup.timer
[Unit]
Description=Run backup.service daily

[Timer]
OnCalendar=daily
Persistent=true                 # catch up on runs missed during downtime
RandomizedDelaySec=15m          # spread fleet-wide load to avoid a thundering herd

[Install]
WantedBy=timers.target
```

Validate the units *before* activating them:

```bash
sudo systemd-analyze verify /etc/systemd/system/backup.service
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
systemctl list-timers backup.timer --all     # confirm the next scheduled run
```

**Cron example (only if systemd is unavailable):**

Cron runs with a minimal environment, so jobs that work in your shell can fail under cron with no notice. Setting `PATH` and `MAILTO` explicitly makes cron jobs debuggable.

```bash
# Edit the crontab:
crontab -e

# --- Put these at the top so every job inherits a sane environment ---
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=admin@example.com

# Daily backup at 02:00; redirect both streams so output is captured.
0 2 * * * /usr/local/bin/backup.sh --source /var/www --target /mnt/backups --retention 30 >> /var/log/backup.log 2>&1

# Weekly cleanup, Sundays at 03:00.
0 3 * * 0 /usr/local/bin/cleanup.sh >> /var/log/cleanup.log 2>&1
```

**Copy-paste prompt:**
```
Use @workflow-automation to create automated system maintenance workflow
```

## Common Troubleshooting Scenarios

Each block is a fast, read-only first pass. The comments explain what the numbers mean so you can interpret them.

### High CPU Usage
```bash
top -b -n1 | head -n 20                                   # snapshot of the busiest tasks
ps -eo pid,ppid,comm,%mem,%cpu --sort=-%cpu | head -n 10  # top CPU consumers by command
command -v pidstat >/dev/null 2>&1 && pidstat 1 5         # per-process CPU over 5 samples
```

### Memory Issues
```bash
free -h                                                   # used/free/available at a glance
command -v vmstat >/dev/null 2>&1 && vmstat 1 10          # watch si/so: nonzero = swapping
grep -E 'MemTotal|MemAvailable|Swap' /proc/meminfo        # MemAvailable is the real headroom
```

### Disk Space
```bash
df -hT 2>/dev/null || df -h                               # per-filesystem usage (and type)
du -sh ./* 2>/dev/null | sort -h                          # biggest entries in the CWD
# Largest files on the system, ignoring permission-denied noise:
find / -xdev -type f -size +500M -printf '%s\t%p\n' 2>/dev/null | sort -rn | head -n 20
```

### Network Issues
```bash
command -v ip >/dev/null 2>&1 && ip -br addr              # interface state, one line each
command -v ip >/dev/null 2>&1 && ip route show            # default route present?
command -v ss >/dev/null 2>&1 && ss -tulnp                # who is listening on what
curl -fsS --max-time 10 -o /dev/null -w 'status=%{http_code}\n' https://example.com
```

### Service Failures
```bash
systemctl status service-name.service                    # current state + recent log tail
journalctl -u service-name.service -n 100 --no-pager      # last 100 lines, scriptable
sudo systemctl restart service-name.service               # attempt recovery
sudo systemctl reset-failed service-name.service          # clear the failed state after a fix
```

## Pitfalls

- **ShellCheck version drift:** A stale ShellCheck silently skips newer security checks, giving false confidence. Always verify `installed >= 0.9.0` before trusting results. Pin the version in CI.
- **`set -e` in assessment scripts:** During Phase 1 environment assessment, omit `-e`. A missing optional tool should skip that probe, not abort the whole survey. Use `set -uo pipefail` only.
- **`patch -p0` vs `patch -p1`:** `shellcheck -f diff` emits a git-style diff with `a/` `b/` prefixes, so you must use `patch -p1` (not `-p0`). Always run `--dry-run` first to avoid applying a half-matching patch.
- **`declare -i` does not validate input:** `declare -i x=abc` yields `0`, not an error. Always pair integer declarations with a regex guard (`[[ "$v" =~ ^[0-9]+$ ]]`) at the boundary.
- **Logging failures masking real errors:** Never let an unwritable log path abort the script — a logging failure must not mask the real error. Guard log file writes with `|| true` or check writability first.
- **Cron's minimal environment:** Cron runs with a minimal `PATH` and no mail routing. Jobs that work in your shell fail silently under cron. Always set `PATH` and `MAILTO` explicitly at the top of the crontab.
- **Unquoted expansions with spaces:** The default `IFS` splits on spaces, so an unquoted `$path` containing a space becomes two arguments. Set `IFS=$'\n\t'` and quote every expansion.
- **`eval` injection:** `eval` executes whatever it is handed. A value like `"; rm -rf ~"` becomes command injection. Use arrays for dynamic commands instead.
- **Secrets in scripts:** Secrets leak through `ps`, shell history, process environment, backups, and version control. Pull them at runtime from a secrets manager or injected environment variables. Never hard-code secrets.
- **Floating tool versions in CI:** Floating ShellCheck/Bats versions cause local-vs-CI drift. Pin versions and verify the floor at runtime.

## Verification

Before declaring the workflow complete, confirm each item:

- [ ] All scripts pass `shellcheck -x` with the pinned version (≥ 0.9.0), in CI.
- [ ] Bats-core tests (≥ 1.9.0) pass, including error-path and side-effect cases.
- [ ] Strict mode (`set -euo pipefail`) and an `ERR`/EXIT trap are present.
- [ ] Inputs are validated at the boundary with explicit types and regex guards.
- [ ] No secrets are hard-coded; they are injected at runtime.
- [ ] Structured (JSON) logging is configured and log rotation is set up.
- [ ] Documentation includes usage (`--help`), `--version`, and a license header.
- [ ] Scheduling uses systemd timers, or cron with explicit `PATH`/`MAILTO`.

**Checkable commands:**

```bash
# Verify ShellCheck version meets floor
shellcheck --version | awk '/^version:/ {print $2}'
# Expected: 0.9.0 or higher

# Verify strict mode is present in script
grep -q 'set -euo pipefail' script.sh && echo "PASS: strict mode" || echo "FAIL: no strict mode"

# Verify ERR trap is present
grep -q 'trap.*ERR' script.sh && echo "PASS: ERR trap" || echo "FAIL: no ERR trap"

# Verify no hard-coded secrets (heuristic check for common patterns)
grep -qE '(password|secret|api_key|token)\s*=\s*["\x27][^$\{]' script.sh && echo "WARN: possible hard-coded secret" || echo "PASS: no obvious secrets"

# Verify systemd timer is scheduled
systemctl list-timers backup.timer --all --no-pager

# Verify Bats tests pass
bats tests/backup.bats
# Expected: all tests pass with exit code 0
```

## Related Skills

- `development` — Software development
- `cloud-devops` — Cloud and DevOps
- `security-audit` — Security testing
- `database` — Database operations
