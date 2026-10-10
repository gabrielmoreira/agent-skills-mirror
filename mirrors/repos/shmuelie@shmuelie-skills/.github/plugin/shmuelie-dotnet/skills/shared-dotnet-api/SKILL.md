---
name: shared-dotnet-api
description: "Design one typed, host-independent .NET API behind thin PowerShell cmdlets and CLI commands. Use when two command surfaces must share validation, state changes, cancellation, and errors without duplicating business logic."
---

# Shared .NET API, PowerShell cmdlets, and CLI

Use this architecture when two independently useful hosts must perform the same
operations. For one command surface, keep its logic there until a second
consumer actually exists. The core owns typed inputs/results, validation,
external-service interfaces, and domain errors; hosts own syntax, presentation,
and policy. Never have the CLI call PowerShell or a cmdlet shell out to the CLI.

## Boundaries

1. Define operations such as `ListAsync(CancellationToken)` and
   `AddAsync(name, CancellationToken)` in a plain class library. Inject an
   `IItemStore` (or explicit HTTP/client/clock dependencies) rather than
   reaching into host global state. Make normalized values and error types
   identical for both hosts. Prefer a typed result for expected partial
   outcomes; use exceptions for invalid inputs, conflicts, cancellation, and
   unexpected external failures. Don't return a success-shaped default on
   failure.
2. Compose dependencies **in each host**. Translate its arguments/configuration
   to the same core types, then translate the result/error outward; don't
   independently validate the business rule in each adapter. Host-only
   validation (unknown CLI options, missing required cmdlet parameters) is
   still necessary. Keep domain types free of `PSObject`, `Console`, and
   PowerShell error categories or process exit codes.
3. PowerShell cmdlets bind named and pipeline input, emit **objects** to the
   success pipeline, call `ShouldProcess` before invoking mutations, and map
   recoverable per-item validation/conflict to non-terminating errors; escalate
   unusable storage/configuration to terminating errors. Users can promote a
   non-terminating error via `-ErrorAction Stop`. Consult
   [powershell-scripting](../../../shmuelie-devenv/skills/powershell-scripting/SKILL.md)
   for `ShouldProcess`/confirmation conventions rather than inventing a dry-run
   flag. Long-running binary cmdlets should cancel a per-invocation token in
   `StopProcessing`; don't treat `CancellationToken.None` as a general solution.
4. The CLI emits text for people or stable JSON on stdout for automation and
   sanitized diagnostics on stderr. Document exit codes (`0` success, `1`
   storage failure, `2` invalid input, `3` conflict, `130` cancellation in the
   example). Subscribe to Ctrl+C, pass its token through the core, and
   unregister on exit. Never print secrets, sensitive paths, or full exceptions
   in machine-readable output. Changes to JSON fields and exit codes affect
   callers just like changes to public .NET types. Do not report cancellation
   *after* a mutation has committed; return its success result instead, so
   callers do not retry a completed write blindly.
5. Let each host resolve its own path/options and credentials; pass an
   authenticated client or narrowly scoped credential provider through an
   explicit interface. Never put tokens into parameters destined for logs,
   exception messages, command history, or checked-in examples. Make precedence
   (explicit option > host config > safe default) and authorization behavior
   consistent, without forcing a PowerShell configuration convention on the CLI.

## Runnable synthetic example

The [example](examples/Test-Example.ps1) uses a fictional item list in a local
JSON file. `Synthetic.Core` is a `net8.0` library; `Synthetic.Cli` is an
executable referencing it; `Synthetic.PowerShell` is a script module that loads
the same built DLL via `-ArgumentList`. Neither host is referenced by the core.
No feed, package, credential, service, or global module installation is needed.
Requires a .NET 8+ SDK targeting .NET 8 and PowerShell 7. Run from this skill's
`examples` directory:

```powershell
pwsh -NoProfile -File .\Test-Example.ps1

# To try it manually after the test builds the DLLs:
Import-Module .\Synthetic.PowerShell\Synthetic.PowerShell.psm1 `
    -ArgumentList (Resolve-Path .\Synthetic.Core\bin\Release\net8.0\Synthetic.Core.dll)
'first', 'second' | Add-SyntheticItem -Path .\items.json -WhatIf
'first', 'second' | Add-SyntheticItem -Path .\items.json
Get-SyntheticItem -Path .\items.json
dotnet .\Synthetic.Cli\bin\Release\net8.0\Synthetic.Cli.dll list --file .\items.json --json
dotnet .\Synthetic.Cli\bin\Release\net8.0\Synthetic.Cli.dll add --file .\items.json --name third
```

The test uses a uniquely named scratch child of `examples` and removes it in
`finally`. It builds the CLI (which builds the core), then runs assertions over
direct core operations, the PowerShell module, real CLI processes, and injected
CLI cancellation. It verifies normalization/conflict parity, pipeline binding
for both cmdlets, typed output, `-WhatIf` without writes, human and JSON output,
exit codes, non-terminating versus terminating cmdlet errors, and injected
cancellation in both adapters without stdout or mutation. This is a
self-contained PowerShell test runner,
**not** a `dotnet test` test project. Actual terminal Ctrl+C delivery is not
simulated; `RunAsync` and the script cmdlets receive pre-cancelled tokens to
prove each adapter's error mapping and lack of side effects.

This file store has no multi-writer locking or cross-process transaction. It
uses a sibling pending file and rename for individual writes, but do not use it
for concurrent writes or as a production database. The script cmdlets block on
the async file operation because PowerShell's synchronous pipeline needs an
object result; for long-running or cancellable work use binary cmdlets with
`StopProcessing` and test actual interruption.

## Packaging and verification

Build/publish the library, PowerShell module (with its compatible core DLL),
and CLI as **separate** artifacts. Resolve the library next to the deployed
module/executable; the example's explicit DLL path is for source checkout only.
Test the *installed* module's dependency loading and the published CLI on each
supported runtime, including assembly-version and target-framework compatibility;
don't rely only on project references. For package metadata, assets, packed
consumer tests, and release workflow use
[dotnet-library-projects](../../../shmuelie-nuget/skills/dotnet-library-projects/SKILL.md),
[nuget-package-authoring](../../../shmuelie-nuget/skills/nuget-package-authoring/SKILL.md)
and [nuget-release](../../../shmuelie-nuget/skills/nuget-release/SKILL.md).
Those skills address distribution rather than multi-host API design.
