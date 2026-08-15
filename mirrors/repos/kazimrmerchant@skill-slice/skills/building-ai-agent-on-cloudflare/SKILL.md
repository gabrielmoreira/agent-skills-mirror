---
name: building-ai-agent-on-cloudflare
description: "Builds stateful Cloudflare Agents SDK workers: Agent/AIChatAgent, Durable Object setState/SQL, WebSockets, this.schedule(), Workers AI, and wrangler.toml class migrations. Use when the user wants a Cloudflare chat or stateful edge agent, the Agents SDK, or WebSocket AI on Workers. Not for generic Wrangler CLI, KV/R2/D1, or Pages (wrangler). Never trust stale SDK APIs; fetch developers.cloudflare.com/agents first."
version: 1.0.1
---

# Building Cloudflare Agents

Your knowledge of the Agents SDK may be outdated. **Prefer retrieval over pre-training** for any agent-building task. Always fetch from the sources below before writing agent code.

## Retrieval Sources

| Source | How to retrieve | Use for |
|--------|-----------------|---------|
| Agents SDK docs | `https://github.com/cloudflare/agents/tree/main/docs` | SDK API, state, routing, scheduling |
| Cloudflare Agents docs | `https://developers.cloudflare.com/agents/` | Platform integration, deployment |
| Workers docs | Search tool or `https://developers.cloudflare.com/workers/` | Runtime APIs, bindings, config |

## When to Use

- User wants to build an AI agent or chatbot on Cloudflare.
- User needs stateful, real-time AI interactions.
- User asks about the Cloudflare Agents SDK.
- User wants scheduled tasks or background AI work.
- User needs WebSocket-based AI communication.
- User mentions "Agents SDK", "Durable Objects agent", or "edge AI agent".

## Prerequisites

- Cloudflare account with Workers enabled.
- Node.js 18+ and npm/pnpm/yarn installed.
- Wrangler CLI installed globally: `npm install -g wrangler`.
- Windows host is primary — use PowerShell for all local commands. Paths use Windows conventions (`~`).

## Procedure

### 1. Scaffold a New Agent Project

```powershell
npm create cloudflare@latest -- my-agent --template=cloudflare/agents-starter
cd my-agent
npm start
```

Agent runs locally at `http://localhost:8787`.

### 2. Define the Agent Class

Create `src/agent.ts` with a class extending `Agent<Env, State>`:

```typescript
import { Agent, Connection } from "agents";

interface Env {
  AI: Ai;  // Workers AI binding
}

interface State {
  messages: Array<{ role: string; content: string }>;
  preferences: Record<string, string>;
}

export class MyAgent extends Agent<Env, State> {
  // Initial state for new instances
  initialState: State = {
    messages: [],
    preferences: {},
  };

  // Called when agent starts or resumes
  async onStart() {
    console.log("Agent started with state:", this.state);
  }

  // Handle WebSocket connections
  async onConnect(connection: Connection) {
    connection.send(JSON.stringify({
      type: "welcome",
      history: this.state.messages,
    }));
  }

  // Handle incoming messages
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      await this.handleChat(connection, data.content);
    }
  }

  // Handle disconnections
  async onClose(connection: Connection) {
    console.log("Client disconnected");
  }

  // React to state changes
  onStateUpdate(state: State, source: string) {
    console.log("State updated by:", source);
  }

  private async handleChat(connection: Connection, userMessage: string) {
    const messages = [
      ...this.state.messages,
      { role: "user", content: userMessage },
    ];

    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages,
    });

    this.setState({
      ...this.state,
      messages: [
        ...messages,
        { role: "assistant", content: response.response },
      ],
    });

    connection.send(JSON.stringify({
      type: "response",
      content: response.response,
    }));
  }
}
```

### 3. Configure the Entry Point

Create `src/index.ts`:

```typescript
import { routeAgentRequest } from "agents";
import { MyAgent } from "./agent";

export default {
  async fetch(request: Request, env: Env) {
    return (
      (await routeAgentRequest(request, env)) ||
      new Response("Not found", { status: 404 })
    );
  },
};

export { MyAgent };
```

