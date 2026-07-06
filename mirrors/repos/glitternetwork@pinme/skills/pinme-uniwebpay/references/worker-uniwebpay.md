# Worker UniwebPay Reference

Use this file when implementing concrete Cloudflare Worker TypeScript code for PinMe UniwebPay payments.

## Install

Install the SDK only when Worker code imports it. Pick the package manager from the existing lockfile.

```bash
pnpm add @uniwebpay/sdk
npm install @uniwebpay/sdk
yarn add @uniwebpay/sdk
bun add @uniwebpay/sdk
```

## Core Helpers

```typescript
import Uniweb from "@uniwebpay/sdk";

export interface Env {
  UNIWEB_SECRET: string;
  UNIWEB_API_URL?: string;
  UNIWEB_PAY_URL?: string;
  UNIWEB_WALLET_ID?: string;
  PROJECT_NAME?: string;
  DB?: D1Database;
  UNIWEB_WEBHOOK_SECRET?: string;
}

type PaymentMethod = "card" | "wechat" | "alipay" | "paynow";

const VALID_PAYMENT_METHODS = new Set<PaymentMethod>(["card", "wechat", "alipay", "paynow"]);

function uniwebClient(env: Env): Uniweb {
  return new Uniweb(env.UNIWEB_SECRET, {
    baseUrl: env.UNIWEB_API_URL,
    payUrl: env.UNIWEB_PAY_URL,
  });
}

function json(data: unknown, init: ResponseInit = {}): Response {
  const headers = new Headers(init.headers);
  headers.set("content-type", "application/json; charset=utf-8");

  return Response.json(data, {
    ...init,
    headers,
  });
}

async function readJSON<T>(request: Request): Promise<T> {
  try {
    return (await request.json()) as T;
  } catch {
    throw new Error("Invalid JSON body");
  }
}

function assertAmountCents(value: unknown): number {
  const amount = Number(value);
  if (!Number.isInteger(amount) || amount < 10) {
    throw new Error("amountCents must be an integer minor-unit amount >= 10");
  }
  return amount;
}

function normalizeCurrency(value: unknown): string {
  const currency = String(value || "SGD").toUpperCase();
  if (!/^[A-Z]{3}$/.test(currency)) throw new Error("currency must be an ISO 4217 code");
  return currency;
}

function defaultPaymentMethods(currency: string): PaymentMethod[] {
  if (currency === "SGD") return ["card", "wechat", "alipay", "paynow"];
  if (currency === "CNY") return ["card", "wechat", "alipay"];
  return ["card"];
}

function normalizePaymentMethods(value: unknown, currency: string): PaymentMethod[] {
  const requested = Array.isArray(value) && value.length > 0 ? value : defaultPaymentMethods(currency);
  const methods = requested.map((method) => String(method).toLowerCase() as PaymentMethod);

  for (const method of methods) {
    if (!VALID_PAYMENT_METHODS.has(method)) {
      throw new Error("paymentMethodTypes contains an unsupported method");
    }
    if (method === "paynow" && currency !== "SGD") {
      throw new Error("PayNow is only supported for SGD payments");
    }
    if ((method === "wechat" || method === "alipay") && !["SGD", "CNY"].includes(currency)) {
      throw new Error("WeChat Pay and Alipay are only supported for SGD or CNY payments");
    }
  }

  return Array.from(new Set(methods));
}

function paymentUrl(payload: { url?: string; paymentUrl?: string }): string {
  const url = payload.url || payload.paymentUrl;
  if (!url) throw new Error("UniwebPay response missing payment URL");
  return url;
}

function projectWebhookUrl(request: Request, path = "/api/pay/webhook"): string {
  return new URL(path, request.url).toString();
}
```

## Payment Link Route

Use this for a simple one-time payment link. It is the lightest Worker integration.

