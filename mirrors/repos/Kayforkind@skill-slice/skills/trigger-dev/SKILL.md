---
name: trigger-dev
description: "Defines Trigger.dev v3 TypeScript tasks: durable background jobs, cron, webhooks, batches, retries, and trigger.config.ts at the package root. Use when the user mentions Trigger.dev, AI/background jobs past serverless timeouts, or Trigger cron/webhooks. Not for BullMQ, Inngest, Temporal sagas, or Wrangler Cron Triggers. Never hardcode TRIGGER_SECRET_KEY or let SDK and CLI versions drift."
version: 1.0.1
---

# Trigger.dev Integration

Trigger.dev provides durable, retryable background jobs with a TypeScript-first API. Tasks are independently retryable, runs survive crashes, and built-in integrations wrap external SDKs with automatic retries and rate-limit handling.

## When to Use

Activate this skill when the user mentions or implies any of the following:

- **trigger.dev** or **trigger dev** (SDK, CLI, dashboard, deployment)
- **Background tasks** or **background jobs** in a TypeScript/Node project
- **AI background jobs** (OpenAI, Anthropic processing off the request cycle)
- **Long-running tasks** that exceed serverless timeouts
- **Integration tasks** (Stripe, Slack, Resend, Supabase wrappers)
- **Scheduled tasks** / cron-style jobs without external cron
- **Webhook handling** with deduplication / idempotency
- **Batch processing** with concurrency control and rate limiting
- **Task queues** managed by Trigger.dev

### Scope Boundaries — Delegate Instead

| Need | Delegate to |
|---|---|
| Redis-backed traditional queues (BullMQ) | `bullmq-specialist` |
| Pure event-driven / event sourcing / fan-out | `inngest` |
| Complex workflow orchestration (sagas, compensation) | `temporal-craftsman` |
| Infrastructure provisioning | `infra-architect` |
| Vercel deployment configuration | `vercel-deployment` |
| Supabase / Postgres backend logic | `supabase-backend` |
| AI model selection and prompt architecture | `llm-architect` |
| Stripe-specific integration logic | `stripe-integration` |
| Email delivery systems | `email-systems` |

## Prerequisites

- **Node.js 18+** and a TypeScript project (Next.js, Remix, Express, or Hono)
- **Trigger.dev account** (Trigger Cloud or self-hosted) with a project created
- **`TRIGGER_SECRET_KEY`** environment variable set — never hardcode the key
- **SDK and CLI on compatible versions** — always update together
- **Windows host (PowerShell)** is the primary development environment; use `npx trigger.dev@latest` commands as shown below

### Install SDK and CLI

```powershell
npm install @trigger.dev/sdk@latest
# CLI is invoked via npx; no global install required
npx trigger.dev@latest --version
```

### Verify versions match

```powershell
npx trigger.dev@latest --version
npm list @trigger.dev/sdk
```

If versions diverge, pin both to the same version:

```powershell
npm install @trigger.dev/sdk@3.3.0
npx trigger.dev@3.3.0 dev
```

## Procedure

### 1. Create `trigger.config.ts` at the Package Root

The CLI looks for `trigger.config.ts` in the current working directory. In a monorepo, place it at the **package** root, not the monorepo root.

```
my-app/
├── trigger.config.ts      <- HERE
├── package.json
├── src/
│   └── trigger/
│       └── tasks.ts
```

```typescript
// trigger.config.ts
import { defineConfig } from '@trigger.dev/sdk/v3';

export default defineConfig({
  project: 'my-project',
  runtime: 'node',
  logLevel: 'log',
  retries: {
    enabledInDev: true,
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
      factor: 2,
    },
  },
});
```

**Monorepo override** — specify config path explicitly:

```powershell
npx trigger.dev dev --config ./apps/web/trigger.config.ts
```

### 2. Define Tasks

```typescript
// src/trigger/tasks.ts
import { task, logger } from '@trigger.dev/sdk/v3';

export const helloWorld = task({
  id: 'hello-world',
  run: async (payload: { name: string }) => {
    logger.log('Processing hello world', { payload });
    await new Promise(resolve => setTimeout(resolve, 1000));
    return { message: `Hello, ${payload.name}!` };
  },
});
```

**HARD RULE**: Every task MUST have an explicit `id` property. Tasks without an `id` will not register.

**HARD RULE**: Every task SHOULD include `logger.log()` calls. Without logging, production failures are undebuggable.

**HARD RULE**: Every task that calls an external API or database SHOULD set a `queue.concurrencyLimit` to protect downstream services.

### 3. Trigger Tasks From Your App

