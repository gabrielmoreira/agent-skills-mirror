---
name: uninstall-constellation
description: "Cleanly uninstalls the four Alex ACT constellation plugins (alex-act-core, alex-act-illustrator-plugin, alex-act-enterprise, alex-act-msft), the seventeen user-scope discipline instructions Core bootstrapped, and the four enabledPlugins entries — by detecting current state, generating a machine-tailored PowerShell script at the workspace root (fallback ~/.copilot/tmp/), and guiding the heir to run it after closing VS Code. Sidesteps the Windows os error 5 problem (VS Code holds plugin-tree handles) rather than trying to force through it. Preserves marketplace registrations and takes a settings.json backup. Use when a heir wants to fully remove the constellation, reset before troubleshooting, migrate to a different setup, or start clean before a major upgrade."
lastReviewed: 2026-08-01
---

# Uninstall Constellation

Detect current constellation state → generate a machine-tailored PowerShell script → guide the heir to run it from a fresh shell after closing VS Code. Never tries to force through Windows file locks.

## When to fire

- Heir invokes `/uninstall-constellation`
- Heir asks to "uninstall Alex ACT", "remove the constellation", "reset the discipline", "clean slate"
- Reset before reinstalling a specific plugin version for troubleshooting
- Migrating away from Alex ACT to a different Copilot configuration
- Preparing for a major upgrade where a clean reinstall is safer than an in-place update

## When NOT to fire

| Situation | Route to |
|---|---|
| Update to a newer plugin version | `/update-plugins` |
| Remove just one plugin | Direct `copilot plugin uninstall <name>` — no need for full teardown |
| Diagnose drift without removing | `/plugin-status` (audit only, no modifications) |
| Change per-project scope of a plugin | Edit `.github/copilot/settings.json` in the project |

## The design constraint

On Windows, `copilot plugin uninstall` cannot delete plugin trees while VS Code holds file handles on them. Every attempt fails with `Access is denied (os error 5)`. Any Chat-invoked flow that tries to remove plugins from inside VS Code fails partway and leaves residue: some plugin trees still on disk, some `enabledPlugins` entries pruned, some bootstrap files swept — a split-brain state that is worse than not having tried.

This skill sidesteps the constraint honestly:

1. Reads current state (plugin list, receipt, enabledPlugins) — all safe from Chat, no locked files touched.
2. Generates a machine-tailored PowerShell script with the exact state baked in as constants.
3. Writes the script to `<workspace_root>/.act-uninstall.ps1` and adds a `.gitignore` entry.
4. Instructs the heir to close VS Code, open a fresh PowerShell (not integrated terminal), and run the script.
5. The script self-verifies clean state and self-deletes on success.

The three cross-platform alternatives were evaluated and rejected:

| Approach | Why rejected |
|---|---|
| Force-close VS Code programmatically | Destroys unsaved work in other windows |
| Wait for VS Code to close, then run inline | Deadlock — Chat is inside VS Code; closing it terminates the skill mid-run |
| Force-close file handles via Sysinternals handle.exe | Corruption risk on active plugin state |

## Consent flow

### Step 1 — Confirm intent

Present the heir with a preview of exactly what will be removed. Read state before asking:

```powershell
copilot plugin list                                               # count of alex-act-* plugins
Get-Content "$env:USERPROFILE\.copilot\instructions\.alex-act-bootstrap.json"  # count of bootstrap files
Get-Content "$env:USERPROFILE\.copilot\settings.json"             # enabledPlugins entries
```

Report to the heir:

| Item | Count | Fate |
|---|---|---|
| Constellation plugins | N (up to 4) | Uninstalled |
| Bootstrap discipline files at `~/.copilot/instructions/` | N (up to 17) | Removed |
| Bootstrap receipt (`.alex-act-bootstrap.json`) | 1 if present | Removed |
| `enabledPlugins` entries in `~/.copilot/settings.json` | N (up to 4) | Removed (usually by CLI during uninstall) |
| Marketplace registrations (`alex-mall`, others) | Preserved | Kept for one-command reinstall |
| Unrelated `enabledPlugins` entries | Preserved | Untouched |
| `settings.json` backup | Created before edit | Kept indefinitely |

Ask: "Generate the uninstall script? Reply 'yes' to proceed, 'no' to cancel, or 'audit' to see current state without generating."

Default to no. Never proceed without explicit consent.

### Step 2 — Locate the target directory

