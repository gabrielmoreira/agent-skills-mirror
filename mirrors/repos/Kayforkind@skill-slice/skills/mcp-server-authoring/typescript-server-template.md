# TypeScript MCP Server Template

Production patterns for `@modelcontextprotocol/sdk` (TypeScript). Pair with `reference.md` for protocol semantics and `security-checklist.md` before shipping.

## 1. Project layout

```
my-mcp-server/
├── src/
│   ├── index.ts          # entry: transport binding ONLY
│   ├── server.ts         # buildServer(): transport-agnostic registrations
│   ├── tools/            # one file per tool (handler + schema)
│   │   └── searchOrders.ts
│   └── lib/              # domain clients, config, redaction
├── test/
│   └── server.test.ts    # in-memory client<->server tests
├── package.json
├── tsconfig.json
└── README.md             # includes install snippet for hosts
```

Keep `index.ts` trivially thin — everything testable lives behind `buildServer()`.

## 2. package.json / tsconfig.json

```jsonc
// package.json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": { "my-mcp-server": "dist/index.js" },     // enables npx my-mcp-server
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts",
    "test": "vitest run",
    "inspect": "npx @modelcontextprotocol/inspector node dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.x",           // pin the current 1.x at authoring time
    "zod": "^3.x"
  },
  "devDependencies": { "typescript": "^5", "tsx": "^4", "vitest": "^2" },
  "engines": { "node": ">=18" }
}
```

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022", "module": "Node16", "moduleResolution": "Node16",
    "outDir": "dist", "rootDir": "src",
    "strict": true, "declaration": false, "sourceMap": true,
    "esModuleInterop": true, "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

For `npx` execution, `dist/index.js` needs a shebang — put `#!/usr/bin/env node` as line 1 of `src/index.ts` (tsc preserves it).

## 3. Core server (`src/server.ts`)

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function buildServer(): McpServer {
  const server = new McpServer(
    { name: "my-mcp-server", version: "1.0.0" },
    {
      // Injected as system-prompt context by many hosts. Short + imperative.
      instructions:
        "Order-management tools. Prefer search_orders to locate ids, then get_order for detail. All times UTC.",
    }
  );

  // ---- TOOL: read-only, paginated -------------------------------------
  server.registerTool(
    "search_orders",
    {
      title: "Search orders",
      description:
        "Search orders by free text and optional status. Returns at most 20 summaries per page; " +
        "pass the returned cursor to page. Use get_order for full line-item detail. Read-only.",
      inputSchema: {
        query: z.string().min(1).max(200).describe("Free-text match on customer name or order id."),
        status: z.enum(["open", "shipped", "cancelled"]).optional()
          .describe("Filter by lifecycle status."),
        cursor: z.string().optional().describe("Opaque cursor from a previous page."),
      },
      annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
    },
    async ({ query, status, cursor }) => {
      const page = await ordersClient.search({ query, status, cursor, limit: 20 });
      const lines = page.items.map((o) => `${o.id}  ${o.customer}  ${o.status}  ${o.totalUsd}`);
      const text =
        lines.length === 0
          ? `No orders matched "${query}".`
          : lines.join("\n") + (page.nextCursor ? `\n\n[more results: cursor=${page.nextCursor}]` : "");
      return { content: [{ type: "text", text }] };
    }
  );

  // ---- TOOL: mutating + structured output -----------------------------
  const RefundResult = z.object({
    refundId: z.string(),
    orderId: z.string(),
    amountUsd: z.number(),
    status: z.enum(["pending", "completed"]),
  });

  server.registerTool(
    "refund_order",
    {
      title: "Refund order",
      description:
        "Issue a full or partial refund for an order. Irreversible once completed. " +
        "Requires an idempotency_key so retries are safe: reuse the same key to retry, " +
        "a new key to issue a second refund.",
      inputSchema: {
        order_id: z.string().regex(/^ORD-\d+$/).describe("Order id, e.g. ORD-1042."),
        amount_usd: z.number().positive().optional()
          .describe("Partial refund amount. Omit for full refund."),
        idempotency_key: z.string().uuid().describe("Client-generated UUID; same key = same refund."),
      },
      outputSchema: RefundResult.shape,
      annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: true },
    },
    async ({ order_id, amount_usd, idempotency_key }) => {
      const r = await ordersClient.refund(order_id, { amount_usd, idempotency_key });
      const structured = RefundResult.parse(r); // assert outputSchema truthfulness
      return {
        content: [{ type: "text", text: JSON.stringify(structured) }], // back-compat mirror
        structuredContent: structured,
      };
    }
  );

  // ---- RESOURCE TEMPLATE ----------------------------------------------
  server.registerResource(
    "order",
    new ResourceTemplate("orders://{orderId}", { list: undefined }),
    { title: "Order record", description: "Full JSON record for one order.", mimeType: "application/json" },
    async (uri, { orderId }) => ({
      contents: [{ uri: uri.href, mimeType: "application/json",
                   text: JSON.stringify(await ordersClient.get(String(orderId)), null, 2) }],
    })
  );

  // ---- PROMPT ----------------------------------------------------------
  server.registerPrompt(
    "triage_order_issue",
    {
      title: "Triage an order issue",
      description: "Structured workflow for investigating a problem order.",
      argsSchema: { order_id: z.string().describe("Order to investigate.") },
    },
    ({ order_id }) => ({
      messages: [{ role: "user", content: { type: "text",
        text: `Investigate order ${order_id}: fetch it with get_order, check refund history, summarize root cause and next action.` } }],
    })
  );

  return server;
}
```

Notes:
- `inputSchema` takes a **zod raw shape** (`{ key: z... }`); the SDK derives JSON Schema, validates inbound args, and types your handler — one source of truth.
- Validate mutating-tool outputs against your own `outputSchema` (as above) so drift fails in tests, not in hosts.

## 4. Error handling pattern

```typescript
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";

