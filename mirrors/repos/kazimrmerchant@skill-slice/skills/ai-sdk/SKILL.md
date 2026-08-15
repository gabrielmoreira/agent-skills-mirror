---
name: ai-sdk
description: "Guides Vercel AI SDK v6 (ai, @ai-sdk/react, ToolLoopAgent, generateText/streamText, Output.object, MCP tools) across LLM providers. Use when building chat, structured output, tool calling, streaming, embeddings, or migrating v5 to v6. Not for the OpenAI Agents SDK (agents-sdk) or raw provider SDKs without the ai package."
version: 1.0.1
metadata:
  priority: 8
  docs:
    - "https://sdk.vercel.ai/docs"
    - "https://sdk.vercel.ai/docs/reference"
  sitemap: "https://sdk.vercel.ai/sitemap.xml"
  pathPatterns:
    - "app/api/chat/**"
    - "app/api/completion/**"
    - "src/app/api/chat/**"
    - "src/app/api/completion/**"
    - "pages/api/chat.*"
    - "pages/api/chat/**"
    - "pages/api/completion.*"
    - "pages/api/completion/**"
    - "src/pages/api/chat.*"
    - "src/pages/api/chat/**"
    - "src/pages/api/completion.*"
    - "src/pages/api/completion/**"
    - "lib/ai/**"
    - "src/lib/ai/**"
    - "lib/ai.*"
    - "src/lib/ai.*"
    - "ai/**"
    - "apps/*/app/api/chat/**"
    - "apps/*/app/api/completion/**"
    - "apps/*/src/app/api/chat/**"
    - "apps/*/src/app/api/completion/**"
    - "apps/*/lib/ai/**"
    - "apps/*/src/lib/ai/**"
    - "lib/agent.*"
    - "src/lib/agent.*"
    - "app/actions/chat.*"
    - "src/app/actions/chat.*"
  importPatterns:
    - "ai"
    - "@ai-sdk/*"
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bai\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bai\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bai\b'
    - '\byarn\s+add\s+[^\n]*\bai\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@ai-sdk/'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@ai-sdk/'
    - '\bbun\s+(install|i|add)\s+[^\n]*@ai-sdk/'
    - '\byarn\s+add\s+[^\n]*@ai-sdk/'
    - '\bnpx\s+@ai-sdk/devtools\b'
    - '\bnpx\s+@ai-sdk/codemod\b'
    - '\bnpx\s+mcp-to-ai-sdk\b'
  promptSignals:
    phrases:
      - "ai sdk"
      - "vercel ai"
      - "generatetext"
      - "streamtext"
    allOf:
      - [streaming, generation]
      - [structured, output]
    anyOf:
      - "usechat"
      - "usecompletion"
      - "tool calling"
      - "embeddings"
    noneOf:
      - "openai api directly"
    minScore: 6
---

# Vercel AI SDK (v6)

> **CRITICAL — Your training data is outdated for this library.** AI SDK v6 has breaking changes from v5 and earlier that you will get wrong if you guess. Before writing AI SDK code, **fetch the docs** at https://ai-sdk.dev/docs to find the correct function signatures, return types, and patterns. Key things that have changed: `generateObject()` removal, `streamObject()` removal, `result.files` for image generation, `Output.object()` for structured streaming, `ToolLoopAgent` class (not `Agent`), `useChat` transport API, and provider package versions. Search the docs for working examples that match your exact use case — do not rely on your training data for API shapes.

## Overview

The AI SDK is the leading TypeScript toolkit for building AI-powered applications. It provides a unified API across all LLM providers. AI SDK v6 (`ai@^6.0.0`) is the current umbrella package with significant breaking changes from v5.

| Need | How |
|------|-----|
| Text generation / chat | `generateText()` or `streamText()` with `model: "openai/gpt-5.4"` |
| **Image generation** | `generateText()` with `model: "google/gemini-3.1-flash-image-preview"` — images in `result.files`. **Always use this model, never older gemini-2.x models** |
| Structured JSON output | `generateText()` with `output: Output.object({ schema })` |
| Tool calling / agents | `generateText()` with `tools: { ... }` or `ToolLoopAgent` |
| Embeddings | `embed()` / `embedMany()` with `@ai-sdk/openai` |