```typescript
type CreatePaymentLinkBody = {
  orderId?: string;
  amountCents: number;
  currency?: string;
  name?: string;
  description?: string;
  successUrl?: string;
  cancelUrl?: string;
  paymentMethodTypes?: PaymentMethod[];
};

async function createPaymentLink(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") return json({ error: "method not allowed" }, { status: 405 });

  let input: CreatePaymentLinkBody;
  try {
    input = await readJSON<CreatePaymentLinkBody>(request);
  } catch (err) {
    return json({ error: (err as Error).message }, { status: 400 });
  }

  const orderId = input.orderId || crypto.randomUUID();
  const amount = assertAmountCents(input.amountCents);
  const currency = normalizeCurrency(input.currency);
  const paymentMethodTypes = normalizePaymentMethods(input.paymentMethodTypes, currency);
  const webhookUrl = projectWebhookUrl(request);
  const uniweb = uniwebClient(env);

  try {
    const link = await uniweb.links.create({
      amount,
      currency,
      name: input.name || "Payment",
      description: input.description,
      successUrl: input.successUrl,
      cancelUrl: input.cancelUrl,
      webhookUrl,
      paymentMethodTypes,
      metadata: {
        orderId,
        projectName: env.PROJECT_NAME,
      },
    });

    return json({
      orderId,
      linkId: link.id,
      url: paymentUrl(link as { url?: string; paymentUrl?: string }),
      walletId: env.UNIWEB_WALLET_ID,
    });
  } catch (err) {
    return json({ error: "failed to create payment link" }, { status: 502 });
  }
}
```

## Checkout Session Route

Use this when checkout is dynamic and should expire after 24 hours. Checkout sessions need a price. For truly stable catalog items, create products/prices once and store the `priceId`; do not create a new product/price for every page view.

```typescript
type CreateCheckoutBody = {
  orderId?: string;
  productName: string;
  amountCents: number;
  currency?: string;
  successUrl: string;
  cancelUrl: string;
  customerEmail?: string;
  quantity?: number;
  paymentMethodTypes?: PaymentMethod[];
};

async function createCheckoutSession(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") return json({ error: "method not allowed" }, { status: 405 });

  let input: CreateCheckoutBody;
  try {
    input = await readJSON<CreateCheckoutBody>(request);
  } catch (err) {
    return json({ error: (err as Error).message }, { status: 400 });
  }

  const orderId = input.orderId || crypto.randomUUID();
  const amount = assertAmountCents(input.amountCents);
  const currency = normalizeCurrency(input.currency);
  const quantity = Math.max(1, Math.floor(Number(input.quantity || 1)));
  const paymentMethodTypes = normalizePaymentMethods(input.paymentMethodTypes, currency);
  const webhookUrl = projectWebhookUrl(request);
  const uniweb = uniwebClient(env);

  try {
    const product = await uniweb.products.create({
      name: input.productName,
      webhookUrl,
      metadata: { orderId, projectName: env.PROJECT_NAME },
    });

    const price = await uniweb.prices.create({
      productId: product.id,
      amount,
      currency,
      type: "one_time",
      metadata: { orderId, projectName: env.PROJECT_NAME },
    });

    const session = await uniweb.checkout.create({
      mode: "payment",
      lineItems: [{ priceId: price.id, quantity }],
      successUrl: input.successUrl,
      cancelUrl: input.cancelUrl,
      customerEmail: input.customerEmail,
      paymentMethodTypes,
      metadata: { orderId, projectName: env.PROJECT_NAME },
    });

    if (env.DB) {
      await env.DB.prepare(
        `INSERT INTO orders(order_id, checkout_session_id, status, amount_cents, currency, created_at)
         VALUES (?, ?, 'pending', ?, ?, ?)
         ON CONFLICT(order_id) DO UPDATE SET checkout_session_id = excluded.checkout_session_id`,
      )
        .bind(orderId, session.id, amount * quantity, currency, Math.floor(Date.now() / 1000))
        .run();
    }

    return json({
      orderId,
      checkoutSessionId: session.id,
      url: paymentUrl(session as { url?: string; paymentUrl?: string }),
      walletId: env.UNIWEB_WALLET_ID,
    });
  } catch (err) {
    return json({ error: "failed to create checkout session" }, { status: 502 });
  }
}
```

