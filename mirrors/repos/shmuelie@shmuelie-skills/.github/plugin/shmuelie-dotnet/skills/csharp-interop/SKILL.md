---
name: csharp-interop
description: CsWin32, LibraryImport, ConPTY, Native AOT, runtime marshalling, plugin security, and VT parsing
---

When working on projects related to c# native interop patterns, apply this domain knowledge.

# C# Native Interop — Domain Knowledge

## CsWin32 (Microsoft.Windows.CsWin32)
- Preferred over hand-written P/Invoke for Windows APIs.
- Add as `<PackageReference Include="Microsoft.Windows.CsWin32" Version="0.3.269" PrivateAssets="all" />`.
- Create `NativeMethods.txt` at project root listing needed Win32 functions/types, one per line.
- Generates safe, AOT-compatible wrappers with SafeHandle and proper marshalling.
- Works with `PublishAot=true` and `DisableRuntimeMarshalling=true`.
- **COM interfaces**: v0.3.298+ can emit `[GeneratedComInterface]` (source-generated COM,
  AOT-friendly) instead of legacy `[ComImport]`. Pairs with `DisableRuntimeMarshalling`.
- **Run as an MSBuild build task** with `<CsWin32RunAsBuildTask>true</CsWin32RunAsBuildTask>`
  when other build steps need the generated types materialized on disk.
- **Generated output is in-memory** by default — the `obj` folder has no emitted `Generated`
  directory. Don't hunt for the file: write your helper against the *expected* Win32/COM
  signatures (e.g. `CoInitializeSecurity`, `CoImpersonateClient`, `CoRevertToSelf`) and let
  the compiler confirm the generated signatures, iterating on errors.

## COM Server / Class Factory (source-generated)
- `DllGetClassObject` returns a friendly `IClassFactory` whose `CreateInstance` uses the
  `out nint` shape; marshal the managed object with `ComInterfaceMarshaller<T>` /
  `StrategyBasedComWrappers` rather than hand-rolled `Marshal.GetComInterfaceForObject`.
- COM *callback* interfaces (device→managed) must also be `[GeneratedComInterface]` so the
  runtime can wrap the managed implementation.
- Testing pointer-based COM methods (`GetIconInfo(nint, ...)`) requires
  `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` in the **test** project too.

## Shell Icon Handler (IExtractIconW / custom file types)
- A shell icon handler is a COM in-proc server registered for a file extension; it needs a
  desktop/COM surface (packaged desktop extension or classic registration).
- `CreateIconFromResourceEx` turns **raw PNG bytes** into a valid `HICON` — reuse the native
  path instead of decoding yourself. For `.ico` input, parse the ICONDIR header to pick a
  frame.
- Prefer MSIX-style multi-PNG assets (one per target size) with best-fit selection over a
  single fixed-size icon, so the shell gets a crisp match at any DPI.

## LibraryImport (modern P/Invoke)
- Use `[LibraryImport]` instead of `[DllImport]` for new code — it's source-generated,
  AOT-compatible, and avoids runtime marshalling overhead.
- Requires `AllowUnsafeBlocks=true` in the csproj.
- String marshalling: specify `[LibraryImport("lib", StringMarshalling = StringMarshalling.Utf16)]`
  explicitly — there is no default.

## NativeLibrary.SetDllImportResolver
- Use for DLLs not on PATH (e.g., VoiceMeeter at "C:\\Program Files (x86)\\VB\\Voicemeeter\\").
- Register in a static constructor or module initializer.
- Look up install paths via Windows Registry (e.g., UninstallString under WOW6432Node).
- Example pattern:
  ```csharp
  NativeLibrary.SetDllImportResolver(typeof(MyInterop).Assembly, (name, asm, paths) => {
      if (name == "MyLib.dll") {
          string path = GetPathFromRegistry();
          return NativeLibrary.Load(path);
      }
      return IntPtr.Zero;
  });
  ```