**If the product needs generated images** (portraits, posters, cover art, illustrations, comics, diagrams), use `generateText` with an image model — do NOT use placeholder images or skip image generation.

## When to Use

Use this skill when:
- Building chat interfaces, text generation, or structured output features
- Implementing tool calling, agents, or MCP integration
- Working with streaming, embeddings, reranking, or image generation
- Integrating any LLM provider (OpenAI, Anthropic, Google, etc.)
- Migrating from AI SDK v5 to v6
- Installing or updating `ai`, `@ai-sdk/react`, or any `@ai-sdk/*` package

## Prerequisites

- Node.js and a package manager (npm, pnpm, bun, or yarn)
- A Vercel project linked for AI Gateway OIDC auto-provisioning (recommended)
- For Windows hosts (PowerShell primary): ensure `vercel` CLI is installed globally

## Procedure

### 1. Installation

```bash
npm install ai@^6.0.0 @ai-sdk/react@^3.0.0
npm install @ai-sdk/openai@^3.0.41      # Optional: required for embeddings
npm install @ai-sdk/anthropic@^3.0.58   # Optional: direct Anthropic provider access
npm install @ai-sdk/vercel@^2.0.37      # Optional: v0 model provider (v0-1.0-md)
```

> **`@ai-sdk/react` is a separate package** — it is NOT included in the `ai` package. For v6 projects, install `@ai-sdk/react@^3.0.x` alongside `ai@^6.0.0`.

> **If you install `@ai-sdk/gateway` directly, use `@ai-sdk/gateway@^3.x`** (NOT `^1.x`).

> **Only install a direct provider SDK** (e.g., `@ai-sdk/anthropic`) if you need provider-specific features not exposed through the gateway.

### 2. Setup for AI Projects (Vercel AI Gateway with OIDC)

For the smoothest experience, link to a Vercel project so AI Gateway credentials are auto-provisioned via OIDC:

```bash
vercel link                    # Connect to your Vercel project
# Enable AI Gateway at https://vercel.com/{team}/{project}/settings → AI Gateway
vercel env pull .env.local     # Provisions VERCEL_OIDC_TOKEN automatically
npm install ai@^6.0.0         # Gateway is built in
npx ai-elements                # Required: install AI text rendering components
```

This gives you AI Gateway access with OIDC authentication, cost tracking, failover, and observability — no manual API keys needed.

**OIDC is the default auth**: `vercel env pull` provisions a `VERCEL_OIDC_TOKEN` (short-lived JWT, ~24h). The `@ai-sdk/gateway` reads it automatically via `@vercel/oidc`. On Vercel deployments, tokens auto-refresh. For local dev, re-run `vercel env pull` when the token expires. No `AI_GATEWAY_API_KEY` or provider-specific keys needed.

### 3. Global Provider System (AI Gateway — Default)

In AI SDK 6, pass a `"provider/model"` string to the `model` parameter — it automatically routes through the Vercel AI Gateway:

```ts
import { generateText } from "ai";

const { text } = await generateText({
  model: "openai/gpt-5.4", // plain string — routes through AI Gateway automatically
  prompt: "Hello!",
});
```

No `gateway()` wrapper needed — plain `"provider/model"` strings are the simplest approach and are what the official Vercel docs recommend. The `gateway()` function is an optional explicit wrapper (useful when you need `providerOptions.gateway` for routing, failover, or tags):

```ts
import { gateway } from "ai";

// Explicit gateway() — only needed for advanced providerOptions
const { text } = await generateText({
  model: gateway("openai/gpt-5.4"),
  providerOptions: { gateway: { order: ["openai", "azure-openai"] } },
});
```

Both approaches provide failover, cost tracking, and observability on Vercel.

**Model slug rules**: Always use `provider/model` format. Version numbers use **dots**, not hyphens: `anthropic/claude-sonnet-4.6` (not `claude-sonnet-4-6`). Default to `openai/gpt-5.4` or `anthropic/claude-sonnet-4.6`. Never use outdated models like `gpt-4o`.