## D1 Schema

Use only if the target Worker already has D1 or the user asks for persistence.

```sql
CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY,
  checkout_session_id TEXT UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  amount_cents INTEGER NOT NULL,
  currency TEXT NOT NULL,
  paid_at INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER
);

CREATE TABLE IF NOT EXISTS payment_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  order_id TEXT,
  raw_payload TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
```

## Optional Webhook Route

PinMe injects `UNIWEB_WEBHOOK_SECRET` after UniwebPay credentials and the wallet webhook secret are provisioned, then the Worker is redeployed. Keep the Env binding optional for projects that have not been provisioned or redeployed yet, but generate verified webhook handling by default when payment fulfillment depends on webhooks.

Add the verifier import next to the `Uniweb` import at the top of the Worker file:

```typescript
import { verifyWebhook } from "@uniwebpay/sdk";
```

```typescript
async function handleUniwebWebhook(request: Request, env: Env): Promise<Response> {
  if (request.method !== "POST") return json({ error: "method not allowed" }, { status: 405 });
  if (!env.UNIWEB_WEBHOOK_SECRET) {
    return json({ error: "webhook verification is not configured" }, { status: 501 });
  }

  const rawBody = await request.text();
  let event: any;

  try {
    event = await verifyWebhook(
      rawBody,
      request.headers.get("uniweb-Signature") || "",
      env.UNIWEB_WEBHOOK_SECRET,
    );
  } catch {
    return json({ error: "invalid signature" }, { status: 400 });
  }

  try {
    if (env.DB) {
      const orderId = String(event?.data?.object?.metadata?.orderId || "");
      await env.DB.prepare(
        `INSERT INTO payment_events(event_id, event_type, order_id, raw_payload, created_at)
         VALUES (?, ?, ?, ?, ?)
         ON CONFLICT(event_id) DO NOTHING`,
      )
        .bind(event.id, event.type, orderId, rawBody, Math.floor(Date.now() / 1000))
        .run();

      if (event.type === "payment.succeeded" && orderId) {
        await env.DB.prepare(
          `UPDATE orders SET status = 'paid', paid_at = ?, updated_at = ? WHERE order_id = ? AND status != 'paid'`,
        )
          .bind(Math.floor(Date.now() / 1000), Math.floor(Date.now() / 1000), orderId)
          .run();
      }
    }

    return json({ ok: true });
  } catch {
    return json({ error: "processing error" }, { status: 500 });
  }
}
```

Rules:

- Read the raw body exactly once before verification.
- Return 400 for bad signatures so UniwebPay does not retry impossible deliveries.
- Return 500 for temporary processing failures so UniwebPay can retry.
- Make event handling idempotent with `event.id`.
- Check amount, currency, metadata, and current order state before granting access.

## Minimal Router

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/pay/link") return createPaymentLink(request, env);
    if (url.pathname === "/api/pay/checkout") return createCheckoutSession(request, env);
    if (url.pathname === "/api/pay/webhook") return handleUniwebWebhook(request, env);

    return json({ error: "not found" }, { status: 404 });
  },
};
```

## Common Mistakes

- Do not use `process.env` in Cloudflare Workers; use the `env` argument.
- Do not put `UNIWEB_SECRET` or `UNIWEB_WEBHOOK_SECRET` in `wrangler.toml`. PinMe injects them during deployment. For local dev, use an uncommitted `.dev.vars` only.
- Do not omit `webhookUrl` on payment links or products when the project expects webhook-driven fulfillment.
- Do not call `uniweb.webhooks.set`, `uniweb.webhooks.remove`, `uniweb.webhooks.rollSecret`, `uniweb.wallet.update`, refunds, payouts, or subscription mutation APIs unless the user explicitly asks for that flow and the route has project/admin authorization.
- Do not mark orders paid from `successUrl` alone.
- Do not import the SDK in browser-side code.
