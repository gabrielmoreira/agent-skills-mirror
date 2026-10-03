---
title: PowerShell
category: Language
x-claim-provenance:
- claim: PowerShell array-addition performance is version-sensitive because PowerShell 7.5 optimized repeated array addition that was costly in earlier versions.
  source: https://learn.microsoft.com/en-us/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations
  scope: PowerShell 7.5 array-addition optimization; compare against the project's resolved version.
- claim: PowerShell 6 and later default to utf8NoBOM for all text output, while Windows PowerShell 5.1 defaults are inconsistent — Out-File and the redirection operators create UTF-16LE, Set-Content and Add-Content use the ANSI code page for new files, and a BOM-less script is read as ANSI.
  source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding
  scope: PowerShell 7.6 documentation.
- claim: When $PSNativeCommandUseErrorActionPreference is $true, native commands with nonzero exit codes issue errors according to $ErrorActionPreference; its default is $false, and the feature was added in PowerShell 7.4.
  source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables
  scope: PowerShell 7.6 documentation dated 2026-06-29.
- claim: Output of remote commands is serialized and deserialized; a deserialized object is a snapshot that includes properties but no methods, except that some types such as DirectoryInfo and GUIDs are converted back into live objects.
  source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_output
---

The configured PowerShell edition and version, supported operating systems, language mode, module versions, remoting transport, provider context, and native-command policy decide which syntax and cmdlets apply, and feature availability depends on those editions and module versions. Encoding shows how far the editions differ: PowerShell 6 and later write BOM-less UTF-8 by default, while Windows PowerShell 5.1 writes UTF-16LE through `Out-File` and `>`, uses the ANSI code page for new files from `Set-Content` and `Add-Content`, and reads a BOM-less script as ANSI, so the same script can write different bytes, or misread its own non-ASCII text, under each edition.

Each boundary carries objects, formatted display text, serialized remote objects, bytes, or native text, and that choice defines its stream, error, exit-status, encoding, quoting, scope, and cleanup behavior. A remote command returns deserialized snapshots that keep properties but lose methods, apart from a few types such as `DirectoryInfo` and GUIDs that are rebuilt as live objects. A native command's nonzero exit code is not an error under `$ErrorActionPreference` unless `$PSNativeCommandUseErrorActionPreference`, added in PowerShell 7.4 and off by default, is enabled, so a script that sets `Stop` still continues past a failed executable. Scripts and commands that manage state need repeatable behavior where the contract requires it.

Behavior runs through pipeline enumeration, scalar versus collection shape, property adaptation, formatting commands, success, error, warning, information, verbose, and debug streams, terminating versus non-terminating errors, and preference variables. At native boundaries, argument passing, quoting, encoding, standard streams, `$LASTEXITCODE`, platform executable resolution, and whether PowerShell converted output into objects or strings decide the result. Behavior is also affected indirectly by:

- profiles, modules and autoloading, and aliases
- dynamic parameters, provider paths, and scope and dot-sourcing
- jobs, runspaces, and remoting serialization
- transcript behavior, credentials, and environment mutation

Behavioral evidence covers zero, one, and many pipeline values, error modes, stream redirection, native nonzero exits, quoting edge cases, Unicode, provider paths, remoting serialization, cancellation, and cleanup. Runtime evidence depends on each supported PowerShell edition and version and operating system with controlled modules and profiles, and object shape and displayed output are separate observable surfaces. Repeatable state-changing logic is evidenced by running it twice in an isolated representative environment and observing convergence, exit status, and rollback or cleanup behavior without hidden partial failures. A performance result is specific to the resolved edition and version, with cold and warm runs and the pipeline measured as a whole. Per-object pipeline work, native-process starts, remoting round trips and serialization, provider enumeration, and collection growth are the countable costs, and whether array addition is costly depends on the runtime version.