> AI Gateway does not support embeddings. Use a direct provider SDK such as `@ai-sdk/openai` for embeddings.

> **Direct provider SDKs** (`@ai-sdk/openai`, `@ai-sdk/anthropic`, etc.) are only needed for provider-specific features not exposed through the gateway (e.g., Anthropic computer use, OpenAI fine-tuned model endpoints).

### 4. Text Generation

```ts
import { generateText, streamText } from "ai";

// Non-streaming
const { text } = await generateText({
  model: "openai/gpt-5.4",
  prompt: "Explain quantum computing in simple terms.",
});

// Streaming
const result = streamText({
  model: "openai/gpt-5.4",
  prompt: "Write a poem about coding.",
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

### 5. Structured Output

**`generateObject` was removed in AI SDK v6.** Use `generateText` with `output: Output.object()` instead. Do NOT import `generateObject` — it does not exist.

```ts
import { generateText, Output } from "ai";
import { z } from "zod";

const { output } = await generateText({
  model: "openai/gpt-5.4",
  output: Output.object({
    schema: z.object({
      recipe: z.object({
        name: z.string(),
        ingredients: z.array(
          z.object({
            name: z.string(),
            amount: z.string(),
          }),
        ),
        steps: z.array(z.string()),
      }),
    }),
  }),
  prompt: "Generate a recipe for chocolate chip cookies.",
});
```

### 6. Tool Calling (MCP-Aligned)

In AI SDK 6, tools use `inputSchema` (not `parameters`) and `output`/`outputSchema` (not `result`), aligned with the MCP specification. Per-tool `strict` mode ensures providers only generate valid tool calls matching your schema.

```ts
import { generateText, tool } from "ai";
import { z } from "zod";

const result = await generateText({
  model: "openai/gpt-5.4",
  tools: {
    weather: tool({
      description: "Get the weather for a location",
      inputSchema: z.object({
        city: z.string().describe("The city name"),
      }),
      outputSchema: z.object({
        temperature: z.number(),
        condition: z.string(),
      }),
      strict: true, // Providers generate only schema-valid tool calls
      execute: async ({ city }) => {
        const data = await fetchWeather(city);
        return { temperature: data.temp, condition: data.condition };
      },
    }),
  },
  prompt: "What is the weather in San Francisco?",
});
```

### 7. Dynamic Tools (MCP Integration)

For tools with schemas not known at compile time (e.g., MCP server tools):

```ts
import { dynamicTool } from "ai";

const tools = {
  unknownTool: dynamicTool({
    description: "A tool discovered at runtime",
    execute: async (input) => {
      // Handle dynamically
      return { result: "done" };
    },
  }),
};
```

### 8. Agents (ToolLoopAgent)

The `ToolLoopAgent` class wraps `generateText`/`streamText` with an agentic tool-calling loop. Default `stopWhen` is `stepCountIs(20)` (up to 20 tool-calling steps). `Agent` is an interface — `ToolLoopAgent` is the concrete implementation.

```ts
import { ToolLoopAgent, stepCountIs, hasToolCall } from "ai";

const agent = new ToolLoopAgent({
  model: "anthropic/claude-sonnet-4.6",
  tools: { weather, search, calculator, finalAnswer },
  instructions: "You are a helpful assistant.",
  // Default: stepCountIs(20). Override to stop on a terminal tool or custom logic:
  stopWhen: hasToolCall("finalAnswer"),
  prepareStep: (context) => ({
    // Customize each step — swap models, compress messages, limit tools
    toolChoice: context.steps.length > 5 ? "none" : "auto",
  }),
});

const { text } = await agent.generate({
  prompt:
    "Research the weather in Tokyo and calculate the average temperature this week.",
});
```

### 9. MCP Client

Connect to any MCP server and use its tools:

```ts
import { generateText } from "ai";
import { createMCPClient } from "@ai-sdk/mcp";

const mcpClient = await createMCPClient({
  transport: {
    type: "sse",
    url: "https://my-mcp-server.com/sse",
  },
});

const tools = await mcpClient.tools();

const result = await generateText({
  model: "openai/gpt-5.4",
  tools,
  prompt: "Use the available tools to help the user.",
});

