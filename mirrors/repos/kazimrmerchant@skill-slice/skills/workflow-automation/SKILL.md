---
name: workflow-automation
description: "Builds durable multi-step automation on n8n, Temporal, Inngest, AWS Step Functions, or Azure Durable Functions with checkpointed steps, idempotency keys, and replay-safe activities. Trigger on Temporal, Inngest, n8n, Step Functions, durable execution, or crash-resistant background jobs. Do not use for Zapier/Make no-code zaps (zapier-make-patterns) or compensating-saga design (saga-orchestration)."
version: 1.0.1
risk: critical
source: vibeship-spawner-skills (Apache 2.0)
date_added: 2026-02-27
capabilities:
  - workflow-automation
  - workflow-orchestration
  - durable-execution
  - event-driven-workflows
  - step-functions
  - job-queues
  - background-jobs
  - scheduled-tasks
scope:
  - multi-agent-coordination → multi-agent-orchestration
  - ci-cd-pipelines → devops
  - data-pipelines → data-engineer
  - api-design → api-designer
---

# Workflow Automation

Workflow automation is the infrastructure that makes AI agents reliable. Without durable execution, a network hiccup during a 10-step payment flow means lost money and angry customers. With it, workflows resume exactly where they left off.

This skill covers the platforms (n8n, Temporal, Inngest, AWS Step Functions, Azure Durable Functions) and patterns (sequential, parallel, orchestrator-worker, event-driven, retry/recovery, scheduled) that turn brittle scripts into production-grade automation.

**Key insight:** The platforms make different tradeoffs. n8n optimizes for accessibility, Temporal for correctness, Inngest for developer experience. Pick based on your actual needs, not hype.

## When to Use

Activate this skill when the user mentions or implies any of:

- **workflow** or **automation** — designing, building, or debugging automated multi-step processes
- **n8n** — visual/low-code workflow platform
- **temporal** — mission-critical durable workflows
- **inngest** — event-driven serverless workflows
- **step function** — AWS or Azure state-machine workflows
- **background job** or **job queue** — async task processing
- **durable execution** — crash-resistant workflow replay
- **event-driven** — reactive workflow triggers
- **scheduled task** or **cron** — time-based recurring workflows
- **trigger** — webhook, event, or schedule-based workflow initiation

## Prerequisites

- **Runtime:** Node.js 18+ for Inngest/Temporal TypeScript SDKs; Python 3.10+ for Temporal Python SDK
- **Windows host (primary):** PowerShell 7+ recommended. Use forward slashes in cross-platform config files; use backslashes only in PowerShell-native commands
- **Platform access:** At least one of: n8n self-hosted or cloud, Temporal Cloud or self-hosted server, Inngest account, AWS account with Lambda+Step Functions, Azure account with Durable Functions
- **No live secrets in output:** Use `YOUR_KEY` placeholders for all API keys, tokens, and connection strings

## Procedure

### 1. Choose the Right Platform

| Platform | Best For | Tradeoff |
|---|---|---|
| **n8n** | Low-code automation, quick prototyping, non-technical users | Self-hostable, 400+ integrations, visual workflows; less programmatic control |
| **Temporal** | Mission-critical workflows, financial transactions, microservices | Strongest durability guarantees; steeper learning curve |
| **Inngest** | Event-driven serverless, TypeScript codebases, AI workflows | Best DX, works with any hosting; newer ecosystem |
| **AWS Step Functions** | AWS-native stacks, existing Lambda functions | Tight AWS integration; JSON-based workflow definition |
| **Azure Durable Functions** | Azure stacks, .NET or TypeScript | Good AI agent support, checkpoint and replay; Azure-locked |

### 2. Select a Workflow Pattern

#### Sequential Workflow Pattern

Steps execute in order; each output becomes the next input. Checkpoint at each step.

**When to use:** Content pipelines, data processing, ordered operations.

```
Step 1 → Step 2 → Step 3 → Output
  ↓         ↓         ↓
(checkpoint at each step)
```

**Inngest example (TypeScript):**

```typescript
import { inngest } from "./client";

export const processOrder = inngest.createFunction(
  { id: "process-order" },
  { event: "order/created" },
  async ({ event, step }) => {
    const validated = await step.run("validate-order", async () => {
      return validateOrder(event.data.order);
    });

    const payment = await step.run("process-payment", async () => {
      return chargeCard(validated.paymentMethod, validated.total);
    });

    const shipment = await step.run("create-shipment", async () => {
      return createShipment(validated.items, validated.address);
    });

    await step.run("send-confirmation", async () => {
      return sendEmail(validated.email, { payment, shipment });
    });

    return { success: true, orderId: event.data.orderId };
  }
);
```

