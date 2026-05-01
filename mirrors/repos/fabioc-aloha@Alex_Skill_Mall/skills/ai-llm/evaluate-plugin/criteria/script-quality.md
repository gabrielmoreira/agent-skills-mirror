---
id: script_quality
name: Script Quality
requires: scripts
---

<!-- The `requires: scripts` front matter signals that this dimension should be
     scored N/A when the plugin contains no script files (.ps1, .sh, .py, .js).
     In interactive evaluation (SKILL.md), the evaluator checks for scripts in
     Phase 2 and skips this dimension if none are found. In CI evaluation
     (llm-judge-plugin.py), the script auto-detects script files and excludes
     this dimension from the prompt when none exist. -->

# Script Quality

Evaluates whether the plugin's implementation scripts are well-structured,
safe, and maintainable.

> **Why it matters:** Scripts are the runtime backbone of many plugins — they execute
> as hooks, commands, or tools. Poorly written scripts introduce bugs, security
> vulnerabilities, and cross-platform failures that no amount of good SKILL.md
> instructions can compensate for.

> **Scope:** "Scripts" means standalone executable files (.ps1, .sh, .py, .js) in the
> plugin directory. Inline shell in CI configs or markdown is not scored here.

## What to look for

- **Strict mode & error handling** — Does the script use `set -euo pipefail` (Bash), `$ErrorActionPreference = 'Stop'` + `Set-StrictMode` (PowerShell), or equivalent? If a strict-mode feature is deliberately omitted with documented rationale, treat that as a valid design choice. Does it handle missing inputs, tool failures, and unexpected errors?
- **Input validation** — Does the script validate arguments, environment variables, and file paths before using them? Does it provide usage/help output for incorrect invocations?
- **Security** — Does the script avoid hardcoded secrets, command injection (`Invoke-Expression`, `eval`, `os.system`), arbitrary code execution, or unsafe file operations? Are file paths sanitized?
- **Exit codes** — Does the script return meaningful exit codes (e.g., 0 = success, 1 = validation failure, 2 = unexpected error)? Does it distinguish expected vs. unexpected failures?
- **Documentation** — Does the script have a header comment explaining purpose, parameters, and usage? Are complex sections commented?
- **Cross-platform** — If the plugin targets multiple OSes, does the script handle platform differences? If single-platform, is the target platform documented?
- **Test coverage** — Does the plugin include tests for its scripts? Do tests cover happy path, invalid input, and missing dependency scenarios? Tests must include assertions, not just invocations.
- **Modularity** — Are scripts focused on a single responsibility? Is shared logic extracted into reusable functions?
- **Dependency checks** — Does the script verify required external tools (e.g., `gh`, `jq`, `curl`) are available before proceeding?
- **Cleanup** — Does the script clean up temporary files/resources on exit (e.g., `trap EXIT` in Bash, `try/finally` in PowerShell/Python)?
- **Output hygiene** — Are logs/diagnostics sent to stderr and data/results to stdout? Is output machine-readable (JSON) where appropriate?
- **Idempotency** — Can the script be safely re-run without side effects? Does it check for existing state before creating or modifying resources?
- **Shebang & portability** — Do Bash/Python scripts include correct shebang lines (`#!/usr/bin/env bash` preferred over `#!/bin/bash`)?

## Scoring rubric

| Score | Criteria |
|-------|----------|
| **5** | Strict mode enabled. Structured error handling, input validation, dependency checks, cleanup. Header documentation. Tests cover success, invalid input, and failure scenarios. Zero security anti-patterns. Cross-platform handled or target platform documented. |
| **4** | Handles common errors and validates required inputs. Checks key dependencies. At least inline comments on non-obvious logic. Basic tests included. No security anti-patterns (no injection, no hardcoded secrets). |
| **3** | Works on the happy path. Handles at least one error case (e.g., file-not-found). May lack automated tests but logic is sound. Documentation is sparse. |
| **2** | No error handling — continues on error or fails silently. No dependency checks. Happy-path-only code that leaves messy state on failure. |
| **1** | Contains security vulnerabilities (command injection, hardcoded secrets, arbitrary code execution), is syntactically broken, or does not run. |
| **N/A** | Plugin has no script files. Score this dimension N/A and exclude from the average. Trivial scripts (e.g., `echo "done"`) should still be scored. |

> **Scoring asymmetry note:** When Script Quality is N/A, the plugin is scored
> on fewer dimensions than a scripted plugin. This means a mediocre script (3/5)
> drags a plugin's average *down*, while an excellent script (5/5) provides a
> *boost* that script-free plugins cannot earn. This is intentional — scripts are
> runtime code that directly affects reliability, so their quality should influence
> the overall score. However, evaluators should be aware of this asymmetry and
> avoid penalizing plugins that make a deliberate architectural choice to avoid
> scripts (e.g., pure-prompt plugins).

## What a 5 looks like

- `set -euo pipefail` or `$ErrorActionPreference = 'Stop'` + `Set-StrictMode -Version Latest`
- Dependencies verified: `command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }`
- Parameters validated with clear error messages: `if (-not $Path) { Write-Error "Path is required"; exit 1 }`
- Header comment: `# Purpose: Validates markdown links in plugin documentation`
- Cleanup on exit: `trap 'rm -f "$tmpfile"' EXIT`
- Tests with assertions covering success, invalid input, and missing dependency
- No secrets, no `Invoke-Expression` on user input, no unsanitized file paths
- Meaningful exit codes: 0 for success, 1 for validation failure, 2 for unexpected error

## Multi-script plugins

If a plugin contains multiple scripts, score based on overall quality. A single
critically flawed script (security vulnerability, no error handling) caps the
dimension score at the level matching that script's quality.

## Scoring examples

### Score 5 — validate-md-links (PowerShell)

```powershell
# validate-md-links.ps1
# Validates markdown links, anchors, and file references
# Parameters: -Include (directories to scan), -Root (plugin root)

param(
    [string[]]$Include = @('.'),
    [string]$Root = '.'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Test-Path $Root)) {
    Write-Error "Root path '$Root' does not exist"
    exit 1
}
```

Why it scores 5: Strict mode enabled, `param()` block is first (correct PowerShell),
validates parameters with clear error messages, uses meaningful exit codes, has header
documentation, and the plugin includes a Pester test suite with multiple scenarios
covering valid links, broken links, and missing files.

### Score 3 — deploy-hook (Bash)

```bash
#!/bin/bash
if [ -f "$1" ]; then
    source "$1"
    echo "Deployed successfully"
else
    echo "File not found"
fi
```

Why it scores 3: Has a shebang and checks that the input file exists (one error case),
but uses `#!/bin/bash` (non-portable), no `set -e`, no input sanitization beyond
existence check, `source` on arbitrary files is risky, no tests, no documentation.

### Score 1 — unsafe-hook (PowerShell)

```powershell
$result = Invoke-Expression $args[0]
Write-Output $result
```

Why it scores 1: Uses `Invoke-Expression` on raw user input — textbook command injection
vulnerability allowing arbitrary code execution. No error handling, no input validation,
no documentation, no tests.
