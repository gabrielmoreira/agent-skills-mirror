---
name: inngest
description: "Builds Inngest serverless functions: typed EventSchemas, step.run checkpoints, step.sleep, step.sendEvent fan-out, cron, concurrency limits, and a Next.js/Vercel serve() handler. Use when the user mentions Inngest, serverless background jobs, durable steps, or event-driven cron. Not for Temporal workers and clusters, n8n Code nodes, or Convex ctx.scheduler as the job platform."
version: 1.0.1
risk: none
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
---

# Inngest Integration

Inngest provides serverless-first background jobs, event-driven workflows, and durable execution without managing queues or workers. Events are the primitive; steps are durable checkpoints; sleeps are real non-blocking waits.

## When to Use

Activate this skill when the user mentions or implies any of the following:

- `inngest` by name
- Serverless background jobs or serverless queues
- Event-driven workflows or event fan-out
- Step functions or durable execution
- Vercel background jobs
- Scheduled functions or cron jobs
- Concurrency control for downstream services
- Idempotent webhook handling
- AI pipelines with long-running, multi-step processing

## Prerequisites

- An Inngest account and an event key (use `YOUR_INNGEST_EVENT_KEY` placeholder; never commit live keys).
- A project using a supported HTTP framework: Next.js (App Router), Express, Hono, Remix, SvelteKit, or any platform that serves HTTP (Vercel, Cloudflare Workers, Netlify, Railway, Fly.io).
- TypeScript recommended for typed event schemas.
- Inngest CLI for local dev: `npx inngest-cli@latest dev` (Windows PowerShell compatible).

## Procedure

### 1. Create the Inngest Client with Typed Events

Define your client and event schemas for type safety.

```typescript
// lib/inngest/client.ts
import { Inngest, EventSchemas } from 'inngest';

type Events = {
  'user/signed.up': { data: { userId: string; email: string } };
  'order/placed': { data: { orderId: string; total: number } };
};

export const inngest = new Inngest({
  id: 'my-app',
  schemas: new EventSchemas().fromRecord<Events>(),
});
```

### 2. Define Functions

Each function must have a unique `id`. Use `step.run` for durable checkpoints, `step.sleep` for non-blocking waits, and `step.sendEvent` for fan-out.

```typescript
// lib/inngest/functions.ts
import { inngest } from './client';

export const sendWelcomeEmail = inngest.createFunction(
  { id: 'send-welcome-email' },
  { event: 'user/signed.up' },
  async ({ event, step }) => {
    const user = await step.run('get-user', async () => {
      return await db.users.findUnique({ where: { id: event.data.userId } });
    });

    await step.run('send-email', async () => {
      await resend.emails.send({
        to: user.email,
        subject: 'Welcome!',
        template: 'welcome',
      });
    });

    await step.sleep('wait-for-tips', '24h');

    await step.run('send-tips', async () => {
      await resend.emails.send({
        to: user.email,
        subject: 'Getting Started Tips',
        template: 'tips',
      });
    });
  }
);
```

### 3. Register the Serve Handler

Inngest requires an HTTP endpoint to receive events. For Next.js App Router:

```typescript
// app/api/inngest/route.ts
import { serve } from 'inngest/next';
import { inngest } from '@/lib/inngest/client';
import { sendWelcomeEmail } from '@/lib/inngest/functions';

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [sendWelcomeEmail],
});
```

For other frameworks, use the corresponding import: `inngest/express`, `inngest/hono`, `inngest/remix`, `inngest/sveltekit`.

### 4. Run the Dev Server

Start the Inngest dev server locally (Windows PowerShell):

```powershell
npx inngest-cli@latest dev
```

This provides a local dashboard at `http://localhost:8288` for inspecting events and function runs.

### 5. Multi-Step Workflow with Parallel Steps and Concurrency