**Temporal example (TypeScript):**

```typescript
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { validateOrder, chargeCard, createShipment, sendEmail } =
  proxyActivities<typeof activities>({
    startToCloseTimeout: '30 seconds',
    retry: {
      maximumAttempts: 3,
      backoffCoefficient: 2,
    }
  });

export async function processOrderWorkflow(order: Order): Promise<void> {
  const validated = await validateOrder(order);
  const payment = await chargeCard(validated.paymentMethod, validated.total);
  const shipment = await createShipment(validated.items, validated.address);
  await sendEmail(validated.email, { payment, shipment });
}
```

**n8n pattern:**

```
[Webhook: order.created]
    ↓
[HTTP Request: Validate Order]
    ↓
[HTTP Request: Process Payment]
    ↓
[HTTP Request: Create Shipment]
    ↓
[Send Email: Confirmation]
```

Configure each node with retry on failure. Use Error Trigger for dead letter handling.

#### Parallel Workflow Pattern

Independent steps run simultaneously; results are aggregated.

**When to use:** Multiple independent analyses, data from multiple sources.

```
        ┌→ Step A ─┐
Input ──┼→ Step B ─┼→ Aggregate → Output
        └→ Step C ─┘
```

**Inngest example:**

```typescript
export const analyzeDocument = inngest.createFunction(
  { id: "analyze-document" },
  { event: "document/uploaded" },
  async ({ event, step }) => {
    const [security, performance, compliance] = await Promise.all([
      step.run("security-analysis", () =>
        analyzeForSecurityIssues(event.data.document)
      ),
      step.run("performance-analysis", () =>
        analyzeForPerformance(event.data.document)
      ),
      step.run("compliance-analysis", () =>
        analyzeForCompliance(event.data.document)
      ),
    ]);

    const report = await step.run("generate-report", () =>
      generateReport({ security, performance, compliance })
    );

    return report;
  }
);
```

**AWS Step Functions (Amazon States Language):**

```json
{
  "Type": "Parallel",
  "Branches": [
    {
      "StartAt": "SecurityAnalysis",
      "States": {
        "SecurityAnalysis": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:security-analyzer",
          "End": true
        }
      }
    },
    {
      "StartAt": "PerformanceAnalysis",
      "States": {
        "PerformanceAnalysis": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:performance-analyzer",
          "End": true
        }
      }
    }
  ],
  "Next": "AggregateResults"
}
```

#### Orchestrator-Worker Pattern

Central coordinator dispatches work to specialized workers.

**When to use:** Complex tasks requiring different expertise, dynamic subtask creation.

```
┌─────────────────────────────────────┐
│          ORCHESTRATOR               │
│  - Analyzes task                    │
│  - Creates subtasks                 │
│  - Dispatches to workers            │
│  - Aggregates results               │
└─────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐
│Worker1│  │Worker2│  │Worker3│
│Create │  │Modify │  │Delete │
└───────┘  └───────┘  └───────┘
```

**Temporal example:**

```typescript
export async function orchestratorWorkflow(task: ComplexTask) {
  const plan = await analyzeTask(task);

  const results = await Promise.all(
    plan.subtasks.map(subtask => {
      switch (subtask.type) {
        case 'create':
          return executeChild(createWorkerWorkflow, { args: [subtask] });
        case 'modify':
          return executeChild(modifyWorkerWorkflow, { args: [subtask] });
        case 'delete':
          return executeChild(deleteWorkerWorkflow, { args: [subtask] });
      }
    })
  );

  return aggregateResults(results);
}
```

**Inngest with AI orchestration:**

```typescript
export const aiOrchestrator = inngest.createFunction(
  { id: "ai-orchestrator" },
  { event: "task/complex" },
  async ({ event, step }) => {
    const plan = await step.run("create-plan", async () => {
      return await llm.chat({
        messages: [
          { role: "system", content: "Break this task into subtasks..." },
          { role: "user", content: event.data.task }
        ]
      });
    });

    const results = [];
    for (const subtask of plan.subtasks) {
      const result = await step.run(`execute-${subtask.id}`, async () => {
        return executeSubtask(subtask);
      });
      results.push(result);
    }

    return await step.run("synthesize", async () => {
      return synthesizeResults(results);
    });
  }
);
```