## ConPTY (Windows Pseudo Console) — CRITICAL BUG PATTERN
- `UpdateProcThreadAttribute` for `PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE`:
  the API expects the HPCON value ITSELF as `lpValue`, NOT a pointer to it.
- WRONG: `ReadOnlySpan<byte>(&hpcHandle)` — causes double indirection → 0xC0000142 in all child processes.
- RIGHT: `(void*)hpcHandle` via raw pointer overload.
- This bug manifests as "all spawned processes exit with 0xC0000142" and looks like a Windows regression
  but is actually a calling convention error.

## Native AOT + Trimming
- Set `<PublishAot>true</PublishAot>` and `<PublishTrimmed>true</PublishTrimmed>`.
- Set `<IsAotCompatible>true</IsAotCompatible>` for libraries.
- Use `<DisableRuntimeMarshalling>true</DisableRuntimeMarshalling>` for modern interop
  (avoids the legacy marshalling layer entirely).
- WinUI 3 apps: the WindowsAppSDK auto-initializer conflicts with AOT — may need
  `<Compile Remove="**\\*AutoInitializer*.cs" />` in certain contexts.
- COM hosting: `<EnableComHosting>true</EnableComHosting>` for COM servers.

## Native Hosting (DNNE / nethost) — hosting CoreCLR in-proc from native
Used to call managed code from a native DLL (e.g. a C++ proxy that loads a .NET plugin
in-process). DNNE (Direct Native to .NET Exports) generates the host glue.
- **`nethost` is NOT in the DNNE NuGet package.** Get `nethost.lib` + `nethost.h` from the
  `Microsoft.NETCore.App.Host.win-<rid>` packs instead of vendoring binaries into git.
- **Don't vendor `platform.c`/`dnne.h`** — compile them straight from the restored DNNE
  package; point the `.vcxproj`/`.filters` at the package path.
- Discover the AppHost pack path with the MSBuild item
  `%(ResolvedAppHostPack.PackageDirectory)` — no hardcoded SDK version.
- **Prevent leaking exports**: set `DNNE_API_OVERRIDE=` on `platform.c` so DNNE's
  `__declspec(dllexport)` is stripped and the DLL exports only your real entry point.
- Provide a custom abort via `dnne_abort` and wire it with the linker's `/alternatename`
  (on x86/Win32 the cdecl decoration is `_dnne_abort`, sensitive to signature changes).
- Because you compile all of `platform.c`, some of its public functions come along unused —
  that's expected; don't cherry-pick unless size matters.

## VT Escape Sequence Parsing in C#
- C# string `"\\x1bE"` is actually character U+01BE (single char), NOT ESC followed by 'E'.
- Always use string concatenation: `"\\x1b" + "E"` for test sequences.
- Colon sub-parameters (`ESC[38:2:R:G:Bm`) should be treated as semicolons.
- Erased cells must use current SGR background attributes, not hardcoded defaults.

## IPC Message Patterns
- Use `System.Text.Json` with `[JsonDerivedType]` for polymorphic IPC messages.
- Length-prefixed framing: concurrent writes from multiple threads can corrupt framing
  without a WriteLock.
- Ensure response messages arrive before any streaming data (e.g., CreateSessionResponse
  must arrive before ScreenUpdate messages).

## Plugin Security
- Path validation: always append `Path.DirectorySeparatorChar` to the canonical plugin directory
  before `StartsWith` check; otherwise "plugins-evil/" passes validation for "plugins/".
- Shell commands: use `-EncodedCommand` with Base64 encoding to prevent PowerShell injection.
- Kill processes after timeout (e.g., 5 seconds for run-shell commands).

## Event Handler Cleanup
- Always unsubscribe event handlers in Close/Dispose methods (ClosePane, CloseWindow,
  DetachClient, etc.) — otherwise disposed objects accumulate and cause leaks/crashes.