Clients connect via: `wss://my-agent.workers.dev/agents/MyAgent/session-id`

### 4. Configure Wrangler

Create or edit `wrangler.toml`:

```toml
name = "my-agent"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[ai]
binding = "AI"

[durable_objects]
bindings = [{ name = "AGENT", class_name = "MyAgent" }]

[[migrations]]
tag = "v1"
new_classes = ["MyAgent"]
```

### 5. Manage State

**Reading state** — current state is always available via `this.state`:

```typescript
const currentMessages = this.state.messages;
const userPrefs = this.state.preferences;
```

**Updating state** — `setState` persists AND syncs to all connected clients:

```typescript
this.setState({
  ...this.state,
  messages: [...this.state.messages, newMessage],
});

// Partial updates work too
this.setState({
  preferences: { ...this.state.preferences, theme: "dark" },
});
```

**SQL Storage** — for complex queries, use the embedded SQLite database:

```typescript
// Create tables
await this.sql`
  CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`;

// Insert
await this.sql`
  INSERT INTO documents (title, content)
  VALUES (${title}, ${content})
`;

// Query
const docs = await this.sql`
  SELECT * FROM documents WHERE title LIKE ${`%${search}%`}
`;
```

### 6. Add Scheduled Tasks

Agents can schedule future work using `this.schedule()`:

```typescript
async onMessage(connection: Connection, message: string) {
  const data = JSON.parse(message);

  if (data.type === "schedule_reminder") {
    const { id } = await this.schedule(3600, "sendReminder", {
      message: data.reminderText,
      userId: data.userId,
    });

    connection.send(JSON.stringify({ type: "scheduled", taskId: id }));
  }
}

// Called when scheduled task fires
async sendReminder(data: { message: string; userId: string }) {
  console.log(`Reminder for ${data.userId}: ${data.message}`);

  this.setState({
    ...this.state,
    lastReminder: new Date().toISOString(),
  });
}
```

**Schedule options:**

```typescript
// Delay in seconds
await this.schedule(60, "taskMethod", { data });

// Specific date
await this.schedule(new Date("2025-01-01T00:00:00Z"), "taskMethod", { data });

// Cron expression (recurring)
await this.schedule("0 9 * * *", "dailyTask", {});       // 9 AM daily
await this.schedule("*/5 * * * *", "everyFiveMinutes", {}); // Every 5 min

// Manage schedules
const schedules = await this.getSchedules();
await this.cancelSchedule(taskId);
```

### 7. Build a Chat Agent with AIChatAgent

For chat-focused agents, extend `AIChatAgent` instead of `Agent`:

```typescript
import { AIChatAgent } from "agents/ai-chat-agent";

export class ChatBot extends AIChatAgent<Env> {
  async onChatMessage(message: string) {
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        ...this.messages,  // Automatic history management
        { role: "user", content: message },
      ],
      stream: true,
    });

    return response;
  }
}
```

Features included with `AIChatAgent`:
- Automatic message history.
- Resumable streaming (survives disconnects).
- Built-in `saveMessages()` for persistence.

### 8. Integrate Client-Side

**React hook:**

```tsx
import { useAgent } from "agents/react";

function Chat() {
  const { state, send, connected } = useAgent({
    agent: "my-agent",
    name: userId,  // Agent instance ID
  });

  const sendMessage = (text: string) => {
    send(JSON.stringify({ type: "chat", content: text }));
  };

  return (
    <div>
      {state.messages.map((msg, i) => (
        <div key={i}>{msg.role}: {msg.content}</div>
      ))}
      <input onKeyDown={(e) => e.key === "Enter" && sendMessage(e.target.value)} />
    </div>
  );
}
```

**Vanilla JavaScript:**

```javascript
const ws = new WebSocket("wss://my-agent.workers.dev/agents/MyAgent/user123");

ws.onopen = () => {
  console.log("Connected to agent");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};

ws.send(JSON.stringify({ type: "chat", content: "Hello!" }));
```

