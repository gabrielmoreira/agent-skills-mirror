---
type: skill
lifecycle: stable
inheritance: inheritable
name: copilot-sdk
description: Build applications powered by GitHub Copilot using the Copilot SDK — session management, custom tools, streaming, hooks, MCP servers, BYOK, deployment patterns
tier: standard
applyTo: '**/*copilot*,**/*sdk*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# GitHub Copilot SDK


> Build applications that programmatically interact with GitHub Copilot

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

The SDK wraps the Copilot CLI via JSON-RPC, providing session management, custom tools, hooks, MCP server integration, and streaming across Node.js, Python, Go, and .NET.

---

## Prerequisites

- **GitHub Copilot CLI** installed and authenticated (`copilot --version`)
- **GitHub Copilot subscription** (Individual, Business, or Enterprise) — not required for BYOK
- **Runtime:** Node.js 18+ / Python 3.10+ / Go 1.21+ / .NET 8.0+

## Installation

| Language | Package | Install |
|----------|---------|---------|
| Node.js | `@github/copilot-sdk` | `npm install @github/copilot-sdk` |
| Python | `github-copilot-sdk` | `pip install github-copilot-sdk` |
| Go | `github.com/github/copilot-sdk/go` | `go get github.com/github/copilot-sdk/go` |
| .NET | `GitHub.Copilot.SDK` | `dotnet add package GitHub.Copilot.SDK` |

---

## Architecture

```text
Your App → SDK Client → [stdio/TCP] → Copilot CLI → Model Provider
                                           ↕
                                      MCP Servers
```

**Transport modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Stdio** (default) | CLI as subprocess via pipes | Local dev, single process |
| **TCP** | CLI as network server | Multi-client, backend services |

---

## Core Pattern: Client → Session → Message

### Node.js / TypeScript

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({ model: "gpt-4.1" });

const response = await session.sendAndWait({ prompt: "What is 2 + 2?" });
console.log(response?.data.content);

await client.stop();
```

### Python

```python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()
    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})
    print(response.data.content)
    await client.stop()

asyncio.run(main())
```

### Go

```go
client := copilot.NewClient(nil)
if err := client.Start(ctx); err != nil { log.Fatal(err) }
defer client.Stop()

session, _ := client.CreateSession(ctx, &copilot.SessionConfig{Model: "gpt-4.1"})
response, _ := session.SendAndWait(ctx, copilot.MessageOptions{Prompt: "What is 2 + 2?"})
fmt.Println(*response.Data.Content)
```

### .NET

```csharp
await using var client = new CopilotClient();
await using var session = await client.CreateSessionAsync(new SessionConfig { Model = "gpt-4.1" });
var response = await session.SendAndWaitAsync(new MessageOptions { Prompt = "What is 2 + 2?" });
Console.WriteLine(response?.Data.Content);
```

---

## Streaming Responses

Enable real-time output by setting `streaming: true`:

```typescript
const session = await client.createSession({ model: "gpt-4.1", streaming: true });

session.on("assistant.message_delta", (event) => {
    process.stdout.write(event.data.deltaContent);
});
session.on("session.idle", () => console.log());

await session.sendAndWait({ prompt: "Tell me a joke" });
```

---

## Custom Tools

Define tools that Copilot can call:

```typescript
import { CopilotClient, defineTool } from "@github/copilot-sdk";

const getWeather = defineTool("get_weather", {
    description: "Get the current weather for a city",
    parameters: {
        type: "object",
        properties: { city: { type: "string", description: "The city name" } },
        required: ["city"],
    },
    handler: async ({ city }) => ({ city, temperature: "72°F", condition: "sunny" }),
});