#### Event-Driven Trigger Pattern

Workflows triggered by events, not schedules.

**When to use:** Reactive systems, user actions, webhook integrations.

**Inngest event-based:**

```typescript
type Events = {
  "user/signed.up": {
    data: { userId: string; email: string };
  };
  "order/completed": {
    data: { orderId: string; total: number };
  };
};

export const onboardUser = inngest.createFunction(
  { id: "onboard-user" },
  { event: "user/signed.up" },
  async ({ event, step }) => {
    await step.sleep("wait-for-exploration", "1 hour");

    await step.run("send-welcome", async () => {
      return sendWelcomeEmail(event.data.email);
    });

    await step.sleep("wait-for-engagement", "3 days");

    const engaged = await step.run("check-engagement", async () => {
      return checkUserEngagement(event.data.userId);
    });

    if (!engaged) {
      await step.run("send-nudge", async () => {
        return sendNudgeEmail(event.data.email);
      });
    }
  }
);

// Send events from anywhere
await inngest.send({
  name: "user/signed.up",
  data: { userId: "123", email: "user@example.com" }
});
```

**n8n webhook trigger:**

```
[Webhook: POST /api/webhooks/order]
    ↓
[Switch: event.type]
    ↓ order.created       ↓ order.cancelled
[Process New Order]      [Handle Cancellation]
```

#### Retry and Recovery Pattern

Automatic retry with backoff and dead letter handling.

**When to use:** Any workflow with external dependencies.

**Temporal retry configuration:**

```typescript
const activities = proxyActivities<typeof activitiesType>({
  startToCloseTimeout: '30 seconds',
  retry: {
    initialInterval: '1 second',
    backoffCoefficient: 2,
    maximumInterval: '1 minute',
    maximumAttempts: 5,
    nonRetryableErrorTypes: [
      'ValidationError',
      'InsufficientFunds',
    ]
  }
});
```

**Inngest retry configuration:**

```typescript
export const processPayment = inngest.createFunction(
  {
    id: "process-payment",
    retries: 5,
  },
  { event: "payment/initiated" },
  async ({ event, step, attempt }) => {
    const result = await step.run("charge-card", async () => {
      try {
        return await stripe.charges.create({...});
      } catch (error) {
        if (error.code === 'card_declined') {
          throw new NonRetriableError("Card declined");
        }
        throw error;
      }
    });

    return result;
  }
);
```

**Dead letter handling:**

```typescript
// Inngest: Handle in onFailure
export const myFunction = inngest.createFunction(
  {
    id: "my-function",
    onFailure: async ({ error, event, step }) => {
      await step.run("alert-team", async () => {
        await slack.postMessage({
          channel: "#errors",
          text: `Function failed: ${error.message}`
        });
      });
    }
  },
  { event: "..." },
  async ({ step }) => { ... }
);
```

```
// n8n: Use Error Trigger node
[Error Trigger]
    ↓
[Log to Error Database]
    ↓
[Send Alert to Slack]
    ↓
[Create Ticket in Jira]
```

#### Scheduled Workflow Pattern

Time-based triggers for recurring tasks.

**When to use:** Daily reports, periodic sync, batch processing.

**Inngest cron:**

```typescript
export const dailyReport = inngest.createFunction(
  { id: "daily-report" },
  { cron: "0 9 * * *" },
  async ({ step }) => {
    const data = await step.run("gather-metrics", async () => {
      return gatherDailyMetrics();
    });

    await step.run("generate-report", async () => {
      return generateAndSendReport(data);
    });
  }
);

export const syncInventory = inngest.createFunction(
  { id: "sync-inventory" },
  { cron: "*/15 * * * *" },
  async ({ step }) => {
    await step.run("sync", async () => {
      return syncWithSupplier();
    });
  }
);
```

**Temporal cron workflow:**

```typescript
const handle = await client.workflow.start(dailyReportWorkflow, {
  taskQueue: 'reports',
  workflowId: 'daily-report',
  cronSchedule: '0 9 * * *',
});
```

**n8n schedule trigger:**

```
[Schedule Trigger: Every day at 9:00 AM]
    ↓
[HTTP Request: Get Metrics]
    ↓
[Code Node: Generate Report]
    ↓
[Send Email: Report]
```

### 3. Apply Hard Rules for Production

These rules are **non-negotiable** for money or state-critical workflows. Violating them causes duplicate charges, lost data, or silent failures.

#### RULE 1: Always use idempotency keys for external calls

