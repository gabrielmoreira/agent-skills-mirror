---
name: powershell-scripting
description: Idiomatic PowerShell scripting — SupportsShouldProcess/-WhatIf/-Confirm, safe destructive operations, and preview-before-apply patterns
---

When writing or reviewing PowerShell scripts (`.ps1`) — especially ones that perform
destructive or bulk operations — apply this domain knowledge.

# PowerShell Scripting — Domain Knowledge

## Prefer Built-in ShouldProcess Over Custom Dry-Run Flags
Do **not** invent custom `-Execute` / `-DryRun` switches or a typed-`yes` prompt for
scripts that mutate state. Use PowerShell's built-in confirmation system so `-WhatIf`
and `-Confirm` work natively and consistently with every other cmdlet.

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $Path
)

foreach ($item in $items) {
    if ($PSCmdlet.ShouldProcess($item.Target, 'Migrate repository')) {
        # ...perform the mutation only inside this block...
    }
}
```

- `-WhatIf` emits the standard `What if: Performing the operation "..." on target "..."`
  lines and changes nothing — this replaces a hand-rolled "print the plan" dry run.
- `-Confirm` (or `ConfirmImpact='High'` triggering it automatically) shows the native
  prompt: **[Y] Yes [A] Yes to All [N] No [L] No to All [S] Suspend [?] Help**.
  Press **A** to apply all remaining operations.
- `-Confirm:$false` suppresses prompts for unattended/CI runs.
- Every state-changing operation must be guarded by its own `ShouldProcess` call so
  `-WhatIf` and `-Confirm` gate it correctly. Read-only steps run unconditionally.

## Common Anti-Patterns to Replace
- **Typed-`yes` gate** (`Read-Host` then compare to `"yes"`) → replace with
  `ShouldProcess` + `ConfirmImpact='High'`.
- **Custom `-Execute` / `-Force` switches** that reimplement preview vs apply →
  delete them; `-WhatIf` previews and a normal run applies.
- Manually printing a plan then looping → `ShouldProcess` already narrates each action
  under `-WhatIf`; keep an optional summary line but don't build a parallel dry-run path.

## Verification Discipline
- Validate syntax without executing: parse the file or run with `-WhatIf` against a
  throwaway target and confirm nothing changed (e.g., the resource is still in its
  original state and the script reports 0 mutations).
- Then confirm a real apply on the same throwaway target succeeds before using it for real.