```typescript
export const processOrder = inngest.createFunction(
  {
    id: 'process-order',
    retries: 3,
    concurrency: { limit: 10 },
  },
  { event: 'order/placed' },
  async ({ event, step }) => {
    const { orderId } = event.data;

    const [inventory, payment] = await Promise.all([
      step.run('check-inventory', () => checkInventory(orderId)),
      step.run('validate-payment', () => validatePayment(orderId)),
    ]);

    if (!inventory.available) {
      await step.sendEvent('notify-backorder', {
        name: 'order/backordered',
        data: { orderId, items: inventory.missing },
      });
      return { status: 'backordered' };
    }

    const charge = await step.run('charge-payment', async () => {
      return await stripe.charges.create({
        amount: event.data.total,
        customer: payment.customerId,
      });
    });

    await step.run('ship-order', () => fulfillment.ship(orderId));

    return { status: 'completed', chargeId: charge.id };
  }
);
```

### 6. Scheduled / Cron Functions

```typescript
export const dailyDigest = inngest.createFunction(
  { id: 'daily-digest' },
  { cron: '0 9 * * *' },
  async ({ step }) => {
    const users = await step.run('get-users', async () => {
      return await db.users.findMany({ where: { digestEnabled: true } });
    });

    await step.sendEvent(
      'send-digests',
      users.map(user => ({
        name: 'digest/send',
        data: { userId: user.id },
      }))
    );

    return { sent: users.length };
  }
);

export const sendDigest = inngest.createFunction(
  { id: 'send-digest', concurrency: { limit: 50 } },
  { event: 'digest/send' },
  async ({ event, step }) => {
    // ... send individual digest
  }
);
```

### 7. Webhook Handler with Idempotency

```typescript
export const handleStripeWebhook = inngest.createFunction(
  {
    id: 'stripe-webhook',
    idempotency: 'event.data.stripeEventId',
  },
  { event: 'stripe/webhook.received' },
  async ({ event, step }) => {
    const { type, data } = event.data;

    switch (type) {
      case 'checkout.session.completed':
        await step.run('fulfill-order', async () => {
          await fulfillOrder(data.session.id);
        });
        break;
      case 'customer.subscription.deleted':
        await step.run('cancel-subscription', async () => {
          await cancelSubscription(data.subscription.id);
        });
        break;
    }
  }
);
```

### 8. AI Pipeline with Long Processing

```typescript
export const processDocument = inngest.createFunction(
  {
    id: 'process-document',
    retries: 2,
    concurrency: { limit: 5 },
  },
  { event: 'document/uploaded' },
  async ({ event, step }) => {
    const text = await step.run('extract-text', async () => {
      return await extractTextFromPDF(event.data.fileUrl);
    });

    const chunks = await step.run('chunk-text', async () => {
      return chunkText(text, { maxTokens: 500 });
    });

    const embeddings = await step.run('generate-embeddings', async () => {
      return await openai.embeddings.create({
        model: 'text-embedding-3-small',
        input: chunks,
      });
    });

    await step.run('store-vectors', async () => {
      await vectorDb.upsert({
        vectors: embeddings.data.map((e, i) => ({
          id: `${event.data.documentId}-${i}`,
          values: e.embedding,
          metadata: { chunk: chunks[i] },
        })),
      });
    });

    return { chunks: chunks.length, status: 'indexed' };
  }
);
```

## Pitfalls

- **Missing serve handler (CRITICAL):** Inngest requires a serve handler to receive events. Without `app/api/inngest/route.ts` (or framework equivalent), no events will be delivered.
- **Functions not registered in serve() (ERROR):** Every function must be added to the `functions` array in the `serve()` call. A function defined but not registered will never execute.
- **Missing or duplicate function ID (CRITICAL):** Every `createFunction` call must have a unique `id`. Duplicate IDs cause silent overwrites.
- **waitForEvent without timeout (ERROR):** `waitForEvent` must include a timeout option: `{ timeout: '24h' }`. Without it, functions can wait indefinitely.
- **Payment functions without idempotency (ERROR):** Payment-related functions must use `idempotency: 'event.data.orderId'` (or equivalent) to prevent duplicate charges.
- **Step names not descriptive (WARNING):** Use kebab-case descriptive names like `'fetch-user'` or `'send-email'`. Generic names make debugging difficult.
- **No concurrency limit (WARNING):** Add `concurrency: { limit: N }` to protect downstream services from overload.
- **No event schemas (WARNING):** Define `schemas: new EventSchemas().fromRecord<Events>()` for type safety and autocomplete.
- **Sleep using milliseconds (WARNING):** Use duration strings like `'1h'`, `'30m'`, `'24h'` — not raw milliseconds.
- **No retry policy (WARNING):** Add `retries: 3` or `retries: { attempts: 3, backoff: { ... } }` for failure handling.
- **Blocking sleep instead of step.sleep:** Never use `setTimeout` or `await new Promise(resolve => setTimeout(...))` inside an Inngest function. Use `step.sleep('name', '24h')` for durable, non-blocking waits.
- **Direct function calls instead of events for fan-out:** Use `step.sendEvent` to trigger other functions rather than calling them directly. This preserves durability and retry semantics.