```typescript
import { helloWorld } from '@/trigger/tasks';

// Fire and forget
await helloWorld.trigger({ name: 'World' });

// Wait for result
const handle = await helloWorld.trigger({ name: 'World' });
const result = await handle.wait();
```

**HARD RULE**: Payloads are JSON-serialized. Never pass `Date` objects, class instances, functions, or circular references. Use ISO strings and plain objects.

```typescript
// WRONG
await myTask.trigger({ createdAt: new Date() });
await myTask.trigger({ user: new User(data) });

// RIGHT
await myTask.trigger({ createdAt: new Date().toISOString() });
await myTask.trigger({ user: { id: data.id, email: data.email } });
```

### 4. Run the Dev Server

In development, tasks execute through the local dev server. If it is not running, triggers queue silently or fail without errors.

```powershell
# Terminal 1: Your app
npm run dev

# Terminal 2: Trigger.dev dev server
npx trigger.dev dev
```

Add a convenience script to `package.json`:

```json
{
  "scripts": {
    "dev": "next dev",
    "trigger:dev": "trigger.dev dev",
    "dev:all": "concurrently \"npm run dev\" \"npm run trigger:dev\""
  }
}
```

Confirm the dev server is connected: the console should show "Connected to Trigger.dev" and task registrations should appear.

### 5. Sync Environment Variables to Trigger Cloud

Trigger.dev runs tasks in its own cloud, separate from Vercel/Railway. Environment variables must be configured in **both** places — they do not auto-sync.

```powershell
# Create .env.trigger file (example placeholders only — never commit real secrets)
# DATABASE_URL=postgres://YOUR_DB_HOST/YOUR_DB
# OPENAI_API_KEY=YOUR_KEY
# STRIPE_SECRET_KEY=YOUR_KEY

# Push to Trigger.dev
npx trigger.dev@latest env push
```

Alternatively, add variables manually via the Trigger.dev dashboard: **Project Settings > Environment Variables**.

Common missing variables: `DATABASE_URL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `STRIPE_SECRET_KEY`, service API keys, internal service URLs.

**HARD RULE**: Configure staging environment variables separately — Trigger.dev has separate environments.

### 6. Use Built-in Integrations (Not Raw SDKs)

Trigger.dev integrations wrap external SDKs with automatic retries, rate-limit handling, and structured logging. Using raw SDKs means you lose these features.

```typescript
import { task, logger } from '@trigger.dev/sdk/v3';
import { openai } from '@trigger.dev/openai';

const openaiClient = openai.configure({
  id: 'openai',
  apiKey: process.env.OPENAI_API_KEY,
});

export const generateContent = task({
  id: 'generate-content',
  retry: { maxAttempts: 3 },
  run: async (payload: { topic: string; style: string }) => {
    logger.log('Generating content', { topic: payload.topic });
    const completion = await openaiClient.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: `You are a ${payload.style} writer.` },
        { role: 'user', content: `Write about: ${payload.topic}` },
      ],
    });
    const content = completion.choices[0].message.content;
    logger.log('Generated content', { length: content?.length });
    return { content, tokens: completion.usage?.total_tokens };
  },
});
```

Available integrations: `@trigger.dev/openai`, `@trigger.dev/anthropic`, `@trigger.dev/resend`, `@trigger.dev/slack`, `@trigger.dev/stripe`.

### 7. Scheduled Tasks (Cron)

No external cron needed — Trigger.dev handles scheduling natively.

```typescript
import { schedules, task, logger } from '@trigger.dev/sdk/v3';

export const dailyCleanup = schedules.task({
  id: 'daily-cleanup',
  cron: '0 2 * * *',  // 2 AM daily
  run: async () => {
    logger.log('Starting daily cleanup');
    const deleted = await db.logs.deleteMany({
      where: {
        createdAt: { lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) },
      },
    });
    logger.log('Cleanup complete', { deletedCount: deleted.count });
    return { deleted: deleted.count };
  },
});

export const weeklyReport = schedules.task({
  id: 'weekly-report',
  cron: '0 9 * * 1',  // Monday 9 AM
  run: async () => {
    const stats = await generateWeeklyStats();
    await sendReportEmail(stats);
    return stats;
  },
});
```

### 8. Batch Processing with Concurrency Control

```typescript
import { task, logger, wait } from '@trigger.dev/sdk/v3';

export const processBatch = task({
  id: 'process-batch',
  queue: {
    concurrencyLimit: 5,  // Only 5 running at once
  },
  run: async (payload: { items: string[] }) => {
    const results = [];
    for (const item of payload.items) {
      logger.log('Processing item', { item });
      const result = await processItem(item);
      results.push(result);
      await wait.for({ seconds: 1 });
    }
    return { processed: results.length, results };
  },
});

