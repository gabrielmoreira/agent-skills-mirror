---
name: scripted-batch-execution
description: "Run known, lengthy multi-step shell work through a temporary script instead of repeated tool calls. Use when commands and their dependencies are already understood and verbose output would waste context; not for interactive discovery or short one-off commands."
---

# Scripted batch execution

When a task has several **known** shell steps, put their orchestration in one
task-scoped script and invoke it once. This reduces shell round trips and keeps
routine output out of the conversation; it does not make the underlying work
faster or replace inspection of failures.

## Decide what to batch

- Batch predictable sequences such as testing several projects, processing a
  known file list, or collecting repeatable diagnostics. Validate assumptions
  and inputs before writing the script.
- Keep exploratory commands separate when the next step depends on inspecting
  the previous result. Stop at any decision, approval, or safety boundary;
  do not hide it inside a long unattended script.
- For one short command, run it directly. For unrelated independent jobs,
  consider separate concurrent invocations rather than serializing them merely
  to save calls. Do not add a script just to work around a failing command.

## Make the run observable and safe

1. Put the reviewed script and its logs in a unique, task-scoped temporary
   directory outside the repository (or an existing session-artifact directory).
   Parameterize paths and options; never interpolate untrusted text into shell
   source or embed credentials. Use the existing environment/credential
   mechanism and avoid logging sensitive output.
2. Print a brief stage-start and stage-result line. Keep full output in
   per-stage files; return a bounded diagnostic excerpt on failure **only if**
   the output is safe to display. Otherwise return the file path and inspect or
   redact it locally. Do not discard stderr, turn failures into success, or
   report success while a child command is still running.
3. Fail at the first required-step failure and propagate its nonzero exit code.
   Check native process exit codes explicitly in PowerShell; in Bash, use
   `set -euo pipefail` and handle failures inside conditionals explicitly.
   For mutations, keep approval and preview/confirmation behavior intact;
   defer PowerShell `ShouldProcess` to `powershell-scripting` and shell safety
   details to `shell-wsl`.
4. Run the script with the appropriate synchronous tool timeout, or keep an
   intentionally long-running process attached and verify its status. Read the
   final exit status and inspect the concise summary; a quiet command is not
   proof it completed. Preserve failure logs until diagnosis, then remove only
   the script and task-specific artifacts created by this run.

## Example: three test calls become one

Instead of invoking `dotnet test` separately for each known project and
receiving three complete logs in the conversation, review and save this
PowerShell script in a unique temporary directory. Pass that directory as
`-LogDirectory` (created by the caller); the project paths are illustrative.

```powershell
param(
    [Parameter(Mandatory)] [string] $Repository,
    [Parameter(Mandatory)] [string] $LogDirectory
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
if (-not (Test-Path -LiteralPath $Repository -PathType Container) -or
    -not (Test-Path -LiteralPath $LogDirectory -PathType Container)) {
    throw 'Repository and log directory must exist.'
}

$projects = @(
    'tests\Api.Tests\Api.Tests.csproj',
    'tests\Core.Tests\Core.Tests.csproj',
    'tests\Cli.Tests\Cli.Tests.csproj'
)

for ($i = 0; $i -lt $projects.Count; $i++) {
    $project = $projects[$i]
    $log = Join-Path $LogDirectory ("test-{0}.log" -f ($i + 1))
    Write-Host "[$($i + 1)/$($projects.Count)] Testing $project"
    & dotnet test (Join-Path $Repository $project) --verbosity quiet *> $log
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        [Console]::Error.WriteLine("FAILED ($code): $project; full log: $log")
        # Only when the test output is known not to contain sensitive data:
        Get-Content -LiteralPath $log -Tail 40 | Out-Host
        exit $code
    }
    Write-Host "PASS $project"
}
Write-Host "PASS: $($projects.Count) projects"
```

Run it once, for example `pwsh -NoProfile -File <temp-script.ps1>
-Repository <repo-path> -LogDirectory <task-log-dir>`. A failure stops later
tests and keeps its log; success prints only stage summaries. Do not delete the
task directory before checking the final result.

For Bash, the equivalent wrapper must preserve the failing command's status
even when collecting a bounded excerpt:

```bash
#!/usr/bin/env bash
set -euo pipefail
repo=$1 logs=$2
for project in tests/Api.Tests/Api.Tests.csproj \
               tests/Core.Tests/Core.Tests.csproj \
               tests/Cli.Tests/Cli.Tests.csproj; do
  log="$logs/$(basename "$(dirname "$project")").log"
  printf 'Testing %s\n' "$project"
  if dotnet test "$repo/$project" --verbosity quiet >"$log" 2>&1; then
    printf 'PASS %s\n' "$project"
  else
    status=$?
    printf 'FAILED (%s): %s; full log: %s\n' "$status" "$project" "$log" >&2
    # Only print a tail if the log is known to contain no sensitive data.
    tail -n 40 -- "$log" >&2
    exit "$status"
  fi
done
```

Both examples assume the caller already knows which tests to run and has
created a unique log directory. If a failed test changes what to do next,
inspect its log and decide before launching another batch.