Durable execution replays workflows from the beginning on restart. If step 3 crashes and the workflow resumes, steps 1 and 2 run again. Without idempotency keys, external services don't know these are retries.

```typescript
// Stripe example — ALWAYS include idempotency_key
await stripe.paymentIntents.create({
  amount: 1000,
  currency: 'usd',
  idempotency_key: `order-${orderId}-payment`
});

// Email example — check before sending
await step.run("send-confirmation", async () => {
  const alreadySent = await checkEmailSent(orderId);
  if (alreadySent) return { skipped: true };
  return sendEmail(customer, orderId);
});

// Database example — use upsert
await db.query(`
  INSERT INTO orders (id, ...) VALUES ($1, ...)
  ON CONFLICT (id) DO NOTHING
`, [orderId]);
```

**Generate idempotency keys from stable inputs, not random values.**

#### RULE 2: Break long workflows into checkpointed steps

A workflow that runs for 24 hours with one step per hour accumulates state for 24h. Workers have memory limits. Functions have execution time limits.

```typescript
// WRONG — one long step, one checkpoint
await step.run("process-all", async () => {
  for (const item of thousandItems) {
    await processItem(item);
  }
});

// CORRECT — many small steps, checkpoint after each
for (const item of thousandItems) {
  await step.run(`process-${item.id}`, async () => {
    return processItem(item);
  });
}

// For very long waits, use sleep (doesn't consume resources)
await step.sleep("wait-for-trial", "14 days");

// Consider child workflows for long processes
await step.invoke("process-batch", {
  function: batchProcessor,
  data: { items: batch }
});
```

#### RULE 3: Always set timeouts on activities

External APIs can hang forever. Without timeout, your workflow waits forever.

```typescript
// Temporal
const activities = proxyActivities<typeof activitiesType>({
  startToCloseTimeout: '30 seconds',
  scheduleToCloseTimeout: '5 minutes',
  heartbeatTimeout: '10 seconds',
  retry: {
    maximumAttempts: 3,
    initialInterval: '1 second',
  }
});

// Inngest
await step.run("call-api", { timeout: "30s" }, async () => {
  return fetch(url, { signal: AbortSignal.timeout(25000) });
});
```

```json
// AWS Step Functions
{
  "Type": "Task",
  "TimeoutSeconds": 30,
  "HeartbeatSeconds": 10,
  "Resource": "arn:aws:lambda:..."
}
```

**Rule: Activity timeout < Workflow timeout.**

#### RULE 4: No side effects outside step/activity boundaries

Workflow code runs on EVERY replay. Random IDs, current time, and direct API calls in workflow code break determinism.

```typescript
// WRONG — side effects in workflow code
export async function orderWorkflow(order) {
  const orderId = uuid();        // Different every replay!
  const now = new Date();        // Different every replay!
  await activities.process(orderId, now);
}

// CORRECT — side effects in activities
export async function orderWorkflow(order) {
  const orderId = await activities.generateOrderId();
  const now = await activities.getCurrentTime();
  await activities.process(orderId, now);
}

// ALSO CORRECT — Temporal sideEffect and workflow.now()
import { sideEffect } from '@temporalio/workflow';
const orderId = await sideEffect(() => uuid());
const now = workflow.now();
```

**Safe in workflow code:** Reading function arguments, simple calculations (no randomness), logging (usually).

#### RULE 5: Always use exponential backoff for retries

When a service is struggling, immediate retries make it worse. 100 workflows retrying instantly = 100 requests hitting a service that's already failing.

```typescript
// Temporal
const activities = proxyActivities({
  retry: {
    initialInterval: '1 second',
    backoffCoefficient: 2,        // 1s, 2s, 4s, 8s, 16s...
    maximumInterval: '1 minute',
    maximumAttempts: 5,
  }
});

// Inngest (built-in exponential backoff)
{
  id: "my-function",
  retries: 5,
}

// Manual backoff with jitter
const backoff = (attempt) => {
  const base = 1000;
  const max = 60000;
  const delay = Math.min(base * Math.pow(2, attempt), max);
  const jitter = delay * 0.1 * Math.random();
  return delay + jitter;
};
```

**Always add jitter to prevent thundering herd.**

#### RULE 6: Store references, not large data, in workflow state

Workflow state is persisted and replayed. A 10MB payload is stored, serialized, and deserialized on every step. Some platforms have hard limits (Step Functions: 256KB).