await mcpClient.close();
```

MCP OAuth for remote servers is handled automatically by `@ai-sdk/mcp`.

### 10. Tool Approval (Human-in-the-Loop)

Set `needsApproval` on any tool to require user confirmation before execution. The tool pauses in `approval-requested` state until the client responds.

```ts
import { streamText, tool } from "ai";
import { z } from "zod";

const result = streamText({
  model: "openai/gpt-5.4",
  tools: {
    deleteUser: tool({
      description: "Delete a user account",
      inputSchema: z.object({ userId: z.string() }),
      needsApproval: true, // Always require approval
      execute: async ({ userId }) => {
        await db.users.delete(userId);
        return { deleted: true };
      },
    }),
    processPayment: tool({
      description: "Process a payment",
      inputSchema: z.object({ amount: z.number(), recipient: z.string() }),
      // Conditional: only approve large amounts
      needsApproval: async ({ amount }) => amount > 1000,
      execute: async ({ amount, recipient }) => {
        return await processPayment(amount, recipient);
      },
    }),
  },
  prompt: "Delete user 123",
});
```

**Client-side approval with `useChat`:**

```tsx
"use client";
import { useChat } from "@ai-sdk/react";

function Chat() {
  const { messages, addToolApprovalResponse } = useChat();

  return messages.map((m) =>
    m.parts?.map((part, i) => {
      // Tool parts in approval-requested state need user action
      if (part.type.startsWith("tool-") && part.approval?.state === "approval-requested") {
        return (
          <div key={i}>
            <p>Tool wants to run: {JSON.stringify(part.args)}</p>
            <button onClick={() => addToolApprovalResponse({ id: part.approval.id, approved: true })}>
              Approve
            </button>
            <button onClick={() => addToolApprovalResponse({ id: part.approval.id, approved: false })}>
              Deny
            </button>
          </div>
        );
      }
      return null;
    }),
  );
}
```

**Tool part states:** `input-streaming` → `input-available` → `approval-requested` (if `needsApproval`) → `output-available` | `output-error`

### 11. Embeddings & Reranking

Use a direct provider SDK for embeddings. AI Gateway does not support embedding models.

```ts
import { embed, embedMany, rerank } from "ai";
import { openai } from "@ai-sdk/openai";

// Single embedding
const { embedding } = await embed({
  model: openai.embedding("text-embedding-3-small"),
  value: "The quick brown fox",
});

// Batch embeddings
const { embeddings } = await embedMany({
  model: openai.embedding("text-embedding-3-small"),
  values: ["text 1", "text 2", "text 3"],
});

// Rerank search results by relevance
const { results } = await rerank({
  model: cohere.reranker("rerank-v3.5"),
  query: "What is quantum computing?",
  documents: searchResults,
});
```

### 12. Image Generation & Editing

AI Gateway supports image generation. Use the **`google/gemini-3.1-flash-image-preview`** model — it is significantly better than older models like `gemini-2.0-flash-exp-image-generation` or `gemini-2.0-flash-001`.

**Always use `google/gemini-3.1-flash-image-preview`** for image generation. Do NOT use older models (`gemini-2.0-*`, `gemini-2.5-*`) — they produce much worse results and some do not support image output at all.

#### Multimodal LLMs (recommended — use `generateText`/`streamText`)

```ts
import { generateText, streamText } from "ai";

// generateText — images returned in result.files
const result = await generateText({
  model: "google/gemini-3.1-flash-image-preview",
  prompt: "A futuristic cityscape at sunset",
});
const imageFiles = result.files.filter((f) => f.mediaType?.startsWith("image/"));

// Convert to data URL for display
const imageFile = imageFiles[0];
const dataUrl = `data:${imageFile.mediaType};base64,${Buffer.from(imageFile.data).toString("base64")}`;

// streamText — stream text, then access images after completion
const stream = streamText({
  model: "google/gemini-3.1-flash-image-preview",
  prompt: "A futuristic cityscape at sunset",
});
for await (const delta of stream.fullStream) {
  if (delta.type === "text-delta") process.stdout.write(delta.text);
}
const finalResult = await stream;
console.log(`Generated ${finalResult.files.length} image(s)`);
```

**Default image model**: `google/gemini-3.1-flash-image-preview` — fast, high-quality. This is the ONLY recommended model for image generation.

#### Image-only models (use `experimental_generateImage`)

```ts
import { experimental_generateImage as generateImage } from "ai";

