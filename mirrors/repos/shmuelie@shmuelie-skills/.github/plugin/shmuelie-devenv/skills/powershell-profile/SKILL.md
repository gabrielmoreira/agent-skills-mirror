---
name: powershell-profile
description: PowerShell profile engineering, PSReadLine configuration, prompt customization, terminal directory reporting, git worktree detection, Start-Copilot script, and symlink management
---

When working on PowerShell profile scripts, custom cmdlets, or terminal customization, apply this domain knowledge.

# PowerShell Profile Engineering — Domain Knowledge

## Profile Architecture
- Keep the profile entry point small: run an interactivity guard, import reusable modules, then apply machine-specific configuration.
- Put shared prompt, PSReadLine, alias, path, and encoding setup in focused scripts or modules instead of one monolithic profile.
- Resolve symlinked script roots before deriving adjacent paths; never hardcode a checkout or worktree location.
- Keep host-specific behavior in an optional tail so the shared core works in ordinary terminals, remote shells, and build environments.
- **Window title guard**: the prompt only sets `$Host.UI.RawUI.WindowTitle` when **not** running under Copilot CLI (`if (-not $env:COPILOT_CLI)`). Copilot CLI manages its own terminal title, so setting it from the prompt would clobber it. Apply the same `$env:COPILOT_CLI` guard to any future title-setting logic.
- Scripts in `PowerShell/Scripts/` follow Verb-Noun PascalCase naming with approved PowerShell verbs.
- Shared utilities in `Utilities.ps1`: `Test-IsElevated`, `New-PathVariable`, `Invoke-InLocation`.
- Define a shared `Test-Interactive` helper and invoke it before loading PSReadLine or touching raw console APIs.