```typescript
// WRONG — large data in workflow
await step.run("fetch-data", async () => {
  const largeDataset = await fetchAllRecords();  // 100MB!
  return largeDataset;
});

// CORRECT — store reference
await step.run("fetch-data", async () => {
  const largeDataset = await fetchAllRecords();
  const s3Key = await uploadToS3(largeDataset);
  return { s3Key };
});

const processed = await step.run("process-data", async () => {
  const data = await downloadFromS3(fetchResult.s3Key);
  return processData(data);
});
```

#### RULE 7: Every production workflow needs a failure handler

Even with retries, some workflows will fail permanently. Without dead letter handling, failed workflows silently disappear.

```typescript
// Inngest onFailure handler
export const myFunction = inngest.createFunction(
  {
    id: "process-order",
    onFailure: async ({ error, event, step }) => {
      await step.run("log-error", () =>
        sentry.captureException(error, { extra: { event } })
      );
      await step.run("alert", () =>
        slack.postMessage({
          channel: "#alerts",
          text: `Order ${event.data.orderId} failed: ${error.message}`
        })
      );
      await step.run("queue-review", () =>
        db.insert(failedOrders, { orderId, error, event })
      );
    }
  },
  { event: "order/created" },
  async ({ event, step }) => { ... }
);
```

```
// n8n Error Trigger — every production workflow needs this
[Error Trigger]
    ↓
[Set: Extract Error Details]
    ↓
[HTTP: Log to Error Service]
    ↓
[Slack/Email: Alert Team]
```

#### RULE 8: Add heartbeats to long-running Temporal activities

For any activity > 10 seconds, add heartbeat. Without heartbeat, Temporal can't tell if activity is working or stuck.

```typescript
import { heartbeat, activityInfo } from '@temporalio/activity';

export async function processLargeFile(fileUrl: string): Promise<void> {
  const chunks = await downloadChunks(fileUrl);

  for (let i = 0; i < chunks.length; i++) {
    const { cancelled } = activityInfo();
    if (cancelled) {
      throw new CancelledFailure('Activity cancelled');
    }

    await processChunk(chunks[i]);
    heartbeat({ progress: (i + 1) / chunks.length });
  }
}

// Configure heartbeat timeout
const activities = proxyActivities({
  startToCloseTimeout: '10 minutes',
  heartbeatTimeout: '30 seconds',
});
```

## Pitfalls

### CRITICAL: Non-Idempotent Steps in Durable Workflows

**Symptoms:** Customer charged twice. Email sent three times. Database record created multiple times.

**Cause:** Durable execution replays workflows from the beginning on restart. Without idempotency keys, external services process retries as new requests.

**Fix:** See RULE 1 above. Always use idempotency keys derived from stable inputs.

### CRITICAL: Side Effects Outside Step/Activity Boundaries

**Symptoms:** Random failures on replay. "Workflow corrupted" errors. Different behavior on replay than initial run. Non-determinism errors.

**Cause:** Workflow code runs on every replay. `uuid()`, `Date.now()`, `new Date()`, and direct API calls produce different values/results each replay.

**Fix:** See RULE 4 above. Move all side effects into activities/steps or use `sideEffect()`.

### HIGH: Workflow Runs for Hours/Days Without Checkpoints

**Symptoms:** Memory consumption grows. Worker timeouts. Lost progress after crashes. "Workflow exceeded maximum duration" errors.

**Cause:** Workflows hold state in memory until checkpointed. One long step = one checkpoint for hours of work.

**Fix:** See RULE 2 above. Break into many small steps. Use `sleep` for long waits.

### HIGH: Activities Without Timeout Configuration

**Symptoms:** Workflows hang indefinitely. Worker pool exhausted. Dead workflows that never complete or fail.

**Cause:** External APIs can hang forever. Most platforms don't set default timeouts on activities.

**Fix:** See RULE 3 above. Always set `startToCloseTimeout`. Rule: activity timeout < workflow timeout.

### HIGH: Storing Large Data in Workflow State

**Symptoms:** Slow workflow execution. Memory errors. "Payload too large" errors. Expensive storage costs. Slow replays.

**Cause:** Workflow state is persisted and replayed on every step. Step Functions has a 256KB hard limit.

**Fix:** See RULE 6 above. Store data in S3/DB, return only references.

### HIGH: Missing Dead Letter Queue or Failure Handler

**Symptoms:** Failed workflows silently disappear. No alerts when things break. Customer issues discovered days later.

**Cause:** Even with retries, some workflows fail permanently. Without failure handling, there's no alert, no data, no recovery path.

