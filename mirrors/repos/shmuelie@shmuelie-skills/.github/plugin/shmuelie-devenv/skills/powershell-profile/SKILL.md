---
name: powershell-profile
description: PowerShell profile engineering, PSReadLine configuration, prompt customization, git worktree detection, Start-Copilot script, and symlink management
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
- CLI tools that emit shell completion scripts (`uv generate-shell-completion powershell`, `dotnet-suggest list`) spawn a process on every profile load (~200-800ms each).
- **Cache to `%TEMP%`** with a version-gated sidecar file:
  ```powershell
  $cache = Join-Path $env:TEMP 'PowerShellProfileCache' 'uv-completion.ps1'
  $versionFile = Join-Path $env:TEMP 'PowerShellProfileCache' 'uv-completion.version'
  $current = (uv --version 2>$null)
  if (-not (Test-Path $cache) -or (Get-Content $versionFile -Raw)?.Trim() -ne $current) {
      # Regenerate
  }
  . $cache
  ```
- Regenerate only when `--version` output changes. Cache files are ephemeral (`%TEMP%`) and not tracked in the repo.
- For `Update-FormatData`, batch all format files into one call instead of N individual calls: `Update-FormatData -AppendPath @(Get-ChildItem *.format.ps1xml).FullName`.

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
- **Git status script**: `psmux-git-status.ps1` is a standalone script invoked with `-NoProfile` that dot-sources `Get-GitStatusSummary.ps1` and outputs `RepoName\path [branch|OP ≡ +A ~M -D | +A ~M -D !C ?]` format matching the PowerShell prompt.
- **Git tab completion**: `GitTabCompletion.ps1` registers a native argument completer (`Register-ArgumentCompleter -CommandName git -Native`) providing context-aware completions for subcommands, branches, tags, remotes, stashes, files, and parameters — no external module dependency (replaces posh-git).

## Copilot CLI Custom Status Line
- **Status line script**: `copilot-statusline.ps1` + `copilot-statusline.cmd` wrapper provide git status and context window usage in the Copilot CLI bottom bar.
- **Layout**: Left-right alignment — git info left, context/cost right, space-padded to terminal width (minus 4-char margin for CLI footer chrome). Falls back to linear `·`-joined layout if terminal is too narrow.
- **Left**: `RepoName [branch|OP ↓N ↑M +A ~M -D | +A ~M -D !C ?]`
- **Right**: `ctx: 42.1k/200k ████░░░░░░ 21% · 132 reqs, +3127/-789 lines · AI Credits: 3689`
- **Width detection**: `(Get-Host).UI.RawUI.WindowSize.Width` works with redirected stdin; `[Console]::WindowWidth` fails.
- **Configuration**: Requires `statusLine.type: "command"` and `statusLine.command: "~/.copilot/statusline.cmd"` in `~/.copilot/settings.json`, plus `feature_flags.enabled: ["STATUS_LINE"]`.
- **Symlink deployment**: DSC symlinks both `.cmd` and `.ps1` to `~/.copilot/`. The `.ps1` resolves its real script root via `(Get-Item $PSCommandPath).Target` to find `Get-GitStatusSummary.ps1` through the symlink.
- **Windows `.cmd` wrapper required**: Copilot CLI on Windows cannot reliably spawn `pwsh -File ...` inline — a `.cmd` wrapper is needed for argument parsing and stdin redirection to work correctly. Uses Windows PowerShell 5.1 (`powershell.exe`) instead of `pwsh` for ~600ms faster startup (~300ms vs ~900ms cold start), preventing timeouts in large repos.
- **Per-segment fault isolation**: Each segment (git / ctx / cost / AIU) is built inside its own `try/catch`, and the final left-right layout has a plain-`Join-Segments` fallback `catch`. A throw while building one segment must not blank the whole line — the others still print. On failure a segment renders a dim `label: ?` marker (via `New-StatusMarker`) so a *broken* segment is visible, which is distinct from a legitimately *empty* segment (no data) that renders nothing. Guard **each** independent piece separately (cost and AIU share `$costSegment`, so wrap them individually and combine the non-null pieces) — otherwise one failure still takes out its sibling. Note PowerShell returns `$null` (not a throw) for property access on a wrong-typed value, so only genuine exceptions (e.g. an `[int]` cast on a non-numeric field) trip the marker; degenerate-but-valid output is left as-is.

### ForEach-Object -Parallel Gotchas
- `$using:` **cannot pass ScriptBlock values** — PowerShell throws "script block variables are not supported". Pass function bodies as strings if needed, or dot-source the script file inside the parallel block.
- **AllScope constant variables** (created with `New-Variable -Option Constant,AllScope`) may not resolve via `$using:`. Pre-resolve the value to a local variable before the parallel block: `$path = $PSUserRoot; ... $using:path`.
- **Switch parameters should never default to `$true`** — use opt-out names instead (e.g., `-NoPrune` instead of `-Prune = $true`). Switches always default to `$false`.