export const startBatchJob = task({
  id: 'start-batch',
  run: async (payload: { datasetId: string }) => {
    const items = await fetchDataset(payload.datasetId);
    const chunks = chunkArray(items, 100);
    const handles = await Promise.all(
      chunks.map(chunk => processBatch.trigger({ items: chunk }))
    );
    logger.log('Started batch processing', {
      totalItems: items.length,
      batches: chunks.length,
    });
    return { batches: handles.length };
  },
});
```

**HARD RULE**: Avoid `wait.for` inside loops with thousands of iterations — each `wait.for` creates checkpoint state and the state blob grows until it hits memory limits. Batch items instead:

```typescript
// WRONG — 1000 waits = bloated state
for (const item of items) {
  await processItem(item);
  await wait.for({ milliseconds: 100 });
}

// RIGHT — batch and wait once per batch
const chunks = chunkArray(items, 50);
for (const chunk of chunks) {
  await Promise.all(chunk.map(processItem));
  await wait.for({ milliseconds: 500 });
}
```

For very large datasets, split into subtasks using `triggerAndWait` so each chunk is a separate task with its own timeout and state.

### 9. Webhook Handling with Idempotency

```typescript
import { task, logger, idempotencyKeys } from '@trigger.dev/sdk/v3';

export const handleStripeEvent = task({
  id: 'handle-stripe-event',
  run: async (payload: { eventId: string; type: string; data: any }) => {
    const idempotencyKey = await idempotencyKeys.create(payload.eventId);

    if (idempotencyKey.isNew === false) {
      logger.log('Duplicate event, skipping', { eventId: payload.eventId });
      return { skipped: true };
    }

    logger.log('Processing Stripe event', {
      type: payload.type,
      eventId: payload.eventId,
    });

    switch (payload.type) {
      case 'checkout.session.completed':
        await handleCheckoutComplete(payload.data);
        break;
      case 'customer.subscription.updated':
        await handleSubscriptionUpdate(payload.data);
        break;
    }

    return { processed: true, type: payload.type };
  },
});
```

**HARD RULE**: Trigger.dev retries failed tasks from the **beginning**. If your task has side effects (emails, charges, Slack messages) before the failure point, those execute again on retry. Always use `idempotencyKeys` or database tracking for side-effect tasks.

### 10. Configure Timeouts for Long-Running Tasks

Trigger.dev has execution timeouts (defaults vary by plan). When exceeded, the task is killed mid-execution, often without a clear error in logs.

```typescript
export const processDocument = task({
  id: 'process-document',
  machine: {
    preset: 'large-2x',  // More resources = longer allowed time
  },
  run: async (payload) => {
    logger.log('Starting document processing', { docId: payload.id });
    logger.log('Step 1: Extracting text');
    const text = await extractText(payload.fileUrl);
    logger.log('Step 2: Generating embeddings', { textLength: text.length });
    const embeddings = await generateEmbeddings(text);
    logger.log('Step 3: Storing vectors', { count: embeddings.length });
    await storeVectors(embeddings);
    logger.log('Completed successfully');
    return { processed: true };
  },
});
```

For very long tasks, break into subtasks using `triggerAndWait` — each subtask has its own timeout and progress is visible in the dashboard.

### 11. Deploy

```powershell
npx trigger.dev@latest deploy
```

In CI/CD, pin the version:

```yaml
- run: npm install @trigger.dev/sdk@${{ env.TRIGGER_VERSION }}
- run: npx trigger.dev@${{ env.TRIGGER_VERSION }} deploy
```

## Pitfalls

### CRITICAL: Task timeout kills execution without clear error

**Symptoms**: Task fails with no error message; partial data processing; works locally but fails in production; "Task timed out" in dashboard.

**Cause**: Execution timeout exceeded. Especially common with AI tasks that take minutes.

**Fix**: Set `machine.preset` for more resources, log progress at each step, and break very long tasks into subtasks with `triggerAndWait`.

### CRITICAL: Non-serializable payload causes silent task failure

**Symptoms**: Payload values are `undefined` in task; `Date` objects become strings; class methods unavailable; "Converting circular structure to JSON" error.

**Cause**: Trigger.dev serializes payloads to JSON. Dates → strings, class instances → plain objects (methods lost), functions → disappear, circular refs → throw.

**Fix**: Always pass plain objects with ISO string dates. Reconstitute `Date` objects inside the task body.

### CRITICAL: Environment variables not synced to Trigger Cloud

**Symptoms**: "Environment variable not found"; API calls return 401 in production; database connection errors in tasks; works in dev, fails in production.

**Cause**: Trigger.dev runs tasks in its own cloud. Env vars must be configured in both your app host and Trigger.dev.

**Fix**: Run `npx trigger.dev@latest env push` or add manually via dashboard. Configure staging separately.

### CRITICAL: Hardcoded API key

**Symptoms**: Secret exposed in source control.

**Fix**: Never hardcode `TRIGGER_SECRET_KEY` or any integration API key. Always use `process.env.TRIGGER_SECRET_KEY` / `process.env.OPENAI_API_KEY` etc.

### HIGH: SDK version mismatch between CLI and package

**Symptoms**: Tasks not appearing in dashboard; type errors in `trigger.config.ts`; "Failed to register task"; dev server crashes on start.

**Fix**: Always update SDK and CLI together. Pin to the same version in CI/CD.

### HIGH: Task retries cause duplicate side effects

**Symptoms**: Duplicate emails, multiple charges, duplicate webhook deliveries, data inserted multiple times.

**Fix**: Use `idempotencyKeys.create()` or database tracking (e.g., `emailLogs` table with unique constraint on `orderId` + `type`).

### HIGH: High concurrency overwhelms downstream services

**Symptoms**: 429 rate limit errors; database connection pool exhausted; mass task failures; retry storms.

**Fix**: Set `queue.concurrencyLimit`. Start conservative: 5–10 for external APIs, 20–50 for databases. Add `wait.for` between calls and use exponential backoff on retries.

### HIGH: `trigger.config.ts` not at project root

**Symptoms**: "Could not find trigger.config.ts"; tasks not discovered; empty task list in dashboard.

**Fix**: Place config at the package root. In monorepos, run `npx trigger.dev dev` from the package directory or use `--config` flag.

### MEDIUM: `wait.for` in loops causes memory issues

**Symptoms**: Task killed for memory; "State blob too large" error; works for small batches, fails for large.

**Fix**: Batch items and use fewer `wait.for` calls, or split into subtasks.

### MEDIUM: Using raw SDK instead of Trigger.dev integrations

**Symptoms**: Manual retry logic needed; rate limit errors not handled; no automatic logging of API calls.

**Fix**: Use `@trigger.dev/openai`, `@trigger.dev/anthropic`, `@trigger.dev/slack`, etc. instead of raw SDKs.

### MEDIUM: Triggering tasks without dev server running

**Symptoms**: Triggers don't run; no task in dashboard; no errors, just silence.

**Fix**: Always run `npx trigger.dev dev` during development alongside your app dev server.

## Verification

Run these checks to confirm a healthy Trigger.dev setup:

### Check 1: Dev server is connected

```powershell
npx trigger.dev dev
```

**Expected**: Console shows "Connected to Trigger.dev" and lists registered task IDs. Dashboard at `https://cloud.trigger.dev` shows tasks under your project.