### 9. Deploy

```powershell
# Deploy to Cloudflare Workers
npx wrangler deploy

# View live logs
wrangler tail

# Test endpoint
curl https://my-agent.workers.dev/agents/MyAgent/test-user
```

## Advanced Patterns

**When to load reference files:**

- **`references/agent-patterns.md`** — Load when the user asks for tool calling, function execution, multi-agent orchestration, RAG (Retrieval Augmented Generation), or human-in-the-loop workflows.
- **`references/state-patterns.md`** — Load when the user needs advanced state management strategies beyond basic `setState` or SQL.
- **`references/examples.md`** — Load when the user wants official templates or production-ready examples to start from.
- **`references/troubleshooting.md`** — Load when the user encounters errors during development, deployment, or runtime.

## Pitfalls

- **Outdated SDK knowledge**: The Agents SDK evolves rapidly. Always retrieve from the GitHub docs or `developers.cloudflare.com/agents/` before writing code. Do not rely on pre-trained knowledge alone.
- **Missing Durable Object migration**: If you add a new Agent class, you must add a `[[migrations]]` entry with `new_classes`. Without it, the Worker will fail to deploy or route correctly.
- **State not syncing**: `setState` must be called with a new object (not a mutation of `this.state`). Directly mutating `this.state` will NOT persist or sync to clients.
- **SQL injection risk**: Always use tagged template literals (`this.sql\`...\``) with parameter placeholders. Never interpolate raw user input into SQL strings.
- **Schedule method name mismatch**: The method name passed to `this.schedule()` (e.g., `"sendReminder"`) must exactly match a method on the Agent class. Typos cause silent failures.
- **Model availability**: `@cf/meta/llama-3-8b-instruct` is used in examples. Verify model availability in the user's Cloudflare account region before deploying. Check Workers AI model catalog for current models.
- **Windows path issues**: On Windows PowerShell, use backslash paths for local files. Wrangler and Node commands work the same, but file paths in scripts should use Windows conventions.
- **`routeAgentRequest` not exported**: Ensure `MyAgent` is re-exported from `src/index.ts` (`export { MyAgent }`). Without this export, the Durable Object binding will not resolve.
- **Port conflicts**: Local dev server defaults to `http://localhost:8787`. If that port is in use, `npm start` will fail. Check with `netstat -ano | findstr 8787` in PowerShell.

## Verification

1. **Verify local server is running:**

   ```powershell
   curl http://localhost:8787
   ```

   Expected: a response (not a connection error).

2. **Verify WebSocket connection:**

   ```powershell
   # Use a WebSocket client or browser console
   # Connect to: ws://localhost:8787/agents/MyAgent/test-session
   # Send: {"type":"chat","content":"Hello"}
   # Expect: {"type":"response","content":"..."}
   ```

3. **Verify deployment:**

   ```powershell
   npx wrangler deploy
   curl https://my-agent.workers.dev/agents/MyAgent/test-user
   ```

   Expected: successful deploy output and a non-404 response.

4. **Verify state persistence:**

   - Connect to an agent session, send messages, disconnect.
   - Reconnect to the same session ID.
   - Confirm `onConnect` sends back the full message history.

5. **Verify scheduled tasks:**

   ```typescript
   // In agent code, log when scheduled method fires
   console.log("Scheduled task fired");
   ```

   - Trigger a short-delay schedule (e.g., `this.schedule(5, "testTask", {})`).
   - Run `wrangler tail` and confirm the log appears after 5 seconds.

## References

- [references/examples.md](references/examples.md) — Official templates and production examples
- [references/agent-patterns.md](references/agent-patterns.md) — Advanced patterns: tool calling, multi-agent, RAG, human-in-the-loop
- [references/state-patterns.md](references/state-patterns.md) — State management strategies
- [references/troubleshooting.md](references/troubleshooting.md) — Error solutions and common issues