## Verification

1. **Serve handler present:**

   ```powershell
   # Check that the route file exists (Next.js App Router)
   Test-Path app\api\inngest\route.ts
   # Expected: True
   ```

2. **All functions registered:**

   ```powershell
   # List all createFunction IDs
   Select-String -Path "lib\inngest\functions.ts" -Pattern "id:\s*'" -AllMatches | ForEach-Object { $_.Matches.Value }
   # Then verify each ID appears in the serve() functions array
   ```

3. **Local dev server running:**

   ```powershell
   npx inngest-cli@latest dev
   # Expected: Dashboard available at http://localhost:8288
   ```

4. **Send a test event:**

   ```powershell
   curl -X POST http://localhost:8288/e/key `
     -H "Content-Type: application/json" `
     -d '{\"name\":\"user/signed.up\",\"data\":{\"userId\":\"test-123\",\"email\":\"test@example.com\"}}'
   # Expected: 200 OK with event ID
   ```

5. **Check function run in dashboard:**

   Open `http://localhost:8288` in a browser. Verify the function appears with status `Completed` and each step shows its durably stored output.

6. **Verify concurrency and retry config:**

   ```powershell
   Select-String -Path "lib\inngest\functions.ts" -Pattern "concurrency|retries|idempotency"
   # Expected: matches for functions that need them
   ```

## Related Skills

Works well with: `nextjs-app-router`, `vercel-deployment`, `supabase-backend`, `email-systems`, `ai-agents-architect`, `stripe-integration`.

### Delegation Triggers

- `redis`, `queue infrastructure`, `bullmq` → `bullmq-specialist` (Need Redis-based queue with existing infrastructure)
- `saga`, `compensation`, `rollback`, `long-running workflow` → `temporal-craftsman` (Need complex workflow orchestration with compensation)
- `event sourcing`, `event store`, `cqrs` → `event-architect` (Need event sourcing patterns)
- `vercel`, `deploy`, `production` → `vercel-deployment` (Need deployment configuration)
- `database`, `schema`, `data model` → `supabase-backend` (Need database for event data)
- `api`, `endpoint`, `route` → `backend` (Need API to trigger events)

### Collaboration Workflows

**Vercel Background Jobs** (`inngest`, `nextjs-app-router`, `vercel-deployment`):
1. Define Inngest functions (`inngest`)
2. Set up serve handler in Next.js (`nextjs-app-router`)
3. Configure function timeouts (`vercel-deployment`)
4. Deploy and test (`vercel-deployment`)

**AI Pipeline** (`inngest`, `ai-agents-architect`, `supabase-backend`):
1. Design AI workflow steps (`ai-agents-architect`)
2. Implement with Inngest durability (`inngest`)
3. Store results in database (`supabase-backend`)
4. Handle retries for API failures (`inngest`)

**Webhook Processing** (`inngest`, `stripe-integration`, `backend`):
1. Receive webhook (`backend`)
2. Send to Inngest with idempotency (`inngest`)
3. Process payment logic (`stripe-integration`)
4. Update application state (`backend`)

**Email Automation** (`inngest`, `email-systems`, `supabase-backend`):
1. Trigger event from user action (`inngest`)
2. Schedule drip emails with `step.sleep` (`inngest`)
3. Send emails with retry (`email-systems`)
4. Track email status (`supabase-backend`)

**Scheduled Tasks** (`inngest`, `backend`, `analytics-architecture`):
1. Define cron triggers (`inngest`)
2. Implement processing logic (`backend`)
3. Aggregate and report data (`analytics-architecture`)
4. Handle failures with alerting (`inngest`)

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