Precedence order for where to write the script:

| Preference | Location | When it applies |
|---|---|---|
| 1 | `<workspace_root>/.act-uninstall.ps1` | Chat has a workspace open AND the root is writable AND (has `.git/` OR the heir accepts a plain-directory write). Discoverable from the file explorer; easy to run with `.\.act-uninstall.ps1`. |
| 2 | `~/.copilot/tmp/uninstall-constellation-<YYYYMMDD-HHmm>.ps1` | No workspace root, or root is read-only, or the heir explicitly wants it out of the project |

Create parent directories if missing. On the fallback path, always include the timestamp so re-runs do not collide.

### Step 3 — Generate the script

The script must include:

**Guard block** — refuses to execute if VS Code is running:

```powershell
$vscode = Get-Process Code, code -ErrorAction SilentlyContinue
if ($vscode) {
    Write-Host "[X] VS Code is still running. Close ALL windows (File > Exit) first." -ForegroundColor Red
    Write-Host "    Detected PIDs: $($vscode.Id -join ', ')" -ForegroundColor DarkGray
    exit 1
}
```

**Plugin uninstall block** — exact plugin identifiers baked in (not discovered at runtime):

```powershell
$plugins = @(
    'alex-act-core@alex-mall',
    'alex-act-illustrator-plugin@alex-mall',
    'alex-act-enterprise@alex-mall',
    'alex-act-msft'
)
foreach ($p in $plugins) {
    copilot plugin uninstall $p
    if ($LASTEXITCODE -ne 0) {
        Write-Host "     [!] exit code $LASTEXITCODE (continuing)" -ForegroundColor Yellow
    }
}
```

**Bootstrap sweep** — exact filenames read from the receipt at generation time (not `alex-act-*` glob, which would be brittle if the heir has hand-authored files matching the pattern):

```powershell
$bootstrapFiles = @(
    'alex-act-act-pass.instructions.md',
    'alex-act-critical-thinking.instructions.md',
    # ... 15 more, exact list from the receipt at time of generation
)
foreach ($f in $bootstrapFiles) {
    $path = Join-Path $env:USERPROFILE ".copilot\instructions\$f"
    if (Test-Path $path) { Remove-Item $path -Force }
}
Remove-Item "$env:USERPROFILE\.copilot\instructions\.alex-act-bootstrap.json" -Force -ErrorAction SilentlyContinue
```

**Settings.json backup + safety-net prune** — the backup is unconditional; the prune is a safety net because `copilot plugin uninstall` normally cleans `enabledPlugins` itself:

```powershell
$settingsPath = "$env:USERPROFILE\.copilot\settings.json"
$backup = "$settingsPath.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item $settingsPath $backup
# then prune the 4 baked entries — normally a no-op after step 1
```

**Verification block** — checks all four state dimensions and reports honestly:

```powershell
# plugin list, bootstrap files, receipt, settings.json enabledPlugins
```

If verify shows a residue in ANY dimension, the script exits with code 2 and keeps itself on disk for debugging. If clean, it exits with code 0 and self-deletes.

**Self-delete on success**:

```powershell
Remove-Item -Path $MyInvocation.MyCommand.Path -Force
```

### Step 4 — Update .gitignore

If `<workspace_root>/.git/` exists, append `.act-uninstall.ps1` to `.gitignore` (create the file if missing). Non-destructive — check for existing entry first. Skip on the `~/.copilot/tmp/` fallback path.

### Step 5 — Print run instructions

Direct the heir precisely:

> **Ready. To complete the uninstall:**
>
> 1. Close ALL VS Code windows (File → Exit).
> 2. Open a fresh PowerShell — Start Menu → PowerShell. Do NOT use VS Code's integrated terminal (it dies when VS Code closes).
> 3. Navigate: `cd <workspace_root>` (or the tmp folder for fallback).
> 4. Run: `.\.act-uninstall.ps1` (or `& "<full_path>"` for fallback).
> 5. On success, reopen VS Code and run `copilot plugin list` in the integrated terminal to verify no `alex-act-*` remains.

### Step 6 — Report

After writing the script, produce a summary:

| Item | Count | Fate |
|---|---|---|
| Script written | 1 | `<full_path>` |
| .gitignore updated | Yes/No | Line appended |
| Plugins slated for uninstall | N | Listed in script |
| Bootstrap files slated for sweep | N | Exact list from receipt |
| Marketplace registrations | Preserved | Named |