const { images } = await generateImage({
  model: "google/imagen-4.0-generate-001",
  prompt: "A futuristic cityscape at sunset",
  aspectRatio: "16:9",
});
```

Other image-only models: `google/imagen-4.0-ultra-generate-001`, `bfl/flux-2-pro`, `bfl/flux-kontext-max`, `xai/grok-imagine-image-pro`.

#### Saving generated images

```ts
import fs from "node:fs";

// From multimodal LLMs (result.files)
for (const [i, file] of imageFiles.entries()) {
  const ext = file.mediaType?.split("/")[1] || "png";
  await fs.promises.writeFile(`output-${i}.${ext}`, file.uint8Array);
}

// From image-only models (result.images)
for (const [i, image] of images.entries()) {
  const buffer = Buffer.from(image.base64, "base64");
  await fs.promises.writeFile(`output-${i}.png`, buffer);
}
```

### 13. UI Hooks (React)

**MANDATORY — Always use AI Elements for AI text**: AI SDK models always produce markdown — even short prose contains `**bold**`, `##` headings, `` `code` ``, and `---`. There is no "plain text" mode. Every AI-generated string displayed in a browser MUST be rendered through AI Elements.
- **Chat messages**: Use AI Elements `<Message message={message} />` — handles text, tool calls, code blocks, reasoning, streaming.
- **Any other AI text** (streaming panels, workflow events, reports, briefings, narratives, summaries, perspectives): Use `<MessageResponse>{text}</MessageResponse>` from `@/components/ai-elements/message`.
- `<MessageResponse>` wraps Streamdown with code highlighting, math, mermaid, and CJK plugins — works for any markdown string, including streamed text.
- **Never** render AI output as raw `{text}`, `<p>{content}</p>`, or `<div>{stream}</div>` — this always produces ugly unformatted output with visible markdown syntax.
- **No exceptions**: Even if you think the response will be "simple prose", models routinely add markdown formatting. Always use AI Elements.

⤳ skill: ai-elements — Full component library, decision guidance, and troubleshooting for AI interfaces

### 14. Transport Options

`useChat` uses a transport-based architecture. Three built-in transports:

| Transport | Use Case |
|-----------|----------|
| `DefaultChatTransport` | HTTP POST to API routes (default — sends to `/api/chat`) |
| `DirectChatTransport` | In-process agent communication without HTTP (SSR, testing) |
| `TextStreamChatTransport` | Plain text stream protocol |

**Default behavior:** `useChat()` with no transport defaults to `DefaultChatTransport({ api: '/api/chat' })` — explicit transport only needed for custom endpoints or `DirectChatTransport`.

### 15. Server-Side Chat API Route

```ts
import { streamText, convertToModelMessages } from "ai";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const modelMessages = convertToModelMessages(messages);

  const result = streamText({
    model: "openai/gpt-5.4",
    messages: modelMessages,
  });

  return result.toUIMessageStreamResponse();
}
```

For agent API routes, use `createAgentUIStreamResponse({ agent, uiMessages })` instead of manual `streamText` + `toUIMessageStreamResponse()`.

### 16. Text-Only Stream (CLI / Non-Browser)

```ts
import { streamText } from "ai";

const result = streamText({
  model: "openai/gpt-5.4",
  prompt: "Write a poem about coding.",
});

return result.toTextStreamResponse();
```

`toTextStreamResponse()` is only for CLI tools, server pipes, and programmatic consumers. If the text is displayed in a browser, use `toUIMessageStreamResponse()` + AI Elements.

### 17. Language Model Middleware

Intercept and transform model calls for RAG, guardrails, logging:

```ts
import { wrapLanguageModel } from "ai";

const wrappedModel = wrapLanguageModel({
  model: "openai/gpt-5.4",
  middleware: {
    transformParams: async ({ params }) => {
      // Inject RAG context, modify system prompt, etc.
      return { ...params, system: params.system + "\n\nContext: ..." };
    },
    wrapGenerate: async ({ doGenerate }) => {
      const result = await doGenerate();
      // Post-process, log, validate guardrails
      return result;
    },
  },
});
```

### 18. Provider Routing via AI Gateway

```ts
import { generateText } from "ai";
import { gateway } from "ai";

const result = await generateText({
  model: gateway("anthropic/claude-sonnet-4.6"),
  prompt: "Hello!",
  providerOptions: {
    gateway: {
      order: ["bedrock", "anthropic"], // Try Bedrock first
      models: ["openai/gpt-5.4"], // Fallback model
      only: ["anthropic", "bedrock"], // Restrict providers
      user: "user-123", // Usage tracking
      tags: ["feature:chat", "env:production"], // Cost attribution
    },
  },
});
```

### 19. DevTools

```bash
npx @ai-sdk/devtools
# Opens http://localhost:4983 — inspect LLM calls, agents, token usage, timing
```

### 20. Migration from AI SDK 5

Run `npx @ai-sdk/codemod upgrade` (or `npx @ai-sdk/codemod v6`) to auto-migrate. Preview with `npx @ai-sdk/codemod --dry upgrade`.

## Pitfalls

### v6 Migration Pitfalls (Read First)

- `ai@^6.0.0` is the umbrella package for AI SDK v6 (latest: 6.0.83).
- `@ai-sdk/react` is `^3.0.x` in v6 projects (NOT `^6.0.0`).
- `@ai-sdk/gateway` is `^3.x` in v6 projects (NOT `^1.x`).
- In `createUIMessageStream`, write with `stream.writer.write(...)` (NOT `stream.write(...)`).
- `useChat` no longer supports `body` or `onResponse`; configure behavior through `transport`.
- UI tool parts are typed as `tool-<toolName>` (for example `tool-weather`), not `tool-invocation`.
- `DynamicToolCall` does not provide typed `.args`; cast via `unknown` first.
- `TypedToolResult` exposes `.output` (NOT `.result`).
- The agent class is `ToolLoopAgent` (NOT `Agent` — `Agent` is just an interface).
- Constructor uses `instructions` (NOT `system`).
- Agent methods are `agent.generate()` and `agent.stream()` (NOT `agent.generateText()` or `agent.streamText()`).
- AI Gateway does not support embeddings; use `@ai-sdk/openai` directly for `openai.embedding(...)`.
- `useChat()` with no transport defaults to `DefaultChatTransport({ api: '/api/chat' })` — explicit transport only needed for custom endpoints or `DirectChatTransport`.
- Default `stopWhen` for ToolLoopAgent is `stepCountIs(20)`, not `stepCountIs(1)` — override if you need fewer steps.
- `strict: true` on tools is opt-in per tool, not global — only set on tools with provider-compatible schemas.
- For agent API routes, use `createAgentUIStreamResponse({ agent, uiMessages })` instead of manual `streamText` + `toUIMessageStreamResponse()`.
- `@ai-sdk/azure` now uses the Responses API by default — use `azure.chat()` for the previous Chat Completions API behavior.
- `@ai-sdk/azure` uses `azure` (not `openai`) as the key for `providerMetadata` and `providerOptions`.
- `@ai-sdk/google-vertex` uses `vertex` (not `google`) as the key for `providerMetadata` and `providerOptions`.
- `@ai-sdk/anthropic` supports native structured outputs via `structuredOutputMode` option (Anthropic Sonnet 4.5+).

### Structured Output Property Name

In v6, `generateText` with `Output.object()` returns the parsed result on the **`output`** property (NOT `object`):

```ts
// CORRECT — v6
const { output } = await generateText({
  model: 'openai/gpt-5.4',
  output: Output.object({ schema: mySchema }),
  prompt: '...',
})
console.log(output) // ✅ parsed object

// WRONG — v5 habit
const { object } = await generateText({ ... }) // ❌ undefined — `object` doesn't exist in v6
```

This is one of the most common v5→v6 migration mistakes. The config key is `output` and the result key is also `output`.