const session = await client.createSession({
    model: "gpt-4.1",
    tools: [getWeather],
});
```

### Tool Requirements

- Handler must return JSON-serializable data (not `undefined`)
- Parameters must follow JSON Schema format
- Tool description should clearly state when to use

---

## Hooks

Intercept and customize session behavior at key lifecycle points:

| Hook | Trigger | Use Case |
|------|---------|----------|
| `onPreToolUse` | Before tool executes | Permission control, argument modification |
| `onPostToolUse` | After tool executes | Result transformation, logging, redaction |
| `onUserPromptSubmitted` | User sends message | Prompt modification, context injection |
| `onSessionStart` | Session begins | Add context, configure session |
| `onSessionEnd` | Session ends | Cleanup, analytics, metrics |
| `onErrorOccurred` | Error happens | Custom error handling, retry logic |

### Pre-Tool Use Hook

```typescript
const session = await client.createSession({
    hooks: {
        onPreToolUse: async (input) => {
            if (["shell", "bash"].includes(input.toolName)) {
                return { permissionDecision: "deny", permissionDecisionReason: "Shell access not permitted" };
            }
            return { permissionDecision: "allow" };
        },
    },
});
```

### Post-Tool Use Hook (Redaction)

```typescript
hooks: {
    onPostToolUse: async (input) => {
        if (typeof input.toolResult === "string") {
            let redacted = input.toolResult;
            for (const pattern of SENSITIVE_PATTERNS) {
                redacted = redacted.replace(pattern, "[REDACTED]");
            }
            if (redacted !== input.toolResult) {
                return { modifiedResult: redacted };
            }
        }
        return null; // Pass through unchanged
    },
}
```

---

## MCP Server Integration

Connect to MCP servers for pre-built tool capabilities:

### Local Stdio Server

```typescript
const session = await client.createSession({
    mcpServers: {
        filesystem: {
            type: "local",
            command: "npx",
            args: ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
            tools: ["*"],
            env: { DEBUG: "true" },
            cwd: "./servers",
            timeout: 30000,
        },
    },
});
```

### Remote HTTP Server

```typescript
const session = await client.createSession({
    mcpServers: {
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
            headers: { Authorization: "Bearer ${TOKEN}" },
            tools: ["*"],
        },
    },
});
```

### MCP Debugging

```bash
# Test MCP server independently
npx @modelcontextprotocol/inspector /path/to/your/mcp-server
```

**Common issues:**

- Tools not appearing → Set `tools: ["*"]` and verify server responds to `tools/list`
- Server not starting → Use absolute command paths, check `cwd`
- Stdout pollution → Debug output must go to stderr, not stdout

---

## Authentication

### Methods (Priority Order)

1. **Explicit token** — `githubToken` in constructor
2. **HMAC key** — `CAPI_HMAC_KEY` or `COPILOT_HMAC_KEY` env vars
3. **Direct API token** — `GITHUB_COPILOT_API_TOKEN` with `COPILOT_API_URL`
4. **Environment variables** — `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN`
5. **Stored OAuth** — From `copilot auth login`
6. **GitHub CLI** — `gh auth` credentials

### OAuth GitHub App

```typescript
const client = new CopilotClient({
    githubToken: userAccessToken,    // gho_ or ghu_ token from OAuth flow
    useLoggedInUser: false,          // Don't use stored CLI credentials
});
```

**Supported:** `gho_` (OAuth), `ghu_` (GitHub App), `github_pat_` (fine-grained PAT)
**Not supported:** `ghp_` (classic PAT — deprecated)

---

## BYOK (Bring Your Own Key)

Use your own API keys — no Copilot subscription required:

### Provider Configurations

**OpenAI:**

```typescript
provider: { type: "openai", baseUrl: "https://api.openai.com/v1", apiKey: process.env.OPENAI_API_KEY }
```

**Azure AI Foundry:**

```typescript
provider: {
    type: "openai",
    baseUrl: "https://your-resource.openai.azure.com/openai/v1/",
    apiKey: process.env.FOUNDRY_API_KEY,
    wireApi: "responses",  // Use "responses" for GPT-5 series
}
```

**Azure OpenAI (native):**

```typescript
provider: {
    type: "azure",
    baseUrl: "https://my-resource.openai.azure.com",
    apiKey: process.env.AZURE_OPENAI_KEY,
    azure: { apiVersion: "2024-10-21" },
}
```

**Anthropic:**

```typescript
provider: { type: "anthropic", baseUrl: "https://api.anthropic.com", apiKey: process.env.ANTHROPIC_API_KEY }
```

**Ollama (local):**

```typescript
provider: { type: "openai", baseUrl: "http://localhost:11434/v1" }
```

### BYOK Limitations

- **Static credentials only** — no native Entra ID, OIDC, or managed identity support
- **No auto-refresh** — expired tokens require creating a new session
- **Keys not persisted** — must re-provide `provider` config on session resume

---

## Session Persistence

Resume sessions across restarts by providing your own session ID:

```typescript
// Create with explicit ID
const session = await client.createSession({
    sessionId: "user-123-task-456",
    model: "gpt-4.1",
});