// Wrap every handler body: execution failures -> isError result the model can act on.
async function guarded<T extends { content: unknown[] }>(
  fn: () => Promise<T>
): Promise<T | { content: [{ type: "text"; text: string }]; isError: true }> {
  try {
    return await fn();
  } catch (err) {
    if (err instanceof UpstreamRateLimit) {
      return { content: [{ type: "text",
        text: `Rate-limited by upstream API. Retry after ${err.retryAt.toISOString()}, or narrow the query.` }],
        isError: true };
    }
    if (err instanceof NotFound) {
      return { content: [{ type: "text",
        text: `${err.what} not found. Verify the id via search_orders before retrying.` }],
        isError: true };
    }
    console.error("unhandled tool error:", err);                    // detail -> stderr only
    return { content: [{ type: "text",
      text: "Internal error executing the tool. The failure was logged; do not retry with identical input." }],
      isError: true };
  }
}
// Reserve `throw new McpError(ErrorCode.InvalidParams, "...")` for genuine protocol violations
// the SDK's schema validation didn't already catch.
```

## 5. Logging without breaking stdio

```typescript
// NEVER console.log in a stdio server. Two legal sinks:

// 1) stderr — always safe, host log files:
console.error(JSON.stringify({ level: "info", msg: "search", q: query.slice(0, 40) }));

// 2) MCP logging notifications — visible in host UIs; respects logging/setLevel:
await server.server.sendLoggingMessage({
  level: "info",
  logger: "orders",
  data: { event: "refund_issued", orderId },
});
```

stdout-cleanliness smoke test (run in CI):

```bash
printf '' | node dist/index.js > out.json 2> err.log &  sleep 2; kill %1
node -e "for (const l of require('fs').readFileSync('out.json','utf8').split('\n').filter(Boolean)) JSON.parse(l)"
```

If any dependency prints a banner on import, this catches it before a user does.

## 6. Entry point A — stdio (`src/index.ts`)

```typescript
#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { buildServer } from "./server.js";

async function main() {
  const server = buildServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("my-mcp-server ready (stdio)");   // stderr, never stdout
}

main().catch((err) => { console.error("fatal:", err); process.exit(1); });
```

Config is env-only for stdio: read `process.env.ORDERS_API_KEY` lazily (first tool call), fail with an `isError` message that names the missing variable — not a startup crash the user can't diagnose.

## 7. Entry point B — Streamable HTTP

```typescript
import express from "express";
import { randomUUID } from "node:crypto";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { buildServer } from "./server.js";

const app = express();
app.use(express.json());
const transports: Record<string, StreamableHTTPServerTransport> = {};

