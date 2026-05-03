---
type: skill
lifecycle: stable
inheritance: inheritable
name: mcp-builder
description: Build MCP servers for LLM tool integration — Python (FastMCP), Node/TypeScript (MCP SDK), or C#/.NET (Microsoft MCP SDK)
tier: standard
applyTo: '**/*mcp*,**/*builder*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# MCP Server Development Guide


> Build high-quality MCP servers that enable LLMs to interact with external services

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

The quality of an MCP server is measured by how well it enables LLMs to accomplish real-world tasks.

---

## When to Build vs Use Existing

### Microsoft MCP Servers

Before building custom, check if Microsoft already provides one:

| Server | Type | Description |
|--------|------|-------------|
| **Azure MCP** | Local | 48+ Azure services (Storage, KeyVault, Cosmos, SQL, etc.) |
| **Foundry MCP** | Remote | `https://mcp.ai.azure.com` - Models, deployments, evals, agents |
| **Fabric MCP** | Local | Microsoft Fabric APIs, OneLake, item definitions |
| **Playwright MCP** | Local | Browser automation and testing |
| **GitHub MCP** | Remote | `https://api.githubcopilot.com/mcp` |

### Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Azure service integration | Use **Azure MCP Server** (48 services covered) |
| AI Foundry agents/evals | Use **Foundry MCP** remote server |
| Custom internal APIs | Build **custom server** (this guide) |
| Third-party SaaS integration | Build **custom server** (this guide) |

---

## Server Types

| Type | Transport | Use Case | Example |
|------|-----------|----------|---------|
| **Local** | stdio | Desktop apps, single-user, local dev | Azure MCP Server via NPM/Docker |
| **Remote** | Streamable HTTP | Cloud services, multi-tenant, Agent Service | `https://mcp.ai.azure.com` (Foundry) |

---

## Phase 1: Research and Planning

### 1.1 Understand Modern MCP Design

**API Coverage vs. Workflow Tools:**
Balance comprehensive API endpoint coverage with specialized workflow tools. When uncertain, prioritize comprehensive API coverage.

**Tool Naming and Discoverability:**
Clear, descriptive tool names help agents find the right tools quickly. Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`) and action-oriented naming.

**Context Management:**
Design tools that return focused, relevant data. Agents benefit from concise tool descriptions and the ability to filter/paginate results.

**Actionable Error Messages:**
Error messages should guide agents toward solutions with specific suggestions and next steps.

### 1.2 Study MCP Protocol Documentation

Start with the sitemap: `https://modelcontextprotocol.io/sitemap.xml`

Key pages to review:

- Specification overview and architecture
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions

### 1.3 Select Language and Transport

**Language Selection:**

| Language | Best For | SDK |
|----------|----------|-----|
| **TypeScript** (recommended) | General MCP servers, broad compatibility | `@modelcontextprotocol/sdk` |
| **Python** | Data/ML pipelines, FastAPI integration | `mcp` (FastMCP) |
| **C#/.NET** | Azure/Microsoft ecosystem, enterprise | `Microsoft.Mcp.Core` |

**Transport Selection:**

| Transport | Use Case | Characteristics |
|-----------|----------|-----------------|
| **Streamable HTTP** | Remote servers, multi-tenant, Agent Service | Stateless, scalable, requires auth |
| **stdio** | Local servers, desktop apps | Simple, single-user, no network |

---

## Phase 2: Implementation

### TypeScript Server (Recommended)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-mcp-server",
  version: "1.0.0",
});

// Register a tool with Zod schema
server.tool(
  "get_weather",
  "Get current weather for a city",
  { city: z.string().describe("City name") },
  async ({ city }) => ({
    content: [{ type: "text", text: JSON.stringify({ city, temp: "72°F" }) }],
  })
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python Server (FastMCP)

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("my-mcp-server")

class WeatherParams(BaseModel):
    city: str = Field(description="City name")

@mcp.tool(description="Get current weather for a city")
async def get_weather(params: WeatherParams) -> dict:
    return {"city": params.city, "temp": "72°F"}

if __name__ == "__main__":
    mcp.run()
```

### C#/.NET Server

```csharp
using Microsoft.Mcp.Core;

var server = new McpServerBuilder()
    .WithName("my-mcp-server")
    .WithVersion("1.0.0")
    .AddTool("get_weather", "Get current weather", async (string city) =>
        new { city, temp = "72°F" })
    .Build();

await server.RunAsync();
```

---

## Tool Design Best Practices

### Input Schema

- Use Zod (TypeScript) or Pydantic (Python) for validation
- Include constraints and clear descriptions
- Add examples in field descriptions

### Output Schema

- Define `outputSchema` where possible for structured data
- Use `structuredContent` in tool responses (TypeScript SDK feature)
- Helps clients understand and process tool outputs

### Annotations

| Annotation | Purpose |
|------------|---------|
| `readOnlyHint: true` | Tool doesn't modify state |
| `destructiveHint: true` | Tool makes irreversible changes |
| `idempotentHint: true` | Safe to retry |
| `openWorldHint: true` | Tool accesses external systems |

### Implementation Patterns

```typescript
// Good: Async, error handling, pagination
server.tool(
  "list_items",
  "List items with pagination",
  {
    page: z.number().default(1),
    limit: z.number().max(100).default(20),
  },
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
  }
);
```

---

## Phase 3: Testing

### Build and Verify

**TypeScript:**

```bash
npm run build
npx @modelcontextprotocol/inspector ./dist/server.js
```

**Python:**

```bash
python -m py_compile your_server.py
npx @modelcontextprotocol/inspector -- python your_server.py
```

### MCP Inspector

Interactive debugging for any MCP server:

```bash
npx @modelcontextprotocol/inspector /path/to/your/mcp-server
```

### Code Quality Checklist

- [ ] No duplicated code (DRY principle)
- [ ] Consistent error handling with actionable messages
- [ ] Full type coverage
- [ ] Clear tool descriptions
- [ ] Pagination support where applicable
- [ ] Proper async/await for I/O operations

---

## Phase 4: Create Evaluations

### Evaluation Purpose

Test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

### Create 10 Evaluation Questions

1. **Tool Inspection**: List available tools and understand capabilities
2. **Content Exploration**: Use READ-ONLY operations to explore data
3. **Question Generation**: Create 10 complex, realistic questions
4. **Answer Verification**: Solve each question yourself to verify answers

### Evaluation Requirements

Each question must be:

- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requiring multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer that can be verified by string comparison
- **Stable**: Answer won't change over time

### Output Format

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined?</question>
    <answer>3</answer>
  </qa_pair>
  <!-- More qa_pairs... -->
</evaluation>
```

---

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Tools not appearing | Server not responding to `tools/list` | Verify tool registration, check server startup |
| Stdout pollution | Debug output on stdout | Move debug output to stderr |
| Connection refused | Port conflict or server crash | Check port availability, review logs |
| Timeout | Slow API calls | Add timeout handling, implement pagination |
| Schema validation | Invalid input schema | Use Zod/Pydantic with proper constraints |

---

## Related Skills

This skill complements:

- **mcp-development** — Core MCP protocol patterns and architecture
- **azure-architecture-patterns** — When building Azure-integrated MCP servers
- **testing-strategies** — For comprehensive MCP server testing

---

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