// Resume later (even from a different client instance)
const resumed = await client.resumeSession("user-123-task-456");
await resumed.sendAndWait({ prompt: "What did we discuss?" });
```

### Session ID Best Practices

| Pattern | Example | Use Case |
|---------|---------|----------|
| `user-{userId}-{taskId}` | `user-alice-pr-review-42` | Multi-user apps |
| `tenant-{tenantId}-{workflow}` | `tenant-acme-onboarding` | Multi-tenant SaaS |
| `{userId}-{taskType}-{timestamp}` | `alice-deploy-1706932800` | Time-based cleanup |

### What Gets Persisted

| Data | Persisted? | Notes |
|------|------------|-------|
| Conversation history | ✅ Yes | Full message thread |
| Tool call results | ✅ Yes | Cached for context |
| Agent planning state | ✅ Yes | `plan.md` file |
| Provider/API keys | ❌ No | Must re-provide on resume |
| In-memory tool state | ❌ No | Design tools to be stateless |

### Infinite Sessions

For long-running workflows that may exceed context limits:

```typescript
const session = await client.createSession({
    infiniteSessions: {
        enabled: true,
        backgroundCompactionThreshold: 0.80,  // Start background compaction at 80%
        bufferExhaustionThreshold: 0.95,      // Block and compact at 95%
    },
});
```

---

## Deployment Patterns

### Local CLI (Default)

```typescript
const client = new CopilotClient(); // Auto-manages CLI process
```

### External CLI Server (Backend Services)

```bash
copilot --headless --port 4321
```

```typescript
const client = new CopilotClient({ cliUrl: "localhost:4321" });
```

### Docker Compose

```yaml
services:
  copilot-cli:
    image: ghcr.io/github/copilot-cli:latest
    command: ["--headless", "--port", "4321"]
    environment:
      - COPILOT_GITHUB_TOKEN=${COPILOT_GITHUB_TOKEN}
    volumes:
      - session-data:/root/.copilot/session-state
  api:
    build: .
    environment:
      - CLI_URL=copilot-cli:4321
    depends_on: [copilot-cli]
volumes:
  session-data:
```

### Session Isolation Patterns

| Pattern | Isolation | Resources | Best For |
|---------|-----------|-----------|----------|
| **CLI per user** | Complete | High | Multi-tenant SaaS, compliance |
| **Shared CLI + session IDs** | Logical | Low | Internal tools |
| **Shared sessions** | None | Low | Team collaboration (requires locking) |

### Production Checklist

- Session cleanup: periodic deletion of expired sessions
- Health checks: ping CLI server, restart if unresponsive
- Persistent storage: mount `~/.copilot/session-state/` for containers
- Secret management: use Vault/K8s Secrets for tokens
- Session locking: Redis or similar for shared session access
- Graceful shutdown: drain active sessions before stopping CLI

---

## Configuration Reference

### Client Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cliPath` | string | Auto-detected | Path to Copilot CLI executable |
| `cliUrl` | string | — | URL of external CLI server |
| `githubToken` | string | — | GitHub token for auth |
| `useLoggedInUser` | boolean | `true` | Use stored CLI credentials |
| `logLevel` | string | `"none"` | `"none"` \| `"error"` \| `"warning"` \| `"info"` \| `"debug"` |
| `autoRestart` | boolean | `true` | Auto-restart CLI on crash |

### Session Configuration

| Option | Type | Description |
|--------|------|-------------|
| `model` | string | Model to use (e.g., `"gpt-4.1"`, `"claude-sonnet-4"`) |
| `sessionId` | string | Custom ID for resumable sessions |
| `streaming` | boolean | Enable streaming responses |
| `tools` | Tool[] | Custom tools |
| `mcpServers` | object | MCP server configurations |
| `hooks` | object | Session hooks |
| `provider` | object | BYOK provider config |
| `customAgents` | object[] | Custom agent definitions |
| `systemMessage` | object | System message override |
| `skillDirectories` | string[] | Directories to load skills from |
| `infiniteSessions` | object | Auto-compaction config |

---

## API Summary

| Language | Client | Session Create | Send | Resume | Stop |
|----------|--------|----------------|------|--------|------|
| Node.js | `new CopilotClient()` | `client.createSession()` | `session.sendAndWait()` | `client.resumeSession()` | `client.stop()` |
| Python | `CopilotClient()` | `client.create_session()` | `session.send_and_wait()` | `client.resume_session()` | `client.stop()` |
| Go | `copilot.NewClient(nil)` | `client.CreateSession()` | `session.SendAndWait()` | `client.ResumeSession()` | `client.Stop()` |
| .NET | `new CopilotClient()` | `client.CreateSessionAsync()` | `session.SendAndWaitAsync()` | `client.ResumeSessionAsync()` | `client.DisposeAsync()` |

---

## References

- [GitHub Copilot SDK](https://github.com/github/copilot-sdk)
- [Copilot CLI Installation](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