**Fix:** See RULE 7 above. Add `onFailure` handler (Inngest), Error Trigger (n8n), or failure signal (Temporal).

### MEDIUM: Retry Configuration Without Exponential Backoff

**Symptoms:** Overwhelming failing services. Rate limiting. Cascading failures. Retry storms causing outages.

**Cause:** Immediate retries on a struggling service make it worse.

**Fix:** See RULE 5 above. Always use exponential backoff with jitter.

### MEDIUM: n8n Workflow Without Error Trigger

**Symptoms:** Workflow fails silently. Errors only visible in execution logs. No alerts, no recovery, no visibility.

**Cause:** n8n doesn't notify on failure by default. Without an Error Trigger node, production failures go unnoticed.

**Fix:** Every production n8n workflow needs: (1) Error Trigger node, (2) connected error handling chain (log → alert → ticket), (3) consider dead letter pattern with Redis/Postgres for failed jobs.

### MEDIUM: Long-Running Temporal Activities Without Heartbeat

**Symptoms:** Activity timeouts even when work is progressing. Lost work when workers restart. Can't cancel long-running activities.

**Cause:** Temporal detects stuck activities via heartbeat. Without heartbeat, long activities appear hung.

**Fix:** See RULE 8 above. Add `heartbeat()` calls for any activity > 10 seconds. Set `heartbeatTimeout`.

## Verification

Run these checks against any workflow code before considering it production-ready:

### 1. Idempotency Key Check

**Check:** Search all payment/external mutation calls for `idempotency_key` or equivalent.

```powershell
# PowerShell — search for Stripe calls missing idempotency_key
Select-String -Path "src\**\*.ts" -Pattern "stripe\.(paymentIntents|charges|refunds)\.create" |
  ForEach-Object { $_.Path + ":" + $_.LineNumber }
```

**Expected:** Every payment call includes `idempotency_key`. If missing → ERROR.

### 2. Timeout Check

**Check:** All `proxyActivities` calls include `startToCloseTimeout`.

```powershell
Select-String -Path "src\**\*.ts" -Pattern "proxyActivities" -Context 0,5
```

**Expected:** Every `proxyActivities` block has `startToCloseTimeout`. If missing → ERROR.

### 3. Determinism Check

**Check:** No `uuid()`, `Math.random()`, `Date.now()`, or `new Date()` in workflow code (outside activities/steps).

```powershell
Select-String -Path "src\workflows\**\*.ts" -Pattern "uuid\(\)|Math\.random|Date\.now|new Date\(\)"
```

**Expected:** Zero matches in workflow files. If found → ERROR. Move to activity or use `sideEffect()`.

### 4. Failure Handler Check

**Check:** All Inngest production functions have `onFailure`. All n8n production workflows have Error Trigger.

```powershell
Select-String -Path "src\**\*.ts" -Pattern "inngest\.createFunction" -Context 0,3
```

**Expected:** Every `createFunction` includes `onFailure` handler. If missing → WARNING.

### 5. Backoff Check

**Check:** All retry configurations include `backoffCoefficient` and `initialInterval` (Temporal) or rely on built-in backoff (Inngest).

```powershell
Select-String -Path "src\**\*.ts" -Pattern "maximumAttempts|retries:" -Context 0,5
```

**Expected:** Retry config includes backoff parameters. If missing → WARNING.

### 6. Large Data Check

**Check:** No step returns raw large datasets. Steps should return references (S3 keys, DB IDs).

```powershell
Select-String -Path "src\**\*.ts" -Pattern "return.*await.*fetchAll|return.*largeDataset"
```

**Expected:** Zero matches. If found → INFO. Consider storing in S3/DB and returning reference.

### 7. Heartbeat Check (Temporal)

**Check:** Activities running > 10 seconds include `heartbeat()` calls.

```powershell
Select-String -Path "src\activities\**\*.ts" -Pattern "heartbeat"
```

**Expected:** Long-running activities call `heartbeat()`. If missing for activities > 10s → WARNING.

## Related Skills

Works well with:
- `multi-agent-orchestration` — workflow provides infrastructure, orchestration provides patterns
- `agent-tool-builder` — tools that workflows can invoke as activities
- `backend` — API design for workflow steps
- `devops` — CI/CD pipeline automation
- `zapier-make-patterns` — no-code automation platform integration
- `browser-automation` — Playwright/Puppeteer activities in workflows
- `computer-use-agents` — desktop automation activities
- `llm-architect` — AI-powered workflow steps

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
