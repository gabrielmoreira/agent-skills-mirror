# API Routes

Next.js API routes for external integrations, webhooks, and health checks. Core data operations are handled by Convex.

## Structure

```
api/
├── health/
│   └── route.ts        # Health check endpoint
├── webhooks/           # (future) Webhook handlers
│   └── {service}/
│       └── route.ts
└── CLAUDE.md           # This file
```

## Purpose

These API routes handle:

- **Health checks** - `/api/health` for orchestration and monitoring
- **Webhooks** - Receiving callbacks from external services (future)
- **External integrations** - APIs for external systems to interact with Clawe (future)

Core data (agents, tasks, messages) is managed by Convex, not these API routes.

## Conventions

### Route Handlers

Use the App Router convention with `route.ts` files:

```typescript
// app/api/health/route.ts
import { NextResponse } from "next/server";

export const GET = () => {
  return NextResponse.json({ status: "ok" });
};

export const POST = async (request: Request) => {
  const body = await request.json();
  // Handle POST request
  return NextResponse.json({ received: true });
};
```

### Response Format

Always return JSON responses:

```typescript
// Success
return NextResponse.json({ data: result });

// Error
return NextResponse.json({ error: "Something went wrong" }, { status: 400 });
```

### Webhook Handlers

For webhooks, verify signatures when applicable:

```typescript
// app/api/webhooks/stripe/route.ts
export const POST = async (request: Request) => {
  const signature = request.headers.get("stripe-signature");
  // Verify signature before processing
  // ...
};
```

## Code Style

- Use const arrow functions for handlers
- Use named exports (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`)
- Keep handlers thin - delegate complex logic to separate functions
- **Use strong typing** - type request bodies and responses

## Environment Variables

For webhook secrets and external API keys:

```bash
STRIPE_WEBHOOK_SECRET=whsec_...
GITHUB_WEBHOOK_SECRET=...
```

Access via `process.env.VARIABLE_NAME` in route handlers.

## Testing

**Convention:** Test files live alongside route files.

```
api/
├── health/
│   ├── route.ts
│   └── route.spec.ts       # Tests for health endpoint
├── webhooks/
│   └── stripe/
│       ├── route.ts
│       └── route.spec.ts   # Tests for webhook handler
```

### Route Test Example

```typescript
// api/health/route.spec.ts
import { describe, it, expect } from "vitest";
import { GET } from "./route";

describe("GET /api/health", () => {
  it("returns ok status", async () => {
    const response = await GET();
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.status).toBe("ok");
  });
});
```

### Webhook Test Example

```typescript
// api/webhooks/stripe/route.spec.ts
import { describe, it, expect, vi } from "vitest";
import { POST } from "./route";

describe("POST /api/webhooks/stripe", () => {
  it("rejects invalid signature", async () => {
    const request = new Request("http://localhost/api/webhooks/stripe", {
      method: "POST",
      headers: { "stripe-signature": "invalid" },
      body: JSON.stringify({ type: "test" }),
    });

    const response = await POST(request);
    expect(response.status).toBe(401);
  });

  it("processes valid webhook", async () => {
    // Mock signature verification
    vi.mock("stripe", () => ({
      webhooks: {
        constructEvent: vi
          .fn()
          .mockReturnValue({ type: "payment_intent.succeeded" }),
      },
    }));

    const request = new Request("http://localhost/api/webhooks/stripe", {
      method: "POST",
      headers: { "stripe-signature": "valid-sig" },
      body: JSON.stringify({ type: "payment_intent.succeeded" }),
    });

    const response = await POST(request);
    expect(response.status).toBe(200);
  });
});
```

### What to Test

- **Health endpoints** - Always return expected format
- **Webhook handlers** - Signature verification, event processing
- **Error responses** - Proper status codes and error messages
- **Input validation** - Reject malformed requests
