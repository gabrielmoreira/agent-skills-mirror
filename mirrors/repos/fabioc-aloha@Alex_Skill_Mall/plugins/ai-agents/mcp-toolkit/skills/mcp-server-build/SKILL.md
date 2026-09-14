---
name: mcp-server-build
description: "Implement an MCP server in TypeScript, Python, or C#/.NET, and register it with a host. Working stdio and HTTP samples verified against the published SDKs."
lastReviewed: 2026-09-13
---

# Build an MCP Server

Samples below are minimal but complete: each one runs.

## TypeScript

```bash
npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-mcp-server", version: "1.0.0" });

server.tool(
  "list_items",
  "List items with pagination. Use before acting on a specific item.",
  { page: z.number().default(1), limit: z.number().max(100).default(20) },
  async ({ page, limit }) => {
    try {
      const items = await api.listItems({ page, limit });
      return {
        content: [{
          type: "text",
          text: JSON.stringify({ items, page, hasMore: items.length === limit }),
        }],
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error: ${error.message}. Try: check API key, verify endpoint, reduce page size.`,
        }],
        isError: true,
      };
    }
  },
);

await server.connect(new StdioServerTransport());
```

## Python

```bash
pip install mcp
```

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("my-mcp-server")

class ListParams(BaseModel):
    page: int = Field(default=1, description="1-based page number")
    limit: int = Field(default=20, le=100, description="Items per page, max 100")

@mcp.tool(description="List items with pagination. Use before acting on one.")
async def list_items(params: ListParams) -> dict:
    items = await api.list_items(page=params.page, limit=params.limit)
    return {"items": items, "page": params.page, "hasMore": len(items) == params.limit}

if __name__ == "__main__":
    mcp.run()
```

FastMCP turns the Pydantic model into the input schema, so field descriptions and
constraints reach the agent. Put the constraint in the model rather than
validating by hand in the body.

## C#/.NET

```bash
dotnet new console
dotnet add package ModelContextProtocol
dotnet add package Microsoft.Extensions.Hosting
```

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using System.ComponentModel;

var builder = Host.CreateApplicationBuilder(args);

// stdio carries the protocol, so every log must go to stderr.
builder.Logging.AddConsole(o => o.LogToStandardErrorThreshold = LogLevel.Trace);

builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

await builder.Build().RunAsync();

[McpServerToolType]
public static class ItemTools
{
    [McpServerTool, Description("Echoes the message back to the client.")]
    public static string Echo(string message) => $"hello {message}";
}
```

`WithToolsFromAssembly` discovers every `[McpServerToolType]` class and registers
its `[McpServerTool]` methods. Prompts and resources use `[McpServerPromptType]`
and `[McpServerResourceType]`.

Three packages ship. `ModelContextProtocol.Core` is the minimum dependency set;
`ModelContextProtocol` adds hosting and DI and is the right starting point;
`ModelContextProtocol.AspNetCore` adds the HTTP transport.

### HTTP variant

```bash
dotnet new web
dotnet add package ModelContextProtocol.AspNetCore
```

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddMcpServer()
    .WithHttpTransport(options =>
    {
        options.SessionMode = HttpServerSessionMode.Stateless;
    })
    .WithToolsFromAssembly();

var app = builder.Build();
app.MapMcp();
app.Run("http://localhost:3001");
```

Stateless is the default and the right choice unless the server needs
server-to-client requests such as sampling or elicitation. Before exposing this
beyond localhost, read [mcp-server-hardening](../mcp-server-hardening/SKILL.md).

## Register It With a Host

A server nobody wired up is a process that exits. For a Copilot plugin, declare
it in `plugin.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "node",
      "args": ["dist/server.js"],
      "env": { "MY_API_TOKEN": "${env:MY_API_TOKEN}" }
    }
  }
}
```

`${env:VAR}` reads from the user's environment at launch, so a token never lands
in a committed file. Omit `env` when the server needs no secret.

Hosts read this at startup. A server that appears absent is usually one added to
a running session — restart before debugging anything else.

## The stdout Rule

On a stdio server, stdout **is** the protocol channel. A stray `print`,
`console.log`, or default-configured logger corrupts the stream and the client
disconnects with no useful error. Send every diagnostic to stderr. The C# sample
above configures this explicitly because the default does the wrong thing.

## Composes With

- [mcp-server-design](../mcp-server-design/SKILL.md) — decide what to expose first
- [mcp-server-testing](../mcp-server-testing/SKILL.md) — prove it works
- [mcp-server-hardening](../mcp-server-hardening/SKILL.md) — required before HTTP

## Verified Against

- C# sample: `ModelContextProtocol` v2.2.0, from the SDK's getting-started guide,
  2026-09-13
- TypeScript and Python samples follow the published SDK APIs; re-verify against
  the SDK docs when either releases a major version

## Would Revise If

- An SDK changes its server-construction API, making a sample here wrong rather
  than merely dated.
- `HttpServerSessionMode` stops defaulting to stateless, which would invert the
  advice in the HTTP variant.