## Non-Interactive Session Handling
- **CRITICAL**: When PowerShell is spawned with redirected stdin (e.g., Copilot's `!` command), the profile must return early before hitting PSReadLine, console encoding, or `$Host.UI.RawUI` operations.
- `Test-Interactive` should check `[Console]::IsInputRedirected` — wrap in `try/catch` for environments where the Console class isn't available.
- Guard all interactive-only operations behind `Test-Interactive`.

## Windows Terminal Directory Reporting
- Windows Terminal's documented `OSC 9 ; 9 ; <CWD>` sequence only accepts a **Windows filesystem path**. PowerShell provider-qualified paths are not sufficient when the current location is a custom PSDrive or a non-filesystem provider.
- Build the report from `$ExecutionContext.SessionState.Path.CurrentLocation` only when the provider is `FileSystem`, and emit **`ProviderPath`** rather than `.Path`. Example: a filesystem drive `Repo:` rooted at `D:\repos` means `Repo:\project` must report `D:\repos\project`; `HKCU:\Software` or `Function:\prompt` must report nothing.
- Emit the directory report only to a supporting real terminal. Check
  `[Console]::IsOutputRedirected` before `[Console]::Write()`; writing through
  `Console` alone does **not** prevent redirected output. A multiplexer may
  filter the sequence; do not assume it reaches the outer terminal or add an
  unverified passthrough escape.
- Prevent terminal-control injection with **validation before serialization**, not just by using `ProviderPath`. Reject any path that contains:
  - C0 or C1 control characters (`0x00-0x1F`, `0x7F-0x9F`)
  - explicit OSC terminators or control bytes such as ESC and BEL
  - carriage return / line feed / tab
  - an embedded double quote (`"`) when using the documented quoted payload form
- The public Windows Terminal docs show a **quoted** `OSC 9;9` payload but do not define an in-band escaping grammar for embedded quotes or control bytes. In this profile, the safe behavior is to **not emit** when validation fails, rather than inventing an undocumented escaping scheme.
- The fixture below accepts only nonempty drive-rooted or UNC Windows paths.
  Empty, relative, POSIX, and device-namespace paths are not emitted. This is
  a guard model for a current filesystem `ProviderPath`, not a general path
  resolver or a promise that every Windows path form is supported.
- After validation, serialize the final payload as ordinary text/UTF-8 bytes. Preserve spaces and Unicode; reject dangerous bytes. Do not concatenate prompt text, provider names, aliases, or arbitrary user input into the OSC payload.
- Distinguish **directory reporting** from **working-directory inheritance**. `OSC 9;9` updates the terminal's metadata for features such as duplicate-tab/split-pane and persisted layouts; it does **not** move an already-running shell and does **not** retroactively change a tmux popup's startup directory.
- If the current provider is not `FileSystem`, skipping the report is the safe behavior. Reusing the last reported directory is better than publishing an invalid pseudo-path that causes the terminal to open new panes or tabs in the wrong place.

Concrete cases:
- **Custom filesystem drive**: `Set-Location Repo:\project` where `Repo:` maps to `D:\repos` -> report `D:\repos\project`, not `Repo:\project`.
- **Non-filesystem provider**: `Set-Location HKCU:\Software` -> emit no `OSC 9;9` sequence.
- **Spaces / Unicode**: `D:\Work\A B\日本語` -> quote the exact `ProviderPath`; do not escape spaces or transliterate Unicode.
- **Redirected stdout**: `powershell -File status.ps1 > status.txt` -> write plain status text only; do not append control sequences to `status.txt`.
- **Rejected payload**: a path containing `"` or a control byte -> emit nothing; do not try to partially sanitize and continue.

In-memory fixture for validating the payload without touching a real terminal:
```powershell
function New-TestWtOsc9Payload {
    param(
        [string]$ProviderName,
        [string]$ProviderPath,
        [bool]$IsOutputRedirected
    )

    if ($IsOutputRedirected -or $ProviderName -ne 'FileSystem') {
        return $null
    }

    if ([string]::IsNullOrWhiteSpace($ProviderPath) -or
        $ProviderPath -match '^\\\\[?.]\\' -or
        $ProviderPath -notmatch '^(?:[A-Za-z]:\\|\\\\[^\\]+\\[^\\]+(?:\\|$))') {
        return $null
    }

    if ($ProviderPath.IndexOf('"') -ge 0) {
        return $null
    }

    foreach ($ch in $ProviderPath.ToCharArray()) {
        $code = [int][char]$ch
        if (($code -ge 0x00 -and $code -le 0x1F) -or
            ($code -ge 0x7F -and $code -le 0x9F)) {
            return $null
        }
    }

    return ([string][char]27) + ']9;9;"' + $ProviderPath + '"' + ([string][char]7)
}

$payload = New-TestWtOsc9Payload -ProviderName 'FileSystem' -ProviderPath 'D:\Work\A B\日本語' -IsOutputRedirected $false
if ($null -eq $payload) { throw 'Expected a filesystem payload.' }
$bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
if ([System.Text.Encoding]::UTF8.GetString($bytes) -ne $payload) {
    throw 'OSC payload round-trip failed.'
}
foreach ($bad in @(
    $null,
    '',
    'relative\folder',
    '/tmp/project',
    '\\.\pipe\example',
    "D:\bad$([char]27)esc",
    "D:\bad$([char]7)bell",
    "D:\bad`nline",
    'D:\bad"quote',
    "D:\bad$([char]0x85)c1"
)) {
    if ($null -ne (New-TestWtOsc9Payload -ProviderName 'FileSystem' -ProviderPath $bad -IsOutputRedirected $false)) {
        throw 'Unsafe payload was not rejected.'
    }
}
```

## Start-Copilot Script
- Supports positional `$Prompt` parameter and `$NoResume` switch.
- **Passthrough commands** (`update`, `help`) bypass session logic and pass directly to the copilot executable.
- Check `$Prompt -in @('update', 'help')` to detect passthrough — don't let these bind to session logic.
- Extra arguments via `[Parameter(ValueFromRemainingArguments)]` are forwarded to the copilot executable.
- The synopsis should say "optionally in autopilot mode" since autopilot only activates when a `Prompt` is provided.

### Wrapping the Copilot CLI
- Resolve the real application with `Get-Command copilot -CommandType Application` so a `copilot` alias does not recursively invoke the wrapper.
- Build argument arrays explicitly. Do not assign a one-element array through an `if` expression, because PowerShell may unwrap it to a scalar and later `+=` operations become string concatenation.
- Verify argument mapping with `-WhatIf`, not by launching. Give the wrapper `[CmdletBinding(SupportsShouldProcess)]` and gate execution on `$PSCmdlet.ShouldProcess("$exe $displayArgs", 'Execute')`.
- Treat native exit codes as failures and include captured stderr in the error record.

### Command Resolution vs Native Process Creation
- `about_Command_Precedence` matters here: a bare command name can resolve to an alias, function, or cmdlet before an external application. An interactive shell shortcut that works at the prompt is not automatically suitable as the target of `Start-Process`, a terminal launcher, or any other host that needs a concrete child process.
- Use `Get-Command <name> -All` to inspect everything with that name, and `Get-Command <name> -CommandType Application -All` when you specifically need launchable applications. `ApplicationInfo.Source` gives the path that PowerShell would start.
- Fail loudly when discovery does not produce exactly the boundary you need. If no application is found, throw with the searched name. If multiple applications are found, surface the candidate paths and pick one deterministically (explicit path, documented preference, or user-configured location) instead of assuming `PATH` order is stable across shells and machines.
- The examples below deliberately select the first discovered application in
  the current environment. That is an explicit example policy, not a promise
  that the same version wins on every machine. Never expand `.Source` from
  multiple `ApplicationInfo` objects and pass the resulting array as one
  executable name.
- For a native executable, use separate arguments and the call operator, and
  check the result. Verify the application's parser and your PowerShell
  version's native-argument behavior when embedded quotes or empty arguments
  matter:
  ```powershell
  $git = (Get-Command git -CommandType Application -All -ErrorAction Stop |
      Select-Object -First 1).Source
  & $git '-C' 'C:\Work With Spaces' 'status' '--short'
  if ($LASTEXITCODE -ne 0) { throw "git failed with exit code $LASTEXITCODE." }
  ```
  Do not build one string such as `"$git -C C:\Work With Spaces status --short"` and hope a later layer reparses it the same way.
- An `Application` lookup can still return a `.cmd` or `.bat` shim, not a native
  executable. It may depend on `cmd.exe` parsing, PATHEXT lookup, or adjacent
  files. A host requiring a native executable should reject that boundary
  rather than silently substitute shell execution:
  ```powershell
  $application = Get-Command tool -CommandType Application -All -ErrorAction Stop |
      Select-Object -First 1
  if ([IO.Path]::GetExtension($application.Source) -in '.cmd', '.bat') {
      throw 'Configure the real executable or a separately reviewed shell launcher.'
  }
  ```
- If the documented entry point really is a shim, use an explicit,
  shell-specific launcher whose quoting and accepted input are tested. An
  argument array passed to `cmd /c` is **not** a general escaping solution:
  spaced shim paths can be reparsed incorrectly, and metacharacters such as
  `&`, `|`, `%`, or `!` can change meaning. Prefer the real executable for
  dynamic arguments; reject unsupported inputs rather than invent a generic
  escaping recipe or interpolate them into a command string.
- Prefer direct invocation (`& $exe @args`) for synchronous execution in the
  current host. `Start-Process -ArgumentList` joins its array into **one string**,
  so its elements are not preserved as an argv array; provide quoting for the
  target parser or use an appropriate process API with a real argument-list
  contract. For `Start-Process`, use an exact `-FilePath`, `-Wait -PassThru` when
  needed, and inspect the returned process's `ExitCode`, not `$LASTEXITCODE`.
  See [Start-Process](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/start-process#-argumentlist)
  and [command precedence](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_command_precedence).

### Terminal Host, Launcher, and Child-Shell Boundaries
- Distinguish the layers: current PowerShell session -> optional launcher (`wt`, `cmd /c start`, another host) -> child shell -> tool. Each layer has its own parsing rules, startup behavior, and exit behavior.
- Resolve aliases/functions/shims **before** crossing into another host. Pass the final executable path plus arguments to the launcher or child shell, not a convenient prompt-only alias from the parent session.
- A launcher usually finishes its job once it creates the child shell or pane. After that, success and failure belong to the child process tree. If you need an interactive shell to remain open after setup, make the child shell explicit (`pwsh -NoExit ...` or the shell equivalent). If you want failure to be immediate and visible, let the tool be the child process rather than hiding it behind an always-successful bootstrap shell.
- Keep startup state local to the child you are creating. Set environment variables, working directory, and temporary toolchain tweaks in the child command line or the child shell's startup script, rather than mutating parent-session state and hoping the launcher copies exactly what you intended.

### Toolchain Environments Are Fresh-Shell Boundaries
- Compiler and SDK setup is process-local: `PATH`, `INCLUDE`, `LIB`, prompt state, loaded modules, and toolchain marker variables all live in the current shell process. Once a shell has loaded one developer environment, trying to "switch" it in place risks mixed state from both toolchains.
- Prefer one fresh shell per toolchain version, architecture, or environment
  flavor. **A new process still inherits the parent's environment by default.**
  Start from a known-clean parent environment or configure the intended child's
  environment explicitly using a supported launcher API. Do not mutate shared
  parent/server state to prepare that child. Also control profile startup:
  `-NoProfile` skips profile scripts but does not reset inherited `PATH`, `LIB`,
  or `INCLUDE`. Apply the chosen toolchain setup only in the intended child.
- This valid, non-interactive example demonstrates a child-only setting, not
  a real SDK setup command. Use the vendor's setup routine in the actual child;
  add `-NoExit` only when an interactive shell should remain open:
  ```powershell
  $pwsh = (Get-Command pwsh -CommandType Application -All -ErrorAction Stop |
      Select-Object -First 1).Source
  & $pwsh '-NoProfile' '-Command' '$env:TOOLCHAIN_ROOT="C:\Sdk A"; Write-Output $env:TOOLCHAIN_ROOT'
  if ($LASTEXITCODE -ne 0) { throw "Child shell failed with exit code $LASTEXITCODE." }
  ```
  Keep the parent shell clean, and do not try to "undo" the first toolchain with manual environment-variable surgery after the fact.

### Restoring the terminal after an engine crash
- Copilot CLI can exit mid-frame and leave the terminal in a bad state: mouse tracking, focus reporting, the alternate screen buffer, bracketed paste, synchronized output, and the kitty keyboard protocol may still be enabled. After a non-zero exit, emit a reset when stdout is not redirected.
- **CRITICAL — these are DEC *private* modes; the disable sequence MUST include the `?`.** `CSI ? <modes> l` (DECRST) disables them; `CSI <modes> l` **without** the `?` is ANSI RM and is a **silent no-op** for mouse/alt-screen/etc. (Bug hit in this repo: `` `e[1000;1004;1049l `` did nothing; the fix was `` `e[?1000;1004;1049l ``.)
- **Full crash-recovery reset** (one `CSI ? … l` for all the private modes, then reset the kitty keyboard flags):
  ```powershell
  "`e[?2026;2004;1049;1006;1004;1003;1000l`e[=0u"
  ```
  Modes: `2026` synchronized output, `2004` bracketed paste, `1049` alternate screen, `1006`/`1003`/`1000` SGR/any-event/normal mouse, `1004` focus reporting. `` `e[=0u `` (kitty `CSI = 0 u`) **force-sets** the keyboard flags to 0 — more robust for crash recovery than `` `e[<u `` (`CSI < u`), which only *pops one entry* off the kitty stack and leaves deeper pushes enabled.
- `` `e `` is the PowerShell 6+ escape (equivalent to `[char]27`). Write it with `[Console]::Write` and the redirect guard keeps it off any captured stream.
- **Centralize it in one helper** (`Reset-TerminalModes` in `Utilities.ps1`) rather than inlining the literal in multiple places — two copies of an escape string drift, and the `?`-less no-op above was exactly that kind of divergence bug.
- Expose it as a **dedicated cmdlet** to run on demand after a crash. `Start-Copilot` calls it on non-zero exit (guard the call with `Get-Command Reset-TerminalModes` so `Shmuelie.Copilot` does not require `Shmuelie.Utilities`). Calling it from the `prompt` function on every render also works, but explicit crash recovery avoids unnecessary writes.


## PSReadLine Configuration
- History prediction, argument completers for dotnet/winget/uv.
- Tab completion customization for enhanced CLI experience.

## Git Status in Prompt
- `Get-GitStatusSummary` is the engine behind the prompt, psmux status bar, and Copilot CLI custom status line — parses `git status --porcelain=v1 --branch` into a typed object.
- The prompt shows a posh-git-style status: `[branch|REBASE-i 2/5 ↓2 ↑3 +A ~M -D | +A ~M -D !C ?]`
- **Branch color** reflects upstream state: Cyan (current), Green (ahead), Red (behind), Yellow (diverged), DarkCyan (upstream gone).
- **Ahead/behind** shows `↓M ↑N` (behind first, space between) when diverged, `↑N` or `↓M` when only one direction, `≡` when up-to-date, `×` when upstream is gone.
- **Operation detection**: Checks `.git/` sentinel files to show in-progress operations in Magenta: `|REBASE-i 2/5` (interactive with step/total), `|REBASE-m` (merge), `|REBASE`, `|AM` (applying patches), `|AM/REBASE`, `|MERGING`, `|REVERTING`, `|CHERRY-PICKING`, `|BISECTING`.
- **Conflicts** (`!N`): Unmerged files (UU, AA, DD, AU, UA) shown in red after working tree counts.
- **Untracked** (`?`): Shown when untracked files exist.
- **Stash count**: Not shown in prompt or StatusString, but `StashCount` property is available on the `GitStatusSummary` object for programmatic use.
- Shows repo name, elevation status (`^` prefix), and relative path variables.

## Cmdlet Documentation Standards
- **Comment-based help** blocks (`<#...#>`) with `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, and `.EXAMPLE` sections.
- **`[CmdletBinding()]`** on all functions with explicit parameter declarations and validation attributes.
- Common documentation gaps: missing `.PARAMETER` entries, missing `.EXAMPLE` sections, wrong cmdlet names in examples (e.g., examples for `Set-NodeVersion` saying `Use-NodeVersion`).
- Typos to watch: "interupted" → "interrupted", "Excplicitly" → "Explicitly", "insatlled" → "installed".

## Script Patterns
- Use `[ValidateNotNullOrEmpty()]`, `[ValidateSet()]`, `[ValidateRange()]` on parameters.
- Approved verb list: Get-, Set-, New-, Update-, Start-, Stop-, Reset-, Add-, Remove-, Rename-, Resume-, Merge-, Test-, Import-, Install-, Uninstall-, Enable-, Disable-, Invoke-, Show-, Wait-, Write-, Compress-, Repair-, Build-, Clear-, Edit-.
- Use `[switch]` for boolean flags, never `[bool]` (avoids `-Flag $true` syntax).
- Wire `-Force` through `$ConfirmPreference = 'None'` in `begin {}` instead of bypassing `ShouldProcess`.
- Use `Write-Verbose`/`Write-Information` instead of `Write-Host` for status messages.
- Return pipeline-friendly objects (with `PSTypeName`) instead of using `Write-Host` for output — callers can filter with `Where-Object` and format with `Format-Table`.
- Use `try`/`finally` to restore state on Ctrl+C (e.g., `$PSStyle.Progress.View`). The `finally` block runs on normal exit, exceptions, AND pipeline stops.
- Use `-Include`/`-Exclude` parameters with `ValidateSet` for step selection in multi-step cmdlets. Make them mutually exclusive via parameter sets.
- **Two independent "pick exactly one" axes need a cross-product of parameter sets.** PowerShell resolves a call to exactly one set, so independent axes such as input source `{Path, Uri}` and operation `{Inspect, Install}` require explicit matrix sets (`PathInspect`, `PathInstall`, `UriInspect`, `UriInstall`).
- **A set-defining switch must be `Mandatory` in its own set, or it can silently make several sets eligible.** Verify every valid combination and every expected conflict.
- **A cross-cutting *modifier* switch must stay untagged (optional, no `ParameterSetName`).** The inverse of the rule above: a switch that only *tweaks* behavior and should combine with any mode — e.g. `Start-Copilot -IncludeUnnamed` (show unnamed `(no summary)` sessions in the picker), composable with both the default resume flow and `-NoAutoResume` — must NOT define its own set. Leave it untagged so it lands in every set (works everywhere) and is a harmless no-op where it doesn't apply. Read it directly (`$IncludeUnnamed`), not via a `ParameterSetName`-derived `$is…` flag. Only make a switch set-defining when it must be mutually exclusive with other modes.
- **Renaming a set-defining switch:** add an alias for the old public name and rename only the parameter variable. Parameter aliases participate in parameter-set resolution, so stable internal set names do not need to change.
- **`-ErrorAction Ignore` vs `SilentlyContinue`**: Use `Ignore` when you truly don't care about errors (e.g., probing if a command exists). `SilentlyContinue` suppresses display but still adds to `$global:error`, polluting the error collection with junk entries.
- **`-Force` vs descriptive switch names**: Reserve `-Force` for "skip the confirmation prompt" (standard PowerShell convention). When a switch skips a *check* rather than a *prompt*, use a descriptive name like `-SkipDirtyCheck`. This avoids confusion when `ShouldProcess` already handles confirmation.
- **`Write-Error` for rejection, not `Write-Warning`**: When a cmdlet refuses to proceed (e.g., dirty state detected), use `Write-Error` — it sets `$?` to `$false` so scripts and automation can detect the failure. `Write-Warning` is informational and doesn't signal failure.

## Pipeline Input Gotchas
- **CRITICAL**: `[PSObject[]]` with `ValueFromPipeline` wraps each piped object in a 1-element array. Use `[PSObject]` (singular) for pipeline parameters — PowerShell delivers one object per `process` call.
- **CRITICAL — `if`/`else` returning a single-element array is unwrapped to a scalar.** `$args = if ($cond) { @() } else { @('--flag') }` assigns the **string** `'--flag'`, not a 1-element array, because PowerShell's output processor unwraps single-item collections from a statement's value. Every later `$args += 'x'` then does **string concatenation** (gluing with no separator at each junction), and `& $exe @args` splats the whole thing as **one** argument. Fix: build the array explicitly — `$args = @(); if (-not $cond) { $args += '--flag' }` — so it stays `[object[]]`. Symptom: joined output like `--flag--allow-all--deny-tool x` with missing spaces between separately-appended items.
- `Get-Content -ReadCount 0` returns a single multi-line string, not an array. Use `[System.IO.File]::ReadAllLines()` for accurate line counting.
- **CRITICAL — a `[string]`-typed variable/param coerces `$null` → `''` on assignment.** If a loop-local shares a name (PowerShell is **case-insensitive**) with a type-constrained `[string]$Name` parameter, then `$name = if ($noMatch) {…}` assigns `$null` but the constraint turns it into an empty string. `$x = $name ?? $summary ?? '(fallback)'` then keeps `''` (empty is not null), defeating the `??` fallback — and the loop also clobbers the `$Name` parameter. Symptom: a value that should be a placeholder shows up blank; the bug only reproduces *inside* the function (where the typed param exists), not in an extracted copy. Fix: give the local a distinct name (e.g. `$sessionName`). (Hit in `Start-Copilot` auto-resume: no-name sessions rendered blank instead of `(no summary)`, breaking the lone-named auto-resume.)
- When adding properties to piped objects, use `Add-Member -NotePropertyName X -NotePropertyValue Y -PassThru` — dot notation doesn't work on `ConvertFrom-Json` output.

## Cancellable Long-Running Cmdlets (Ctrl+C with partial results)
- **Problem**: a cmdlet that captures a pipeline into a variable and emits only at the end loses everything on Ctrl+C — the pipeline-stop aborts the whole statement before the final emit, so completed work is discarded.
- **Pattern**: consume Ctrl+C as *input* instead of letting it interrupt. On an interactive console, set `[Console]::TreatControlCAsInput = $true` (restore the previous value in `finally`), so Ctrl+C becomes a readable key and the function can return normally with whatever finished.
- This requires a **pollable** execution model, so replace `ForEach-Object -Parallel` (no control point) with throttled `Start-ThreadJob -ThrottleLimit` plus a polling loop that drains `Completed`/`Failed`/`Stopped` jobs into a `List`, updates `Write-Progress`, and checks `[Console]::KeyAvailable`/`[Console]::ReadKey($true)` for `Key -eq 'C'` + `Modifiers -band [ConsoleModifiers]::Control`.
- On cancel, `Stop-Job`+`Remove-Job` the remaining jobs (queued ones never started, running ones are killed), then return the accumulated results. Gate the whole thing behind an interactive-host check (`-not [Console]::IsInputRedirected -and $Host.Name -eq 'ConsoleHost'`) so CI/redirected runs keep the simple path. (See `Update-AllWorktrees`.)

## URL Parsing for Git Remotes
- `New-Repository` parses org and repo name from clone URLs. Supports:
  - `https://dev.azure.com/<org>/<project>/_git/<repo>`
  - `https://<org>.visualstudio.com/[DefaultCollection/]<project>/_git/<repo>` (legacy)
  - `https://github.com/<org>/<repo>[.git]`
  - `git@github.com:<org>/<repo>.git`
  - `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>`
- **CRITICAL**: Don't exclude `.` from repo name regex — repo names like `runtime.v2` and `spectre.console` are common. Use `[^/?]+` not `[^/?.]+`. The `.git` suffix is handled by `-replace '\.git$', ''`.

## DSC Bootstrap Script
- `Install-DscConfiguration.ps1` supports both Dev Box automation (SYSTEM) and interactive user execution.
- Auto-detects SYSTEM context via `[WindowsIdentity]::GetCurrent().IsSystem`.
- `-DscFile` parameter for using a local file instead of downloading.
- `-Force` suppresses confirmation prompts (standard PowerShell pattern).

## Performance Optimization Patterns

### Bulk Git Operations
- **Replace per-worktree `Get-GitStatus`** with a single `git for-each-ref --format='%(refname:short)|%(upstream:short)|%(upstream:track)' refs/heads/`. Returns ahead/behind/gone for ALL branches in ~50ms vs N × 350ms.
- Parse `%(upstream:track)` values: `[ahead N]`, `[behind M]`, `[ahead N, behind M]`, `[gone]`, or empty (up-to-date). Only `cd` into worktrees that need action.

### Parallel Independent Operations
- Use `ForEach-Object -Parallel -ThrottleLimit 4` for independent git merges or updates across repositories.
- **Parallel runspaces don't share the parent scope** — dot-source required scripts inside the parallel block using `$using:` for variables from the parent.
- Collect results via pipeline output from the parallel block, not by mutating shared collections.

### Bulk CIM Queries
- Avoid per-item `Get-CimInstance Win32_Service -Filter "Name='X'"` inside loops. Instead, query ALL services once in `begin{}`, index by name in a hashtable, and look up in `process{}`.

### ArgumentCompleter Over ValidateSet
- `[ValidateSet]` on parameters like `-Model` becomes stale when models are added/removed. Replace with `[ArgumentCompleter({ ... })]` that provides tab-completion from a known list but lets unknown values pass through to the CLI for validation. Prevents future breakage without sacrificing discoverability.

### Context-Aware Completions — Match the Valid Value Set Per Command
- When one completer serves several commands, group commands by **which value set is actually valid**, not by convenience. Registering a single completer for a whole command family can suggest values that the command will reject.
- Worktree example (`GitHelpers/_init.ps1`): `Set-Worktree`/`Remove-Worktree`/`cw`/`rw` operate on **existing** worktrees → complete branches that *have* a worktree (`Get-Worktrees`). `Add-Worktree` checks out a branch that has **no** worktree yet → complete *checkout-able* branches (`git branch` **minus** worktree branches), because `git worktree add` errors on a branch already checked out elsewhere. These are two separate `Register-ArgumentCompleter` registrations with two separate 30s caches.
- Keep it **soft** (ArgumentCompleter, no `[ValidateSet]`) so a remote/unfetched branch is still typeable for `Add-Worktree`.
- **The PS ArgumentCompleter and the C# PSReadLine predictor are two independent mechanisms** — a change to the completed value set must be mirrored in BOTH. The worktree completions live in `GitHelpers/_init.ps1` (tab-completion) AND `Ideas/WorktreePredictor/WorktreePredictor.cs` (inline prediction); the predictor keeps its own command groups + branch caches and must be rebuilt/redeployed when they change.
- **A PSReadLine predictor must preserve already-typed parameters/switches and only complete the trailing token.** A naive predictor that strips just the command name (or one known param like `-BranchName`) and appends a value silently produces **zero predictions** the moment the user includes any other flag — e.g. `Remove-Worktree -RemoveBranch <tab>` matched nothing because the predictor treated `-RemoveBranch` as the branch-name filter (and would also have dropped the flag from the accepted suggestion). Fix: split the line into `prefix` (everything before the trailing partial token, kept **verbatim** — preserves switches like `-RemoveBranch`/`-Force` and the user's casing) and `partial` (the branch fragment), then emit `prefix + branch`. Two rules that fall out: (1) if `partial` starts with `-` the user is typing a switch, so return no branch predictions; (2) match the command on a **word boundary** (next char whitespace/EOL) so `cwd` doesn't trigger the `cw` predictor.
- **Match the partial with `Contains` (substring), NOT `StartsWith`, when using ListView prediction.** Typing `Set-Worktree wim` should surface `Set-Worktree user/alex/wim-work`. `StartsWith` is appropriate for InlineView, but breaks middle-fragment matching when branches share a long prefix.

### PSReadLine Plugin Predictors Run Per-Keystroke — Gate Expensive Ones
- With `Set-PSReadLineOption -PredictionSource HistoryAndPlugin`, PSReadLine calls **every** registered `ICommandPredictor`'s `GetSuggestion` on **every keystroke**. A predictor that does cheap in-memory work (VariablePredictor — variable names; WorktreePredictor — a background-cached git branch list) is fine. A predictor that runs real work synchronously per keystroke will **freeze typing**.
- **`CompletionPredictor` runs the full PowerShell completion engine (`TabExpansion2`) on each keystroke.** In very large or virtualized repositories this can make typing unusably slow. Gate expensive predictors with an environment or repository-size check:
  ```powershell
  if (-not $env:DISABLE_EXPENSIVE_PREDICTORS -and $null -eq (Get-Module CompletionPredictor)) { Import-Module CompletionPredictor }
  ```
  Choose a stable environment signal that is set before the profile loads. Keep cheap, cache-backed predictors unconditional.
- **Debugging lesson:** when a shell cannot keep up with typing, investigate per-keystroke hooks and predictors before the prompt function. The prompt renders after Enter; predictors and key handlers run continuously. Diff the behavior-changing commit and measure subprocess cost before optimizing.

### Deploying a Module DLL That Running Sessions Have Loaded
- A predictor/binary-module DLL under `D:\PowerShell\Modules\...` is **file-locked** by every PowerShell session that imported it, so `Copy-Item` over it fails with "being used by another process" — **including from a fresh `pwsh -NoProfile`**, because the lock is held by the *other* live terminals, not the copying process. There is no in-session way to overwrite it in place while any terminal that loaded the module is open.
- **The right fix is versioned side-by-side module folders — deploy alongside a live session, no lock at all.** Put the module at `D:\PowerShell\Modules\<Name>\<version>\<Name>.dll` (+ `<Name>.psd1`) instead of flat at `...\<Name>\<Name>.dll`. `Import-Module <Name>` auto-selects the **highest `ModuleVersion`**, so a new build lands in a NEW (unlocked) version folder while live sessions keep the old folder's DLL loaded, and any new terminal picks up the new one. This removes the lock *and* the logon-timing problem — the deploy runs anytime from any shell (even the session that holds the old DLL). Rules:
  - The **version folder name must equal the manifest `ModuleVersion`**, or PowerShell ignores it. Single-source the version in the project's `.csproj` `<Version>` and write it into the copied `.psd1`'s `ModuleVersion`.
  - A **versioned subfolder (`1.0.1`) wins over a legacy flat root manifest** (`...\<Name>\<Name>.psd1`, effectively `1.0.0`) — so you can migrate incrementally: deploy `1.0.1+` alongside the still-locked legacy flat `.dll`, and prune the flat files later when nothing holds them.
  - **Prune old version folders best-effort** (keep newest N): `Remove-Item` each older folder in `try/catch` so a folder still locked by a live session is skipped, not fatal. The legacy flat `.dll` is typically the one skipped (locked) while its sibling `.psd1` deletes fine.
  - Bump `<Version>` per change. If you *don't* bump and the target version folder's DLL is locked, the copy fails — that's the one self-inflicted failure mode, and the fix is "bump the version so it deploys into a fresh folder."
  - Repo implementation: `Update-PredictorModule` (`Update-WorktreePredictor` / `Update-VariablePredictor`) in `PowerShell/Scripts/Helpers/PredictorHelpers.ps1`, and the two `Build and Deploy … Predictor Module` DSC steps dot-source that same file and call it (one source of truth for the deploy logic).
- **Superseded workarounds (why in-place deploy is painful) — kept for context:** deploying the flat DLL required a moment when *no* session held it (a **DSC apply** right after logon before terminals start, or a clean shell). `RunOnce` was tried and is **unreliable** for this — a value with no leading `!` is deleted by the shell *before* it runs; even the `!`-prefixed form (delete only after success) never fired because **RunOnce only runs at an actual interactive logon**, which a long-lived desktop session never hits. A pure `.cmd`-via-`cmd.exe` trigger (avoiding the flaky `pwsh` App Execution Alias) removed the PowerShell dependency but not the logon-timing problem. Versioned folders make all of that unnecessary.
- Verify predictor changes against the freshly-built `bin\Release\<tfm>\*.dll` (import + `Get-PSSubsystem -Kind CommandPredictor`); a fresh `pwsh` importing the module resolves the new version folder even while the old one stays loaded/locked in other sessions.

### Bypassing Aliases for CLI Subcommands
- When the profile defines `Set-Alias copilot Start-Copilot`, calling `copilot plugin list` invokes `Start-Copilot` (session picker) instead of the CLI. Use `Get-Command copilot -CommandType Application` to resolve the real exe path and call it directly.

### Streaming File Operations
- Replace `[System.IO.File]::ReadAllLines().Count` (allocates full string array) with a `StreamReader` loop: `while ($null -ne $reader.ReadLine()) { $count++ }`. Avoids loading multi-MB files into memory just to count lines.
- For multi-pass JSON parsing (find indices, extract data, filter IDs), restructure into a single pass that collects all needed data in one loop over `ConvertFrom-Json`.

### Write-Progress for Multi-Step Cmdlets
- For cmdlets iterating over a known-length collection (repos, package managers), add `Write-Progress` with step name and count:
  ```powershell
  $activity = 'Updating Apps'
  $stepIdx = 0
  try {
      foreach ($step in $steps) {
          $stepIdx++
          $pct = [int](100 * ($stepIdx - 1) / $steps.Count)
          Write-Progress -Activity $activity -Status "$($step.Name) ($stepIdx of $($steps.Count))" -PercentComplete $pct -Id 1
          # ... do work ...
      }
  } finally {
      Write-Progress -Activity $activity -Id 1 -Completed
  }
  ```
- **Use distinct `-Id` values** when nesting progress bars. The outer loop uses `-Id 1`, the inner operation (e.g., `Update-Worktrees`) uses `-Id 0` — PowerShell stacks them visually.
- **Always wrap in `try`/`finally`** — progress bars persist on Ctrl+C without the `-Completed` cleanup.
- **Don't add progress to pipeline cmdlets** (`process` block) — they don't know total count upfront. Only add to cmdlets with a known-length `foreach` loop.

### Avoiding Duplicate Cmdlets
- Before creating a utility cmdlet, check installed modules for an equivalent:
  `Get-Command -Module * | Where-Object Name -like '*keyword*'`.

### Caching CLI-Generated Completions
- Cache generated completion scripts, but **do not run `<tool> --version` on
  every profile load to validate the cache**. That still pays for a process
  launch per tool on every new shell; antivirus scanning and cold-start work
  can make even a version probe expensive and variable.
- Resolve the application with `Get-Command -CommandType Application`, not an
  invocation. If the optional tool is absent, skip its completion registration
  explicitly rather than attempting a failing probe or loading its old cache.
- Refresh when the cache is missing, older than the resolved executable, or past
  a configurable maximum age. Use UTC timestamps. A maximum age is a safety net
  for preserved executable timestamps or completion lists affected by other
  installed tools, not proof that timestamps detect every upgrade.

This PowerShell 7 example computes the **freshness decision only**; it does not
run a generator or load a script:

```powershell
$tool = Get-Command uv -CommandType Application -ErrorAction Ignore |
    Select-Object -First 1
$needsRefresh = $false
if ($null -eq $tool) {
    Write-Verbose 'uv is unavailable; skip completion registration.'
}
else {
    $cacheBase = [Environment]::GetFolderPath('LocalApplicationData')
    if ([string]::IsNullOrWhiteSpace($cacheBase)) {
        throw 'Choose a writable, user-owned cache directory for this platform.'
    }
    $cachePath = Join-Path $cacheBase 'ExampleProfileCache' 'uv-completion.ps1'
    $exe = Get-Item -LiteralPath $tool.Source -ErrorAction Stop
    $cacheItem = $null
    if (Test-Path -LiteralPath $cachePath -PathType Leaf -ErrorAction Stop) {
        $cacheItem = Get-Item -LiteralPath $cachePath -ErrorAction Stop
    }
    $now = [DateTime]::UtcNow
    $maxAge = [TimeSpan]::FromDays(7)
    $needsRefresh = (
        $null -eq $cacheItem -or
        $cacheItem.LastWriteTimeUtc -lt $exe.LastWriteTimeUtc -or
        ($now - $cacheItem.LastWriteTimeUtc) -ge $maxAge -or
        $cacheItem.LastWriteTimeUtc -gt $now
    )
}
```

- When the tool is present and refresh is needed, invoke its documented
  completion generator once. Check its exit code and validate the complete
  output before replacing a known-good cache. Do not dot-source a missing,
  partial, failed, or untrusted result. Keep script caches in a user-owned
  directory; never execute content from a location writable by other users.
- If PATH can select different installations or a shim can point to a different
  executable, record and compare the resolved source identity as well.
  Timestamp checks on an unchanged launcher do not prove its target is unchanged.
- Lazy or background regeneration can keep startup responsive, but is optional:
  coordinate writers and publish a complete snapshot safely. Report generation
  failures; do not silently treat them as successful refreshes. A valid,
  policy-permitted previous cache may remain usable while refreshing.
- Measure cache-hit and cache-miss startup separately. The expected steady-state
  improvement is removal of generator/version-probe process launches, not a
  universal millisecond guarantee.

| Case | Expected behavior |
|---|---|
| Tool absent | Skip its completion registration; launch nothing. |
| Cache missing | Generate once when the tool is available. |
| Executable newer than cache | Regenerate from the selected executable. |
| Cache within maximum age and not older than executable | Reuse it without launching the tool. |
| Cache expired, or timestamp unexpectedly in the future | Refresh; investigate clock/metadata anomalies when relevant. |
| Generator fails | Surface the failure; never publish or load its partial output. |

See [Get-Command](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/get-command)
and [Get-Item](https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-item)
for command discovery and filesystem metadata.

- For `Update-FormatData`, batch all format files into one call instead of N individual calls: `Update-FormatData -AppendPath @(Get-ChildItem *.format.ps1xml).FullName`.

### Lifetime-Qualified Cross-Process Cache Identity and Atomic Snapshot Publication

Keep completion **freshness** separate from the identity and delivery guarantees
of a shared snapshot. A reused session ID can point at an old cache and suppress
the first update after a server restart.

- Identify the lifetime of the **shared owner/server**, not each reporting
  client's PID: combine its PID, UTC start time, and logical session ID where
  applicable. Include the relevant user/machine namespace. All cooperating
  writers must agree on that identity; missing start-time evidence is not a
  reason to fall back silently to a reused PID alone.
- Serialize the tuple unambiguously with a defined field order and encoding,
  then derive both the file key and cross-process lock from the same hash.
  Validate exact, case-sensitive identity after reads and before cache hits.
- Lock the entire read/compare/write sequence. Write complete encoded data to a
  temporary file in the destination directory, flush, and use same-filesystem
  replace/rename semantics supported by that filesystem. This is atomic
  publication, not a guarantee of crash durability or network-filesystem
  behavior. Never treat a cross-filesystem move as an atomic replacement.
- A lock timeout proves only that the acquisition deadline expired. Report it;
  do not treat it as a cache hit. An abandoned mutex grants ownership to the
  waiter but makes protected state suspect: reread and validate it. If the last
  handle closed when the owner died, reopening the name may create a new mutex
  with no abandonment signal. Recovery cannot depend solely on that signal.
- Local snapshot publication is not acknowledgment that a native dispatch
  succeeded. Track attempts separately from acknowledged delivery; avoid
  suppressing retries or recording success merely because a process started.

| Scenario | Expected outcome |
|---|---|
| Server restarts or a PID/session ID is reused | Start time changes the shared identity; the first update is not suppressed by an old cache. |
| Concurrent writers | The second writer rereads the first complete snapshot after acquiring the same lock. |
| Writer stops before replacement | The last published snapshot remains intact; a later owner validates before republishing. |
| Acquisition deadline expires | Explicit timeout, not a success-shaped result; retry only under the caller's policy. |
| Local write succeeds but external dispatch fails | Preserve the distinction and report the actual delivery failure. |

The [disposable cache lab](examples/Invoke-CacheIdentityExample.ps1) exercises
these local coordination boundaries with synthetic identities, owned temporary
children, and bounded handshakes. Run it with PowerShell 7 on a local filesystem
supporting the documented mutex/replace APIs; it deliberately terminates an
owned child to demonstrate abandonment while an observer handle remains open.
It is not a production cache library or an external-delivery test:

```powershell
pwsh -NoProfile -File ./examples/Invoke-CacheIdentityExample.ps1 -FixtureParent 'C:\Temp\Cache Lab'
```

Resolve the example path relative to this installed skill directory. The
caller-selected parent is preserved; only a newly allocated, ownership-marked
child is cleaned up. Unconfirmed child termination retains the fixture and
reports cleanup errors instead of deleting data still in use.

## Subdirectory Module Pattern
- Large helper scripts (700+ lines) should be split into focused subdirectories: `Scripts/CopilotHelpers/`, `Scripts/GitHelpers/`, `Scripts/NodeHelpers/`.
- Each subdirectory has an `_init.ps1` entry point that dot-sources the individual files and registers argument completers.
- **Custom aliases are centralized** in `PowerShell/Scripts/Microsoft.PowerShell_aliases.ps1` (loaded by the shared core behind a `Test-Path` guard, mirroring `Scripts/Microsoft.PowerShell_paths.ps1`) — not scattered across the helper scripts. Use `Set-Alias` (create-or-update) so re-sourcing is idempotent. Argument completers that reference an alias by name (e.g. the worktree branch completer for `cw`/`rw` in `GitHelpers/_init.ps1`) keep working regardless of load order, since registration is name-keyed and doesn't require the alias to exist yet.
- The shared core dot-sources `_init.ps1` instead of the old monolithic file: `. "$scriptsRoot\Helpers\CopilotHelpers\_init.ps1"`.
- Format files (`.format.ps1xml`) move into their subdirectory alongside the scripts that define the types.
- The shared core's `Update-FormatData` call uses a recursive glob to pick up subdirectory format files: `Get-ChildItem "$scriptsRoot" -Filter *.format.ps1xml -Recurse`.
- **CRITICAL**: When splitting, count braces carefully — the last closing `}` of a function is easy to lose at file boundaries.
- Multiple profile entry points can source the same shared core through relative paths or symlinks.

## psmux/tmux Integration
- `$env:TMUX` is set by tmux/psmux when running inside a session — use this to detect the multiplexer.
- **Prompt simplification**: Skip `Write-VcsStatus` when `$env:TMUX` is set — the psmux status bar already shows git status. Keep the repo name path shortening.
- **Prompt-driven refresh**: Instead of timer-based `status-interval`, set `status-interval 0` and call `tmux refresh-client -S` from the prompt function after each command. This gives instant updates without polling.
- **Scope tmux identity claims carefully**: public tmux docs guarantee `TMUX_PANE` for real panes, and tmux source sets it in `spawn.c` for `spawn_pane`. But `display-popup` goes through the overlay path in `cmd-display-menu.c` -> `popup_display` in `popup.c`, not `spawn_pane`, so popup docs/source do **not** guarantee a distinct new pane ID for the popup command.
- **Launch-time cwd is separate from terminal metadata**: tmux's shipped popup support documents a start-directory flag (`display-popup -d <start-directory>`). Use that to choose the popup's initial cwd. Reporting `OSC 9;9` from inside the popup later only updates terminal metadata for that shell; it does not prove the popup inherited the parent's cwd correctly.
- **Set the popup marker before the profile loads**: the popup launcher must set a dedicated child-only marker in the popup environment before starting the shell. The profile can then see the marker on first load without probing external state. Do **not** rewrite `TMUX`, `TMUX_PANE`, or other native routing variables to fake parent ownership.
- **Scope the marker to its origin**: capture the current native
  session/server/pane context in child-only marker metadata before shell
  startup. Compare it with the current context before suppressing shared
  access. A matching marker suppresses the popup and its same-context
  descendants even when their native pane ID equals the parent's. A marker
  inherited into a positively identified, different ordinary pane must not
  suppress that pane. If identity cannot be established, skip shared access
  and report the uncertainty rather than claiming ownership.
- **Do not infer ownership from `TMUX_PANE` alone**: popup and parent may report the same native pane ID, or the popup may not provide a distinct pane identity at all. The child-only marker is what makes the shell a popup descendant for ownership purposes.
- **Popup descendants are non-owners of shared artifacts**: after matching the
  marker scope, bail out before **both** shared status writes **and any shared
  cache access (reads or writes)**. Keep local prompt rendering, footer text,
  and ordinary in-process calculations enabled. Do not publish the marker into
  the multiplexer's global/session environment.
- **No popup save/restore of parent state**: do not snapshot a parent's shared cwd/status on popup open and restore it on popup close. If the parent pane changes repo or directory while the popup is open, that restore replays stale data and overwrites a newer parent update.
- **Stay within shipped capabilities**: treat current tmux documentation as the boundary. Documented popup start-directory support is available; proposed behaviors from issue threads are not guarantees and must not be presented as if they already exist.
- **Git status script**: `psmux-git-status.ps1` is a standalone script invoked with `-NoProfile` that dot-sources `Get-GitStatusSummary.ps1` and outputs `RepoName\path [branch|OP ≡ +A ~M -D | +A ~M -D !C ?]` format matching the PowerShell prompt.
- **Git tab completion**: `GitTabCompletion.ps1` registers a native argument completer (`Register-ArgumentCompleter -CommandName git -Native`) providing context-aware completions for subcommands, branches, tags, remotes, stashes, files, and parameters — no external module dependency (replaces posh-git).

Conceptual ownership algorithm for popup-safe shared state:
1. Launcher sets a child-only marker and native origin context before the popup shell starts.
2. Profile compares marker scope with current context before any shared access. A match suppresses popup descendants even if `TMUX_PANE` matches the parent; a verified different ordinary pane is unaffected.
3. Ordinary owners use the lifetime-qualified shared identity described in [cache publication](#lifetime-qualified-cross-process-cache-identity-and-atomic-snapshot-publication), not a raw pane ID alone. Popup descendants must not use it to access shared state.
4. Popup descendants render prompt/footer locally but skip shared artifact reads and writes entirely.
5. Popup close performs no restore; the owning pane's next prompt/status refresh publishes the current truth.

Concrete cases:
- **Popup descendant with inherited native ID**: if the popup marker is set and both popup and parent report the same `TMUX_PANE`, the popup still must not read or write shared `statusline-cwd` or shared caches.
- **Popup descendant**: a popup shell with the child marker set may still show a local prompt and run `git status`, but it must not write `statusline-cwd` and must not consume/update any shared cache intended for other panes.
- **Ordinary pane in the same tmux session**: no child marker -> normal shared-state behavior continues.
- **Unrelated pane**: popup-only marker/origin metadata must not suppress shared-state behavior in a different ordinary pane.
- **Nested same-context shell**: an inherited matching marker continues to
  suppress shared reads and writes; it must not be cleared just because the
  shell's own PID changes.
- **Changed or unknown context**: a confirmed new ordinary pane is not the old
  popup; unknown identity does not grant shared-write permission. Origin matching
  is a routing guard, not a security boundary against malicious descendants.

References: [Windows Terminal directory reporting](https://learn.microsoft.com/windows/terminal/tutorials/new-tab-same-directory)
and the installed version's [tmux manual](https://man.openbsd.org/tmux).
The public [tmux source](https://github.com/tmux/tmux) distinguishes real-pane
creation (`spawn.c`) from popup overlays (`popup.c`); other multiplexers may
expose different identity and passthrough mechanisms.

## Copilot CLI Custom Status Line
- **Status line script**: `copilot-statusline.ps1` + `copilot-statusline.cmd` wrapper provide git status and context window usage in the Copilot CLI bottom bar.
- **Layout**: Left-right alignment — git info left, context/cost right, space-padded to terminal width (minus 4-char margin for CLI footer chrome). Falls back to linear `·`-joined layout if terminal is too narrow.
- **Left**: `RepoName [branch|OP ↓N ↑M +A ~M -D | +A ~M -D !C ?]`
- **Right**: `ctx: 42.1k/200k ████░░░░░░ 21% · 132 reqs, +3127/-789 lines · AI Credits: 3689`
- **Width detection**: `(Get-Host).UI.RawUI.WindowSize.Width` works with redirected stdin; `[Console]::WindowWidth` fails.
- **Configuration**: Requires `statusLine.type: "command"` and `statusLine.command: "~/.copilot/statusline.cmd"` in `~/.copilot/settings.json`, plus `feature_flags.enabled: ["STATUS_LINE"]`.
- **Symlink deployment**: DSC symlinks both `.cmd` and `.ps1` to `~/.copilot/`. The `.ps1` resolves its real script root via `(Get-Item $PSCommandPath).Target` to find `Get-GitStatusSummary.ps1` through the symlink.
- **Windows `.cmd` wrapper required**: Copilot CLI on Windows cannot reliably spawn `pwsh -File ...` inline — a `.cmd` wrapper is needed for argument parsing and stdin redirection to work correctly. Uses Windows PowerShell 5.1 (`powershell.exe`) instead of `pwsh` for ~600ms faster startup (~300ms vs ~900ms cold start), preventing timeouts in large repos.
- **Shared cwd/status artifacts are owner-only surfaces**: a non-popup owning pane may publish and consume shared cwd or status information for the status line, but popup descendants must not read from or write to those shared surfaces at all. This avoids a transient popup clobbering the parent pane's status line context or reusing stale parent state.
- **Per-segment fault isolation**: Each segment (git / ctx / cost / AIU) is built inside its own `try/catch`, and the final left-right layout has a plain-`Join-Segments` fallback `catch`. A throw while building one segment must not blank the whole line — the others still print. On failure a segment renders a dim `label: ?` marker (via `New-StatusMarker`) so a *broken* segment is visible, which is distinct from a legitimately *empty* segment (no data) that renders nothing. Guard **each** independent piece separately (cost and AIU share `$costSegment`, so wrap them individually and combine the non-null pieces) — otherwise one failure still takes out its sibling. Note PowerShell returns `$null` (not a throw) for property access on a wrong-typed value, so only genuine exceptions (e.g. an `[int]` cast on a non-numeric field) trip the marker; degenerate-but-valid output is left as-is.

### ForEach-Object -Parallel Gotchas
- `$using:` **cannot pass ScriptBlock values** — PowerShell throws "script block variables are not supported". Pass function bodies as strings if needed, or dot-source the script file inside the parallel block.
- **AllScope constant variables** (created with `New-Variable -Option Constant,AllScope`) may not resolve via `$using:`. Pre-resolve the value to a local variable before the parallel block: `$path = $PSUserRoot; ... $using:path`.
- **Switch parameters should never default to `$true`** — use opt-out names instead (e.g., `-NoPrune` instead of `-Prune = $true`). Switches always default to `$false`.

## Ownership-Preserving Updates for Symlink-Managed Copilot Configuration
- This is an **ownership** problem, not a freshness or launch-timing problem: determine who owns the on-disk path before changing bytes.
- Use first-party CLI help to define the fixture boundary before testing writers: `copilot help environment` documents `COPILOT_HOME`, and `copilot mcp --help` says user MCP configuration loads from `~/.copilot/mcp-config.json`.
- **Discovery metadata alone is not authoritative ownership.** `copilot mcp get ...` showing `Source: User`, or merely finding a file under `~/.copilot`, tells you which config layer won — not whether the path is an ordinary file, a managed symlink, or a broken link replacement.

The examples are Windows PowerShell 7.3+ **lab fragments**, not an unattended
configuration migrator. Replace `C:\ConfigLab` with a newly created disposable
lab you own and prepare the indicated synthetic files. Run in a dedicated child
shell with `$ErrorActionPreference = 'Stop'`; never use real credentials or
live configuration. For actual maintenance, quiesce readers/writers, preserve
the originals, and use an appropriate publication/recovery procedure. Writing
through a preserved link target is not itself an atomic-update guarantee.

### Inspect the active path first
```powershell
$activePath = 'C:\ConfigLab\active\.copilot\mcp-config.json'
$item = Get-Item -LiteralPath $activePath -Force
$authoritativePath = $item.FullName
$hop = $item
$visited = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

while ($hop.LinkType -eq 'SymbolicLink') {
    if ($hop -isnot [System.IO.FileInfo]) {
        throw 'Expected a file link, not a directory or unsupported object.'
    }
    if ([string]::IsNullOrWhiteSpace($hop.Target)) {
        throw 'Unsupported symbolic link with an empty target.'
    }

    $candidatePath = if ([System.IO.Path]::IsPathFullyQualified($hop.Target)) {
        [System.IO.Path]::GetFullPath($hop.Target)
    } elseif ([System.IO.Path]::IsPathRooted($hop.Target)) {
        throw 'Drive-relative or root-relative link targets require explicit review.'
    } else {
        [System.IO.Path]::GetFullPath((Join-Path $hop.Directory.FullName $hop.Target))
    }

    if (-not $visited.Add($candidatePath)) {
        throw "Symbolic-link cycle detected at $candidatePath"
    }

    $authoritativePath = $candidatePath
    try {
        $next = Get-Item -LiteralPath $candidatePath -Force -ErrorAction Stop
    } catch [System.Management.Automation.ItemNotFoundException] {
        break
    }
    $hop = $next
}

if ($hop.LinkType -ne 'SymbolicLink' -and $hop -isnot [System.IO.FileInfo]) {
    throw 'Expected the authoritative configuration to be a file.'
}

[pscustomobject]@{
    Path = $item.FullName
    LinkType = $item.LinkType
    ImmediateTarget = $item.Target
    AuthoritativePath = $authoritativePath
    AuthoritativeExists = Test-Path -LiteralPath $authoritativePath
}
```
- **Ordinary file**: treat it as user-owned until you intentionally migrate it back under management.
- **Valid symlink**: the authoritative source is the final existing non-link target, not the live link path.
- **Broken symlink**: the link still carries ownership metadata, but determine the intended target path explicitly and verify whether that path exists. `ResolveLinkTarget($false)` can return a non-null `FileInfo` whose `Exists` is `false`, so a null test alone misclassifies dangling links.
- Resolve **relative targets against the current link's containing directory at each hop**, not the process current directory.
- If a target chain leaves the expected managed tree, points somewhere you cannot justify, or ends in an unsupported object type, stop instead of inferring ownership from the directory name.

### Probe writer behavior per CLI version, in a disposable fixture
```powershell
$copilotExe = (Get-Command copilot.exe -CommandType Application -All -ErrorAction Stop |
    Select-Object -First 1).Source
$probeHome = 'C:\ConfigLab\fixture\.copilot'
$oldHome = $env:COPILOT_HOME
$oldAutoUpdate = $env:COPILOT_AUTO_UPDATE

try {
    $env:COPILOT_HOME = $probeHome
    $env:COPILOT_AUTO_UPDATE = 'false'
    & $copilotExe --version
    if ($LASTEXITCODE -ne 0) { throw 'CLI version probe failed.' }
    & $copilotExe mcp add demo -- cmd /c exit 0
    if ($LASTEXITCODE -ne 0) { throw 'CLI writer probe failed.' }
} finally {
    if ($null -eq $oldHome) {
        Remove-Item Env:COPILOT_HOME -ErrorAction SilentlyContinue
    } else {
        $env:COPILOT_HOME = $oldHome
    }

    if ($null -eq $oldAutoUpdate) {
        Remove-Item Env:COPILOT_AUTO_UPDATE -ErrorAction SilentlyContinue
    } else {
        $env:COPILOT_AUTO_UPDATE = $oldAutoUpdate
    }
}
```
- Re-run that probe against the **exact writer** and **exact CLI version** you plan to use.
- Prepare a separate ordinary-file, valid-link, or dangling-link case before
  each run. Compare the active entry's link metadata and the authoritative
  file's contents before and after; merely observing a new ordinary config
  in an empty directory does not test whether a writer preserves symlinks.
- Use the **native application path**, not a profile alias or wrapper function.
- **Observed in a disposable `COPILOT_HOME` fixture on GitHub Copilot CLI 1.0.84-3**: `copilot mcp add` replaced `mcp-config.json` symlinks with ordinary files instead of updating their targets. That happened for both a valid link and a broken link.
- Treat other writers (`/settings`, marketplace commands, future builds) as **unknown** until you repeat the same experiment for them.

### Synthetic cases

#### Ordinary file: preserve first, then edit in place
```powershell
$activePath = 'C:\ConfigLab\ordinary\.copilot\mcp-config.json'
$backupDir = 'C:\ConfigLab\ordinary\preserved'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$backupPath = Join-Path $backupDir ("mcp-config.before-edit.{0}.{1}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $PID)
if (Test-Path -LiteralPath $backupPath) { throw "Refusing to overwrite $backupPath" }

[System.IO.File]::Copy($activePath, $backupPath, $false)
$json = Get-Content -LiteralPath $activePath -Raw | ConvertFrom-Json -AsHashtable
$json = if ($json -is [hashtable]) { $json } else { throw 'Unsupported or null JSON root.' }
if (-not $json.ContainsKey('mcpServers') -or $json['mcpServers'] -isnot [hashtable]) {
    throw 'Unsupported schema: mcpServers must be an object.'
}
$json['mcpServers']['ordinary-demo'] = @{
    type = 'local'
    command = 'cmd'
    args = @('/c', 'exit', '0')
    tools = @('*')
}
$updatedJson = $json | ConvertTo-Json -Depth 100 -WarningAction Stop
$updatedJson | Set-Content -LiteralPath $activePath -NoNewline -ErrorAction Stop
```
- Preserve the pre-edit file before changing it.
- Because no managed link exists, there is nothing to restore yet; ownership stays with the active file.

#### Valid link: edit the authoritative source, not the live link
```powershell
$activePath = 'C:\ConfigLab\linked\active\.copilot\mcp-config.json'
$sourcePath = 'C:\ConfigLab\linked\managed\mcp-config.source.json' # resolved by the inspection loop above
$backupDir = 'C:\ConfigLab\linked\preserved'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$sourceBackup = Join-Path $backupDir ("source.before-edit.{0}.{1}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $PID)
if (Test-Path -LiteralPath $sourceBackup) { throw "Refusing to overwrite $sourceBackup" }

[System.IO.File]::Copy($sourcePath, $sourceBackup, $false)
$json = Get-Content -LiteralPath $sourcePath -Raw | ConvertFrom-Json -AsHashtable
$json = if ($json -is [hashtable]) { $json } else { throw 'Unsupported or null JSON root.' }
if (-not $json.ContainsKey('mcpServers')) { $json['mcpServers'] = @{} }
$json['mcpServers'] = if ($json['mcpServers'] -is [hashtable]) {
    $json['mcpServers']
} else {
    throw 'Unsupported schema: mcpServers must be an object.'
}
$json['mcpServers']['demo-safe'] = @{
    type = 'local'
    command = 'cmd'
    args = @('/c', 'exit', '0')
    tools = @('*')
}
$updatedJson = $json | ConvertTo-Json -Depth 100 -WarningAction Stop
$updatedJson | Set-Content -LiteralPath $sourcePath -NoNewline -ErrorAction Stop
```
- Start from the resolved authoritative source so the symlink stays intact and unrelated settings remain in the authoritative file. The same pattern works when the active link points to a **relative target** or to another link, as long as your inspection step resolved the full intended target path deliberately.
- Let the **next Copilot process** discover the change by reading the same active path at startup. Do **not** delete the live link, run a writer, then put the link back — concurrent readers can observe the wrong file during that window.

#### Drifted ordinary file: preserve both sides, surface conflicts, then stop for review
```powershell
$activePath = 'C:\ConfigLab\drifted\.copilot\mcp-config.json'
$sourcePath = 'C:\ConfigLab\managed\mcp-config.source.json'
$backupDir = 'C:\ConfigLab\drifted\preserved'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$stamp = "{0}.{1}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $PID
$activeBackup = Join-Path $backupDir "active.$stamp.json"
$sourceBackup = Join-Path $backupDir "source.$stamp.json"
if ((Test-Path -LiteralPath $activeBackup) -or (Test-Path -LiteralPath $sourceBackup)) {
    throw 'Refusing to overwrite an existing backup.'
}

[System.IO.File]::Copy($activePath, $activeBackup, $false)
[System.IO.File]::Copy($sourcePath, $sourceBackup, $false)
$source = Get-Content -LiteralPath $sourcePath -Raw | ConvertFrom-Json -AsHashtable
$drift = Get-Content -LiteralPath $activePath -Raw | ConvertFrom-Json -AsHashtable
$source = if ($source -is [hashtable]) { $source } else { throw 'Unsupported or null authoritative JSON root.' }
$drift = if ($drift -is [hashtable]) { $drift } else { throw 'Unsupported or null drifted JSON root.' }
if ($source['mcpServers'] -isnot [hashtable] -or $drift['mcpServers'] -isnot [hashtable]) {
    throw 'Unsupported schema: both mcpServers values must be objects.'
}

$conflicts = [ordered]@{
    TopLevelOnlyInSource = @()
    TopLevelOnlyInActive = @()
    ChangedTopLevelKeys = @()
    ServerOnlyInSource = @()
    ServerOnlyInActive = @()
    ChangedServers = @()
}

$sourceKeys = @($source.Keys | Where-Object { $_ -cne 'mcpServers' })
$driftKeys = @($drift.Keys | Where-Object { $_ -cne 'mcpServers' })
$conflicts.TopLevelOnlyInSource = @($sourceKeys | Where-Object { $_ -cnotin $driftKeys })
$conflicts.TopLevelOnlyInActive = @($driftKeys | Where-Object { $_ -cnotin $sourceKeys })
$conflicts.ChangedTopLevelKeys = @(
    $sourceKeys |
        Where-Object { $_ -cin $driftKeys } |
        Where-Object {
            (ConvertTo-Json $source[$_] -Depth 100 -Compress -WarningAction Stop) -cne
            (ConvertTo-Json $drift[$_] -Depth 100 -Compress -WarningAction Stop)
        }
)

$sourceServerNames = @($source['mcpServers'].Keys)
$driftServerNames = @($drift['mcpServers'].Keys)
$conflicts.ServerOnlyInSource = @($sourceServerNames | Where-Object { $_ -cnotin $driftServerNames })
$conflicts.ServerOnlyInActive = @($driftServerNames | Where-Object { $_ -cnotin $sourceServerNames })
$conflicts.ChangedServers = @(
    $sourceServerNames |
        Where-Object { $_ -cin $driftServerNames } |
        Where-Object {
            (ConvertTo-Json $source['mcpServers'][$_] -Depth 100 -Compress -WarningAction Stop) -cne
            (ConvertTo-Json $drift['mcpServers'][$_] -Depth 100 -Compress -WarningAction Stop)
        }
)

$conflicts | ConvertTo-Json -Depth 5
$differenceCount = 0
foreach ($names in $conflicts.Values) { $differenceCount += $names.Count }
if ($differenceCount -gt 0) {
    throw 'Preserved both versions. Review the backups and update the authoritative source intentionally before relinking.'
}
```
- Report **key names and server names only**. Do not echo secret values into logs while comparing drift.
- Do **not** relink while any added, removed, or changed setting/server is
  unresolved. Comparison is case-sensitive and deliberately conservative:
  property-order differences can also require manual review. Preserve both
  files and stop until every difference is intentionally decided; do not hide
  serialization-depth warnings or normalize away unfamiliar data.
- After review, update the authoritative source intentionally, then relink during a **maintenance** window when readers and writers are quiesced:
  ```powershell
  Remove-Item -LiteralPath $activePath
  New-Item -ItemType SymbolicLink -Path $activePath -Target $sourcePath -ErrorAction Stop | Out-Null
  ```
- If relinking fails, restore the preserved active file before resuming writers. This is controlled maintenance or recovery work, **not** a per-launch link swap.

#### Broken link: recreate the missing source before any writer runs
```powershell
$activePath = 'C:\ConfigLab\broken\.copilot\mcp-config.json'
$recoveryPath = 'C:\ConfigLab\broken\preserved\mcp-config.recovered.json'
$targetPath = 'C:\ConfigLab\broken\managed\mcp-config.source.json' # resolved by the inspection loop above
if (Test-Path -LiteralPath $targetPath) { throw 'Expected the authoritative target to be missing.' }
New-Item -ItemType Directory -Path (Split-Path $targetPath -Parent) -Force | Out-Null
[System.IO.File]::Copy($recoveryPath, $targetPath, $false)
```
- If the target path is known and trusted, recreate the **intended authoritative target** and keep the active link stable.
- If the target path is unknown, stop instead of inventing a new "authoritative" file.
- On CLI 1.0.84-3, `copilot mcp add` against a broken link **replaced the link with a plain file**. That is an ownership change, not a repair.
