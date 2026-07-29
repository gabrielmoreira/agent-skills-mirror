---
name: routerbase-model-gateway
description: Configure RouterBase as an OpenAI compatible model gateway for AI apps, with routing, fallback, media generation, and credential handling patterns.
metadata:
  author: zenlee123
  version: 1.0.0
  category: ai-ml
  tags:
    - routerbase
    - model-routing
    - openai-compatible
    - ai-gateway
    - fallback-design
    - media-generation
---

# RouterBase Model Gateway

Use [routerbase](https://routerbase.com/) when an application needs an OpenAI compatible gateway for chat, embeddings, image, video, audio, speech, model routing, or fallback behavior.

The goal is not to rewrite the whole AI layer. The goal is to move provider selection behind a clean server side boundary, keep credentials private, and make model choices reversible.

## When To Use

Use this skill when the user asks to:

- Migrate an OpenAI compatible client to RouterBase.
- Add RouterBase to a backend API, worker, command line tool, or agent runtime.
- Route requests across multiple model providers through one API surface.
- Choose primary and fallback models for latency, quality, price, or availability.
- Add image, video, audio, speech, or embedding generation through a gateway.
- Debug RouterBase base URLs, model IDs, streaming, JSON output, or media job polling.

Do not use this skill for:

- General API gateway design unrelated to AI models.
- Direct provider SDK features that are not exposed through the OpenAI compatible API.
- Frontend only integrations that would expose API keys to users.
- Production security review of the whole application.

## Implementation Principles

### 1. Keep The Gateway Server Side

All RouterBase calls should run in trusted code:

- backend route
- serverless function
- worker
- command line tool
- internal service
- agent runtime process

Never place `ROUTERBASE_API_KEY` in browser code, mobile applications, public logs, screenshots, or checked in examples.

### 2. Change Configuration Before Code Shape

Most migrations should start with configuration:

- base URL: `https://routerbase.com/v1`
- API key variable: `ROUTERBASE_API_KEY`
- chat model variable: `ROUTERBASE_CHAT_MODEL`
- embedding model variable: `ROUTERBASE_EMBEDDING_MODEL`
- media model variables for image, video, audio, or speech

Keep the OpenAI compatible request shape until there is a documented reason to change it.

### 3. Isolate Provider Choices

Do not scatter model IDs across product code. Put them in one adapter, config file, or environment mapping.

Good boundaries:

- `aiClient.ts`
- `modelConfig.ts`
- `llmGateway.ts`
- `services/ai/routerbase.ts`

Poor boundaries:

- hard coded model IDs in every route
- retries implemented differently in every feature
- media polling mixed into UI code
- provider errors returned directly to users

## Quick Start Example

```ts
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.ROUTERBASE_API_KEY,
  baseURL: process.env.ROUTERBASE_BASE_URL || "https://routerbase.com/v1",
});

export async function summarizeReleaseNote(text: string) {
  const completion = await client.chat.completions.create({
    model: process.env.ROUTERBASE_CHAT_MODEL || "openai/gpt-5.4-mini",
    messages: [
      { role: "system", content: "Summarize clearly for product engineers." },
      { role: "user", content: text },
    ],
  });

  return completion.choices[0]?.message?.content || "";
}
```

## Routing Checklist

Before choosing models, answer these questions:

1. What is the workload: chat, JSON output, streaming, tools, embeddings, image, video, audio, or speech?
2. What matters most: latency, output quality, cost, context length, availability, or modality support?
3. Does the fallback model return the same output shape?
4. Can the feature tolerate degraded quality, or should it fail closed?
5. Are user prompts, uploaded files, or generated assets subject to privacy rules?
6. What telemetry is needed: model ID, request ID, latency, status code, retry count, and fallback used?
7. What should the user see when the primary model fails?

## Fallback Pattern

Use fallbacks for availability, not to hide every error.

```ts
async function runWithFallback(messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[]) {
  const primary = process.env.ROUTERBASE_CHAT_MODEL || "openai/gpt-5.4-mini";
  const fallback = process.env.ROUTERBASE_CHAT_FALLBACK_MODEL || "openai/gpt-5.4-mini";

  try {
    return await client.chat.completions.create({ model: primary, messages });
  } catch (error) {
    if (!isRetryableModelError(error)) throw error;

    return client.chat.completions.create({
      model: fallback,
      messages,
    });
  }
}
```

Fallback only when:

- the error is temporary or provider specific
- the fallback model supports the same output contract
- the request does not require a provider that has a unique compliance rule
- the user experience is better with degraded output than with a clear failure

## Media Generation Flow

Treat long running media as a job workflow, not as a chat completion.

1. Validate the prompt and user permissions.
2. Create a media generation job through the RouterBase compatible endpoint for the selected modality.
3. Store the job ID, model ID, user ID, and requested output type.
4. Poll with backoff instead of holding one long request open.
5. Save generated assets to durable storage.
6. Return a stable URL or asset reference to the user.
7. Record failures with model ID, status code, and retry count.

## Evaluation Rubric

Score the integration from 0 to 2 for each item.

| Area | 0 | 1 | 2 |
|---|---|---|---|
| Credential handling | key exposed or hard coded | key is server side but examples are unclear | key is server side, documented, and scanned |
| Model configuration | IDs scattered in code | central config for some workloads | central config for all workloads |
| Fallback design | no fallback or unsafe fallback | fallback exists without clear policy | fallback policy is explicit and tested |
| Error handling | provider errors leak to users | common errors mapped | auth, quota, rate, timeout, and model errors handled |
| Media workflow | synchronous long request | polling exists but storage is weak | job, polling, storage, and status are separate |
| Observability | no useful logs | basic latency and status logs | request ID, model ID, fallback, retry count, latency |

Recommended threshold before production: at least 10 out of 12.

## Common Mistakes

- Putting RouterBase keys in frontend environment variables that are bundled for users.
- Hard coding one model ID in multiple product features.
- Assuming streaming and non streaming responses fail in the same way.
- Falling back to a model with a different JSON output contract.
- Treating image or video generation as a simple request response call.
- Logging full prompts, uploaded file contents, or generated private data.
- Retrying authentication or quota errors that should fail immediately.
- Returning raw provider error messages to end users.

## Output Expectations

When completing a RouterBase task, provide:

- files changed
- environment variables required
- primary and fallback model IDs
- test or smoke check performed
- privacy notes for prompts, files, and generated assets
- any unsupported features or assumptions

Keep the final recommendation concise. Include code only where it changes the integration boundary.