### Image Generation Model Selection

**Always use `google/gemini-3.1-flash-image-preview`** for image generation. Do NOT use older models (`gemini-2.0-*`, `gemini-2.5-*`) — they produce much worse results and some do not support image output at all.

### Rendering AI Text in Browser

**Never** render AI output as raw `{text}`, `<p>{content}</p>`, or `<div>{stream}</div>` — this always produces ugly unformatted output with visible markdown syntax. Always use AI Elements (`<Message>` for chat, `<MessageResponse>` for any other AI text).

### Migration Key Changes (v5 → v6)

- `generateObject` / `streamObject` → `generateText` / `streamText` with `Output.object()`
- `parameters` → `inputSchema`
- `result` → `output`
- `maxSteps` → `stopWhen: stepCountIs(N)` (import `stepCountIs` from `ai`)
- `CoreMessage` → `ModelMessage` (use `convertToModelMessages()` — now async)
- `ToolCallOptions` → `ToolExecutionOptions`
- `Experimental_Agent` → `ToolLoopAgent` (concrete class; `Agent` is just an interface)
- `system` → `instructions` (on `ToolLoopAgent`)
- `agent.generateText()` → `agent.generate()`
- `agent.streamText()` → `agent.stream()`
- `experimental_createMCPClient` → `createMCPClient` (stable)
- New: `createAgentUIStreamResponse({ agent, uiMessages })` for agent API routes
- New: `callOptionsSchema` + `prepareCall` for per-call agent configuration
- `useChat({ api })` → `useChat({ transport: new DefaultChatTransport({ api }) })`
- `useChat` `body` / `onResponse` options removed → configure with transport
- `handleSubmit` / `input` → `sendMessage({ text })` / manage own state
- `toDataStreamResponse()` → `toUIMessageStreamResponse()` (for chat UIs)
- `createUIMessageStream`: use `stream.writer.write(...)` (not `stream.write(...)`)
- text-only clients / text stream protocol → `toTextStreamResponse()`
- `message.content` → `message.parts` (tool parts use `tool-<toolName>`, not `tool-invocation`)
- UIMessage / ModelMessage types introduced
- `DynamicToolCall.args` is not strongly typed; cast via `unknown` first
- `TypedToolResult.result` → `TypedToolResult.output`
- `ai@^6.0.0` is the umbrella package
- `@ai-sdk/react` must be installed separately at `^3.0.x`
- `@ai-sdk/gateway` (if installed directly) is `^3.x`, not `^1.x`
- New: `needsApproval` on tools (boolean or async function) for human-in-the-loop approval
- New: `strict: true` per-tool opt-in for strict schema validation
- New: `DirectChatTransport` — connect `useChat` to an Agent in-process, no API route needed
- New: `addToolApprovalResponse` on `useChat` for client-side approval UI
- Default `stopWhen` changed from `stepCountIs(1)` to `stepCountIs(20)` for `ToolLoopAgent`
- New: `ToolCallOptions` type renamed to `ToolExecutionOptions`
- New: `Tool.toModelOutput` now receives `({ output })` object, not bare `output`
- New: `isToolUIPart` → `isStaticToolUIPart`; `isToolOrDynamicToolUIPart` → `isToolUIPart`
- New: `getToolName` → `getStaticToolName`; `getToolOrDynamicToolName` → `getToolName`
- New: `@ai-sdk/azure` defaults to Responses API; use `azure.chat()` for Chat Completions
- New: `@ai-sdk/anthropic` `structuredOutputMode` for native structured outputs (Anthropic Sonnet 4.5+)
- New: `@ai-sdk/langchain` rewritten — `toBaseMessages()`, `toUIMessageStream()`, `LangSmithDeploymentTransport`
- New: Provider-specific tools — Anthropic (memory, code execution), OpenAI (shell, patch), Google (maps, RAG), xAI (search, code)
- `unknown` finish reason removed → now returned as `other`
- Warning types consolidated into single `Warning` type exported from `ai`

## Verification

1. **Verify installation** — check that `ai` and `@ai-sdk/react` are installed at correct versions:
   ```bash
   npm ls ai @ai-sdk/react
   # Expected: ai@6.x.x, @ai-sdk/react@3.x.x
   ```

