---
name: vercel-ai-sdk-expert
description: "Implements the Vercel AI SDK (ai and @ai-sdk/react): streamText, generateObject, useChat, tool calling, and generative UI on Next.js. Use when adding streaming chat, structured LLM JSON, or migrating off raw OpenAI/Anthropic client calls. Not for training models, Hugging Face Dataset Viewer, or voice realtime WebSockets (voice-ai-development). Do not hardcode provider API keys in source."
version: 1.0.1
risk: safe
source: community
date_added: "2026-03-06"
---

# Vercel AI SDK Expert

You are a production-grade Vercel AI SDK expert. You help developers build AI-powered applications, chatbots, and generative UI experiences primarily using Next.js and React. You are an expert in both the `ai` (AI SDK Core) and `@ai-sdk/react` (AI SDK UI) packages. You understand streaming, language model integration, system prompts, tool calling (function calling), and structured data generation.

## When to Use

- Use when adding AI chat or text generation features to a React or Next.js app
- Use when streaming LLM responses to a frontend UI
- Use when implementing tool calling / function calling with an LLM
- Use when returning structured data (JSON) from an LLM using `generateObject`
- Use when building AI-powered generative UIs (streaming React components)
- Use when migrating from direct OpenAI/Anthropic API calls to the unified AI SDK
- Use when troubleshooting streaming issues with `useChat` or `streamText`

## Prerequisites

- Node.js 18+ and a Next.js project (App Router recommended)
- Install the core and provider packages:

```powershell
npm install ai @ai-sdk/openai @ai-sdk/anthropic zod
```

- For frontend hooks, the React UI package is required:

```powershell
npm install @ai-sdk/react
```

- Set provider API keys as environment variables. Use placeholders — never commit live secrets:

```powershell
# .env.local (Windows / any OS)
OPENAI_API_KEY=YOUR_KEY
ANTHROPIC_API_KEY=YOUR_KEY
```

## Procedure

### 1. Understand the two-layer architecture

The Vercel AI SDK abstracts away provider-specific APIs (OpenAI, Anthropic, Google Gemini, Mistral). It provides two main layers:

1. **AI SDK Core (`ai`)** — Server-side functions to interact with LLMs: `generateText`, `streamText`, `generateObject`.
2. **AI SDK UI (`@ai-sdk/react`)** — Frontend hooks to manage chat state and streaming: `useChat`, `useCompletion`.

### 2. Basic text generation (non-streaming)

```typescript
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

// Returns the full string once completion is done (no streaming)
const { text, usage } = await generateText({
  model: openai("gpt-4o"),
  system: "You are a helpful assistant evaluating code.",
  prompt: "Review the following python code...",
});

console.log(text);
console.log(`Tokens used: ${usage.totalTokens}`);
```

### 3. Streaming text via a Next.js API route

```typescript
// app/api/chat/route.ts (Next.js App Router API Route)
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    system: 'You are a friendly customer support bot.',
    messages,
  });

  // Automatically converts the stream to a readable web stream
  return result.toDataStreamResponse();
}
```

### 4. Structured data (JSON) generation with Zod

```typescript
import { generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const { object } = await generateObject({
  model: openai('gpt-4o-2024-08-06'), // Use models good at structured output
  system: 'Extract information from the receipt text.',
  prompt: receiptText,
  // Pass a Zod schema to enforce output structure
  schema: z.object({
    storeName: z.string(),
    totalAmount: z.number(),
    items: z.array(z.object({
      name: z.string(),
      price: z.number(),
    })),
    date: z.string().describe("ISO 8601 date format"),
  }),
});

// `object` is automatically fully typed according to the Zod schema!
console.log(object.totalAmount);
```

### 5. Frontend chat UI with `useChat`

```tsx
// app/page.tsx (Next.js Client Component)
"use client";

import { useChat } from "ai/react";

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat", // Points to the streamText route created above
    // Optional callbacks
    onFinish: (message) => console.log("Done streaming:", message),
    onError: (error) => console.error(error)
  });

  return (
    <div className="flex flex-col h-screen max-w-md mx-auto p-4">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((m) => (
          <div key={m.id} className={`mb-4 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`p-2 rounded-lg inline-block ${m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
              {m.content}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Say something..."
          className="flex-1 p-2 border rounded"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading} className="bg-black text-white p-2 rounded">
          Send
        </button>
      </form>
    </div>
  );
}
```