app.post("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  let transport = sessionId ? transports[sessionId] : undefined;

  if (!transport && isInitializeRequest(req.body)) {
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),           // crypto-random, per spec
      onsessioninitialized: (sid) => { transports[sid] = transport!; },
      enableDnsRebindingProtection: true,               // Origin/Host validation
      allowedHosts: ["127.0.0.1:3000", "localhost:3000"],
    });
    transport.onclose = () => { if (transport!.sessionId) delete transports[transport!.sessionId]; };
    await buildServer().connect(transport);
  } else if (!transport) {
    res.status(400).json({ jsonrpc: "2.0", id: null,
      error: { code: -32000, message: "Bad Request: no valid session" } });
    return;
  }
  await transport.handleRequest(req, res, req.body);
});

// GET = server->client notification stream; DELETE = session teardown
const sessionHandler = async (req: express.Request, res: express.Response) => {
  const t = transports[req.headers["mcp-session-id"] as string];
  if (!t) { res.status(400).send("Invalid session"); return; }
  await t.handleRequest(req, res);
};
app.get("/mcp", sessionHandler);
app.delete("/mcp", sessionHandler);

app.listen(3000, "127.0.0.1");   // never 0.0.0.0 without auth + TLS
```

Add bearer/OAuth validation middleware before `handleRequest` for anything beyond localhost (`security-checklist.md §HTTP`).

## 8. Progress and cancellation

The third handler argument (`extra`) carries the request plumbing:

```typescript
server.registerTool("export_report", { /* descriptor */ inputSchema: { month: z.string() } },
  async ({ month }, extra) => {
    const rows = await db.count(month);
    for (let i = 0; i < rows; i += 500) {
      if (extra.signal.aborted) throw new Error("cancelled");     // honor notifications/cancelled
      await exportChunk(month, i, 500);
      if (extra._meta?.progressToken !== undefined) {
        await extra.sendNotification({ method: "notifications/progress",
          params: { progressToken: extra._meta.progressToken,
                    progress: i + 500, total: rows, message: `exported ${i + 500}/${rows}` } });
      }
    }
    return { content: [{ type: "resource_link", uri: `file:///exports/${month}.csv`,
                         name: `${month}.csv`, mimeType: "text/csv" },
                       { type: "text", text: `Export complete: ${rows} rows.` }] };
  });
```

If total wall time can exceed ~60s, switch to the job pattern (`start_export` → `get_export_status`) — see `reference.md §5`.

## 9. Testing

### In-memory integration tests (no process spawning)

```typescript
import { describe, it, expect } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { buildServer } from "../src/server.js";

async function connected() {
  const [clientT, serverT] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: "test", version: "0.0.0" });
  await Promise.all([buildServer().connect(serverT), client.connect(clientT)]);
  return client;
}

describe("search_orders", () => {
  it("lists and validates descriptors", async () => {
    const client = await connected();
    const { tools } = await client.listTools();
    for (const t of tools) {
      expect(t.name).toMatch(/^[a-zA-Z0-9_-]{1,64}$/);
      expect(t.description!.length).toBeGreaterThan(30);
    }
  });

  it("returns isError with remedy on bad id", async () => {
    const client = await connected();
    const res = await client.callTool({ name: "refund_order",
      arguments: { order_id: "ORD-999999", idempotency_key: crypto.randomUUID() } });
    expect(res.isError).toBe(true);
    expect((res.content as any)[0].text).toMatch(/search_orders/);   // actionable
  });
});
```

### Interactive

```bash
npm run build && npx @modelcontextprotocol/inspector node dist/index.js
```

Exercise every tool: happy path, schema-invalid input (expect protocol error), semantically-invalid input (expect `isError`), pagination cursor round-trip.

## 10. Packaging & host install

```bash
npm run build          # verify dist/index.js has the shebang
npm pack               # inspect the tarball: dist only, no src/secrets
npm publish            # or keep private and install from absolute path
```

Cursor `mcp.json` (`%USERPROFILE%\.cursor\mcp.json` global, or `<project>\.cursor\mcp.json`):

```jsonc
{
  "mcpServers": {
    // Preferred on Windows: absolute node + absolute script (no PATH/npx roulette)
    "my-mcp-server": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["C:\\Users\\user\\srv\\my-mcp-server\\dist\\index.js"],
      "env": { "ORDERS_API_KEY": "…" }
    },
    // npx form (needs cmd wrapper on Windows if direct spawn fails):
    "my-mcp-server-npx": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "my-mcp-server"],
      "env": { "ORDERS_API_KEY": "…" }
    }
  }
}
```

Full Cursor wiring, reload behavior, and troubleshooting → `mcp-cursor-integration` skill.