2. **Verify OIDC token provisioning** — ensure `.env.local` contains the token:
   ```bash
   # Windows PowerShell
   Get-Content .env.local | Select-String "VERCEL_OIDC_TOKEN"
   # Expected: VERCEL_OIDC_TOKEN=... (non-empty JWT)
   ```

3. **Verify AI Elements installed** — check for component files:
   ```bash
   # Windows PowerShell
   Test-Path components\ai-elements\message.tsx
   # Expected: True
   ```

4. **Verify DevTools** — run and confirm port 4983 is accessible:
   ```bash
   npx @ai-sdk/devtools
   # Opens http://localhost:4983
   ```

5. **Verify migration** — dry-run the codemod to preview changes:
   ```bash
   npx @ai-sdk/codemod --dry upgrade
   # Review output for breaking changes before applying
   ```

## Key Patterns

1. **Default to AI Gateway with OIDC** — pass `"provider/model"` strings (e.g., `model: "openai/gpt-5.4"`) to route through the gateway automatically. `vercel env pull` provisions OIDC tokens. No manual API keys needed. The `gateway()` wrapper is optional (only needed for `providerOptions.gateway`).
2. **Set up a Vercel project for AI** — `vercel link` → enable AI Gateway at `https://vercel.com/{team}/{project}/settings` → **AI Gateway** → `vercel env pull` to get OIDC credentials. Never manually create `.env.local` with provider-specific API keys.
3. **Always use AI Elements for any AI text in a browser** — `npx ai-elements` installs production-ready Message, Conversation, and Tool components. Use `<Message>` for chat and `<MessageResponse>` for any other AI-generated text (streaming panels, summaries, reports). AI models always produce markdown — there is no scenario where raw `{text}` rendering is correct. ⤳ skill: ai-elements
4. **Always stream for user-facing AI** — use `streamText` + `useChat`, not `generateText`
5. **UIMessage chat UIs** — `useChat()` defaults to `DefaultChatTransport({ api: '/api/chat' })`. On the server: `convertToModelMessages()` + `toUIMessageStreamResponse()`. For no-API-route setups: `DirectChatTransport` + Agent.
6. **Text-only clients (non-browser)** — `toTextStreamResponse()` is only for CLI tools, server pipes, and programmatic consumers. If the text is displayed in a browser, use `toUIMessageStreamResponse()` + AI Elements
7. **Use structured output** for extracting data — `generateText` with `Output.object()` and Zod schemas
8. **Use `ToolLoopAgent`** for multi-step reasoning — not manual loops. Default `stopWhen` is `stepCountIs(20)`. Use `createAgentUIStreamResponse` for agent API routes.
9. **Use DurableAgent** (from Workflow DevKit) for production agents that must survive crashes
10. **Use `mcp-to-ai-sdk`** to generate static tool definitions from MCP servers for security
11. **Use `needsApproval`** for human-in-the-loop — set on any tool to pause execution until user approves; supports conditional approval via async function
12. **Use `strict: true`** per tool — opt-in strict mode ensures providers only generate schema-valid tool calls; set on individual tools, not globally

## Related skills

- **ai-elements** — Full component library, decision guidance, and troubleshooting for AI interfaces. Use when rendering any AI-generated text in a browser.

## Official Documentation

- [AI SDK Documentation](https://ai-sdk.dev/docs)
- [AI SDK Core](https://ai-sdk.dev/docs/ai-sdk-core)
- [AI SDK UI](https://ai-sdk.dev/docs/ai-sdk-ui)
- [Generating Text](https://ai-sdk.dev/docs/ai-sdk-core/generating-text)
- [Structured Data](https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data)
- [Tools and Tool Calling](https://ai-sdk.dev/docs/ai-sdk-core/tools-and-tool-calling)
- [Agents](https://ai-sdk.dev/docs/ai-sdk-core/agents)
- [Providers and Models](https://ai-sdk.dev/docs/foundations/providers-and-models)
- [Provider Directory](https://ai-sdk.dev/providers)
- [GitHub: AI SDK](https://github.com/vercel/ai)