### Check 2: SDK and CLI versions match

```powershell
npx trigger.dev@latest --version
npm list @trigger.dev/sdk
```

**Expected**: Both report the same (or compatible) version number.

### Check 3: Config file is discoverable

```powershell
npx trigger.dev dev --config ./trigger.config.ts
```

**Expected**: No "Could not find trigger.config.ts" error. Tasks appear in the dashboard task list.

### Check 4: Environment variables are synced

```powershell
npx trigger.dev@latest env push
```

**Expected**: CLI reports successful push. Verify in dashboard under **Project Settings > Environment Variables** that all required keys are present for both production and staging.

### Check 5: Task triggers successfully

Trigger a test task from your app or the dashboard:

```typescript
const handle = await helloWorld.trigger({ name: 'World' });
const result = await handle.wait();
console.log(result); // { message: 'Hello, World!' }
```

**Expected**: Task appears in dashboard with status `COMPLETED`. Logs are visible. Return value matches expectation.

### Check 6: Retry behavior is correct

Intentionally throw an error inside a task and verify:

- The task retries up to `maxAttempts`
- Logs show each attempt
- Idempotency keys prevent duplicate side effects on retry

### Check 7: Concurrency limits are enforced

Trigger a burst of tasks exceeding `concurrencyLimit` and verify in the dashboard that only the configured number run simultaneously; the rest queue.

## Related Skills

Works well with: `nextjs-app-router`, `vercel-deployment`, `ai-agents-architect`, `llm-architect`, `email-systems`, `stripe-integration`, `supabase-backend`, `bullmq-specialist`, `inngest`, `temporal-craftsman`.