Then close with the reinstall path:

> After running, to reinstall: `copilot plugin install alex-act-core@alex-mall`, then reload VS Code and invoke `/alex-act-core install-constellation`.

## What's preserved

- Marketplace registrations (`alex-mall`, `azure-skills`, `fabric-collection`, `agency`) — reinstall stays one command
- Unrelated `enabledPlugins` entries (any plugin outside the constellation)
- `settings.json` backup at `~/.copilot/settings.json.bak-<timestamp>` — kept indefinitely for manual recovery

## What's removed

- All four constellation plugin trees under `~/.copilot/installed-plugins/`
- All `alex-act-*.instructions.md` files at `~/.copilot/instructions/` (exact list from the receipt, not a glob)
- Bootstrap receipt `.alex-act-bootstrap.json`
- Four constellation entries in `enabledPlugins` (usually already cleaned by `copilot plugin uninstall`)

## Report shape after successful script run

The heir will see the following on their PowerShell terminal:

```text
=== Alex ACT constellation uninstall ===
[1/4] Uninstalling 4 plugins...
     Plugin "alex-act-core@alex-mall" uninstalled successfully.
     ... (× 4)
[2/4] Sweeping bootstrap files...
    Removed 17 / 17 bootstrap files
     Removed receipt
[3/4] Pruning enabledPlugins (safety net) ...
     0 stale entries found — CLI uninstall already cleaned them
[4/4] Verifying clean state...
     Plugins:          0 (clean)
     Bootstrap files:  0 (clean)
     Receipt:          removed
     enabledPlugins:   0 stale entries (clean)
[OK] Constellation uninstall complete.
Deleting this script...
Done.
```

## Anti-patterns

| Anti-pattern | Correction |
|---|---|
| Try to run `copilot plugin uninstall` from inside Chat while VS Code is open | Hard block on Windows (`os error 5`). Detect + generate + guide is the honest path. |
| Sweep plugin trees directly via `Remove-Item -Recurse` on `installed-plugins/*` | Bypasses the CLI's own cleanup (`enabledPlugins` prune, marketplace unlinking). Use `copilot plugin uninstall`. |
| Skip the VS Code guard in the generated script | Heir will hit `os error 5` mid-run, leaving residue and confusion |
| Skip the settings.json backup | Heir loses recoverability if they change their mind mid-run |
| Ship a generic uninstall.ps1 template checked into Core | Each run has different state — bake exact filenames and plugin identifiers at generation time |
| Prompt "are you sure?" three times before generating | One confirmation of what will happen, then generate. The script itself is an artifact of consent — writing it is not the same as running it. |
| Report `Removed 0 / 4` as if it were a failure when the CLI already handled it | Distinguish "no-op because CLI already cleaned it" from "prune failed" in the report |
| Verification block that only checks plugins and bootstrap but skips settings.json | If a heir hand-added a stale entry, verify must catch it |

## Falsifiability

Sunset or restructure this skill if any of the following fires by **2026-11-01** (90 days):

- Copilot CLI adds an official "uninstall while locked" mechanism that makes the detect + generate + guide pattern obsolete
- macOS or Linux users report the workspace-root `.act-uninstall.ps1` boundary leak is a real friction (personal AI-tooling script appearing in work repos)
- Heirs report generating the script but never running it in more than 30% of invocations — closing VS Code is more friction than the design assumed
- The `.gitignore` auto-append silently overrides a heir's existing entry format ≥1 time
- The generated script fails on Windows PowerShell 5.1 (the design targets PS 7+, which is common but not universal)

Track outcomes in Steward `operations/ledgers/curation-log.md` tagged `[UNINSTALL-CONSTELLATION]`.

## Related

- [`plugin-management`](../plugin-management/SKILL.md) — general Copilot CLI plugin operations and safety rules
- [`install-constellation`](../install-constellation/SKILL.md) — sibling install flow that this skill undoes
- [`update-plugins`](../update-plugins/SKILL.md) — sibling update flow; if the heir is trying to fix a broken plugin, update may be the right route before uninstall
- Steward [`USER-EXPERIENCE.md` § Stage 6](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/USER-EXPERIENCE.md) — user-facing walkthrough of the uninstall procedure
- Steward [`PLUGIN-INTEGRATION.md` § 4](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/constellation/PLUGIN-INTEGRATION.md) — the plugin-management operational surface this skill sits within