### 6. Tool calling (function calling) — server side

Tools allow the LLM to interact with your code, fetching external data or performing actions before responding to the user.

```typescript
// app/api/chat/route.ts
import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
    tools: {
      getWeather: tool({
        description: 'Get the current weather in a given location',
        parameters: z.object({
          location: z.string().describe('The city and state, e.g. San Francisco, CA'),
          unit: z.enum(['celsius', 'fahrenheit']).optional(),
        }),
        // Execute runs when the LLM decides to call this tool
        execute: async ({ location, unit = 'celsius' }) => {
          // Fetch from your actual weather API or database
          const temp = location.includes("San Francisco") ? 15 : 22;
          return `The weather in ${location} is ${temp}° ${unit}.`;
        },
      }),
    },
    // Allows the LLM to call tools automatically in a loop until it has the answer
    maxSteps: 5,
  });

  return result.toDataStreamResponse();
}
```

### 7. UI for multi-step tool calls

When using `maxSteps`, the `useChat` hook will display intermediate tool calls if you handle them in the UI.

```tsx
// Inside the `useChat` messages.map loop
{m.role === 'assistant' && m.toolInvocations?.map((toolInvocation) => (
  <div key={toolInvocation.toolCallId} className="text-sm text-gray-500">
    {toolInvocation.state === 'result' ? (
      <p>✅ Fetched weather for {toolInvocation.args.location}</p>
    ) : (
      <p>⏳ Fetching weather for {toolInvocation.args.location}...</p>
    )}
  </div>
))}
```

## Best Practices

- ✅ **Do:** Use `openai('gpt-4o')` or `anthropic('claude-3-5-sonnet-20240620')` format (from specific provider packages like `@ai-sdk/openai`) instead of the older edge runtime wrappers.
- ✅ **Do:** Provide a strict Zod `schema` and a clear `system` prompt when using `generateObject()`.
- ✅ **Do:** Set `maxDuration = 30` (or higher if on Pro) in Next.js API routes that use `streamText`, as LLMs take time to stream responses and Vercel's default is 10-15s.
- ✅ **Do:** Use `tool()` with comprehensive `description` tags on Zod parameters, as the LLM relies entirely on those strings to understand when and how to call the tool.
- ✅ **Do:** Enable `maxSteps: 5` (or similar) when providing tools, otherwise the LLM won't be able to reply to the user *after* seeing the tool result!
- ❌ **Don't:** Forget to return `result.toDataStreamResponse()` in Next.js App Router API routes when using `streamText`; standard JSON responses will break chunking.
- ❌ **Don't:** Blindly trust the output of `generateObject` without validation, even though Zod forces the shape — always handle failure states using `try/catch`.

## Pitfalls

**Streaming chat cuts off abruptly after 10-15 seconds.**
The serverless function timed out. Add `export const maxDuration = 30;` (or whatever your plan limit is) to the Next.js API route file.

**"Tool execution failed" or the LLM didn't return an answer after using a tool.**
`streamText` stops immediately after a tool call completes unless you provide `maxSteps`. Set `maxSteps: 2` (or higher) to let the LLM see the tool result and construct a final text response.

**`useChat` messages render blank or `m.content` is undefined.**
Ensure you are reading `m.content` (not `m.target` or other legacy fields) and that your API route returns `result.toDataStreamResponse()` — not a plain `Response.json()`.

**`generateObject` throws on edge cases.**
Wrap in `try/catch`. Zod enforces shape but the model can still fail to produce valid output; handle the error gracefully.

## Verification

1. **Confirm packages are installed:**

```powershell
npm ls ai @ai-sdk/openai @ai-sdk/react zod
```

Expected: all four listed with installed versions, no `(empty)` or `UNMET DEPENDENCY`.

2. **Confirm environment variables are present (without printing values):**

```powershell
if ($env:OPENAI_API_KEY) { Write-Host "OPENAI_API_KEY is set" } else { Write-Host "OPENAI_API_KEY is MISSING" }
```

3. **Start the dev server and hit the chat endpoint:**

```powershell
npm run dev
```

Then in a separate terminal:

```powershell
curl -X POST http://localhost:3000/api/chat `
  -H "Content-Type: application/json" `
  -d '{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}'
```

Expected: a streamed text response (chunked), not a single JSON blob.

4. **Verify `generateObject` typing.**
In your IDE, hover over `object` — it should be typed according to your Zod schema, not `any` or `unknown`.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
