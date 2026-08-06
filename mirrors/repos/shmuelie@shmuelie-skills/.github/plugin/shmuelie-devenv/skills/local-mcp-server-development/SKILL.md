---
name: local-mcp-server-development
description: "Build local MCP servers in .NET that control desktop apps via COM/WinRT, with STA dispatching, tool gating, and ProgID probing"
version: 1.0.0
---

# Local MCP Server Development — Domain Knowledge

When building a local MCP server that drives a desktop application (OneNote, Outlook, Excel, etc.) via COM/WinRT, apply this domain knowledge.

## Before Building One
- **Search first**: Check NuGet, GitHub, and `mcp.json` registry for an existing MCP server before authoring a new one. Common app categories (Office, browsers, IDEs) often have community implementations.
- If an existing server exists but is missing a tool you need, prefer extending/forking it over building a parallel implementation.

## Project Shape
- Target `net10.0-windows` (or current windows TFM) for COM/WinRT interop.
- Single-file publish (`PublishSingleFile=true`, `SelfContained=false`) so the server is one `.exe` users add to their MCP config without dependency hunting.
- Living location: `Ideas/<AppName>Mcp/` (or wherever experimental projects go in this repo).
- Use the official `ModelContextProtocol` SDK for tool registration and stdio/named-pipe transport.

## STA Dispatcher for COM/WinRT
- COM apartment-threaded apps (OneNote, Office, classic WinRT components) **require an STA**.
- The MCP server's main thread is MTA by default — calls into COM from MTA fail with `RPC_E_WRONG_THREAD` or marshal across apartments.
- **Pattern**: spin up a single dedicated STA thread that owns all COM calls; marshal work onto it via a `BlockingCollection<Func<Task>>` queue. The MCP tool methods enqueue work and `await` the completion task.
- Initialize the STA thread with `Thread.SetApartmentState(ApartmentState.STA)` BEFORE `Start()`.
- Do NOT touch the COM app from any other thread, even for "read-only" property access.

## COM Adapter Pattern
- Wrap the raw COM object behind an adapter class that exposes typed methods returning `Task<T>`.
- The adapter is the only code that talks to COM; tool implementations call the adapter.
- **Surface HRESULTs as actionable errors**: catch `COMException`, decode the HRESULT, and throw a `McpException` whose message includes the hex code AND a hint (e.g. `0x8004200B → OneNote: object not modifiable; the section may be in a sync state`).
- Don't return `null` to indicate failure — throw with context so the agent can react.

## ProgID Probing
- COM ProgIDs are version-suffixed (`Application.15`, `Application.16`). Major versions vary by install (Office 2019 vs 2024 vs 365 click-to-run).
- Probe in descending order and bind the first one that returns a non-null instance:
  ```csharp
  foreach (var progId in new[] { "OneNote.Application.16", "OneNote.Application.15",
                                  "OneNote.Application.14", "OneNote.Application.12" })
  {
      var type = Type.GetTypeFromProgID(progId);
      if (type == null) continue;
      try { instance = Activator.CreateInstance(type); break; }
      catch (COMException) { /* try next */ }
  }
  ```
- Empirical: OneNote 2026 responded to ProgID `12` after `.15`/`.14` returned `E_FAIL`. Don't assume version → ProgID mapping; probe.
- Throw a clear "no compatible version found" error if the probe loop exhausts.

## Tool Registration
- Use the SDK's `[McpServerTool]` (or equivalent) attributes on adapter methods to auto-register.
- **Read-only by default, write tools opt-in**: gate any tool that mutates app state behind a `--enable-write` startup flag. Refuse with a clear policy message:
  ```
  Tool 'create_page' refused: this server is in read-only mode.
  Restart with --enable-write to allow mutations.
  ```
- Group tool names by verb: `list_*`, `get_*`, `find_*` (read), `create_*`, `append_*`, `replace_*`, `insert_*` (write).
- Suffix dangerous tools with `_unsafe` (e.g. `replace_page_outline_unsafe`) to make the destruction explicit at call sites.

## Content Conversion
- Native app formats are typically XML (OneNote OML, Word OOXML). Agents prefer Markdown.
- Provide both `get_*_xml` and `get_*_markdown` tools; the converter is internal.
- Prefer round-trip conversion (Markdown → XML → app → XML → Markdown) and unit-test fidelity on representative documents.

## Testing
- Aim for ~30+ unit tests covering converters, ProgID probing, tool refusal logic, and HRESULT decoding.
- COM-driven integration tests require a real installed app and are flaky in CI — keep them in a separate `Live*` test class gated by an env var (`MCP_LIVE_TESTS=1`).

## Validation Checklist Before Publishing
- `tools/list` returns every registered tool with correct schemas
- At least one read-only tool returns real data from the live app (e.g. `list_notebooks`)
- Read-only refusal returns the actionable policy message
- A bad input produces a useful error, not a silent failure or generic "tool failed"
- Single-file publish runs on a clean machine with the target app installed but no SDK/runtime
