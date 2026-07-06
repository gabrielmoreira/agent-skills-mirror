---
name: pinme-uniwebpay
description: Use when generating, modifying, or reviewing PinMe Cloudflare Worker TypeScript code that accepts payments through UniwebPay. The target app is a PinMe Worker project where PinMe injects UNIWEB_* bindings and the Worker calls UniwebPay directly with @uniwebpay/sdk. Covers Env bindings, SDK client setup, payment links, products/prices, checkout sessions, payment status reads, refunds/subscriptions/webhooks when requested, and PinMe-specific deployment/security rules.
---

# PinMe UniwebPay

Build PinMe Worker payment code that uses `@uniwebpay/sdk` directly from the Worker runtime. PinMe provisions the user's UniwebPay wallet/server key and injects environment bindings during Worker deployment; Worker code should not call PinMe payment proxy routes for UniwebPay checkout.

For SDK surface, request shapes, payment method rules, webhook verification, and CLI behavior, use:

`/Users/didi/vibecash/skills/skills/uniwebpay/SKILL.md`

For concrete Cloudflare Worker TypeScript helpers, routes, D1 schema, and webhook examples, use:

`references/worker-uniwebpay.md`

The UniwebPay skill is the source of truth for how to use UniwebPay and `@uniwebpay/sdk`. This skill adds the PinMe Worker-specific contract.

## First Steps

1. Inspect the target Worker project: `package.json`, lockfile, `wrangler.toml`, source entrypoint, routing style, D1 migrations, and existing helper conventions.
2. If Worker code imports the SDK and `@uniwebpay/sdk` is missing, install it with the existing package manager.
3. Use the UniwebPay SDK skill above for concrete SDK methods and request payloads.
4. Keep code Cloudflare Worker-compatible. Do not add Express, Node-only body parsers, Node-only globals, or browser-side SDK imports.

## PinMe Env Contract

Use this `Env` shape unless the project already has a compatible one:

```typescript
export interface Env {
  UNIWEB_SECRET: string;
  UNIWEB_API_URL?: string;
  UNIWEB_PAY_URL?: string;
  UNIWEB_WALLET_ID?: string;
  PROJECT_NAME?: string;
  DB?: D1Database;
  UNIWEB_WEBHOOK_SECRET?: string;
}
```

PinMe injects these bindings after UniwebPay credentials exist and the Worker is deployed:

- `UNIWEB_SECRET`: full-access PinMe-provisioned `sk_server_`, server-side Worker secret.
- `UNIWEB_API_URL`: UniwebPay API endpoint override.
- `UNIWEB_PAY_URL`: UniwebPay checkout/payment host override.
- `UNIWEB_WALLET_ID`: user-level wallet id for diagnostics and reconciliation.
- `UNIWEB_WEBHOOK_SECRET`: user wallet-level `whsec_` used to verify UniwebPay webhook signatures.
- `PROJECT_NAME`: PinMe project name.

PinMe does not inject the full wallet secret (`sk_live_`). Do not ask the user for it and do not add it to Worker code, `wrangler.toml`, `.dev.vars`, responses, logs, D1 rows, or frontend bundles.

## SDK Pattern

Always import and instantiate the SDK server-side:

```typescript
import Uniweb from "@uniwebpay/sdk";

function uniwebClient(env: Env): Uniweb {
  return new Uniweb(env.UNIWEB_SECRET, {
    baseUrl: env.UNIWEB_API_URL,
    payUrl: env.UNIWEB_PAY_URL,
  });
}
```

Use SDK methods from the UniwebPay SDK skill. Common PinMe Worker flows:

- Fixed one-time collection: `uniweb.links.create(...)`, return the payment link URL.
- Stable product/price: `uniweb.products.create(...)`, `uniweb.prices.create(...)`, return/store the permanent `paymentUrl`.
- Dynamic cart/order: create or reuse a price, then call `uniweb.checkout.create(...)` and return `session.url`.
- Payment reads: `uniweb.payments.get(...)` / `list(...)` only from server routes.
- Refunds, subscription mutations, wallet/webhook setup, payouts, KYC, and bank account APIs are allowed only when the user explicitly requests that business flow and the Worker code has proper validation, persistence, and authorization.

Amounts are integer minor units. Default currency is `SGD` unless the app has a stronger existing convention.

## SDK Interface Cheatsheet

PinMe injects a full-access server-side `sk_server_`. Worker server code can call the UniwebPay SDK surface, but generate only the routes the app needs, and validate authorization and inputs before calling money-moving or account-management APIs.

Products:

```typescript
await uniweb.products.create({ name, description?, webhookUrl?, metadata? });
await uniweb.products.list({ limit?, startingAfter? });
await uniweb.products.get(productId);
await uniweb.products.update(productId, { name?, description?, webhookUrl?, active?, metadata? });
await uniweb.products.del(productId);
for await (const product of uniweb.products.listAll()) {}
```

Prices:

```typescript
await uniweb.prices.create({
  productId,
  amount,        // integer minor units
  currency,      // e.g. "SGD"
  type,          // "one_time" | "recurring"
  interval?,     // "day" | "week" | "month" | "year"; recurring only
  intervalCount?,
  trialPeriodDays?,
  metadata?,
});
await uniweb.prices.list({ productId?, limit?, startingAfter? });
await uniweb.prices.get(priceId);
await uniweb.prices.update(priceId, { active });
await uniweb.prices.activate(priceId);
await uniweb.prices.deactivate(priceId);
for await (const price of uniweb.prices.listAll({ productId? })) {}
```

Checkout sessions:

```typescript
await uniweb.checkout.create({
  mode,           // "payment" | "subscription"
  lineItems: [{ priceId, quantity }],
  successUrl?,
  cancelUrl?,
  customerEmail?,
  customerId?,
  trialPeriodDays?,
  paymentMethodTypes?, // ["card", "wechat", "alipay", "paynow"]
  metadata?,
});
await uniweb.checkout.list({ limit?, startingAfter? });
await uniweb.checkout.get(checkoutSessionId);
```

Checkout session URLs are one-time and expire after 24 hours. For subscriptions, use card-only payment methods unless the upstream SDK skill says otherwise.

Payments:

```typescript
await uniweb.payments.create({ amount, currency, customerId?, metadata? });
await uniweb.payments.list({ status?, customerId?, limit?, startingAfter? });
await uniweb.payments.get(paymentId, { gateway? });
await uniweb.payments.listRefunds(paymentId);
await uniweb.payments.sync(paymentId);
await uniweb.payments.void(paymentId);
for await (const payment of uniweb.payments.listAll({ status?, customerId? })) {}
```

Use payment reads for server-side status checks. Do not mark local orders paid until amount, currency, metadata, and order state match expectations.

Refunds:

```typescript
await uniweb.refunds.create({
  paymentId,
  amount?,            // omit for full refund when appropriate
  reason?,
  offlineRefundFlag?,
});
await uniweb.refunds.get(refundId, { gateway? });
```

Customers:

```typescript
await uniweb.customers.create({ email, name?, metadata? });
await uniweb.customers.list({ email?, limit?, startingAfter? });
await uniweb.customers.get(customerId);
await uniweb.customers.update(customerId, { email?, name?, metadata? });
await uniweb.customers.del(customerId);
for await (const customer of uniweb.customers.listAll({ email? })) {}
```

Subscriptions:

```typescript
await uniweb.subscriptions.create({ customerId, priceId, paymentMethodId?, trialPeriodDays?, metadata? });
await uniweb.subscriptions.list({ customerId?, status?, limit?, startingAfter? });
await uniweb.subscriptions.get(subscriptionId);
await uniweb.subscriptions.update(subscriptionId, { cancelAtPeriodEnd? });
await uniweb.subscriptions.cancel(subscriptionId); // cancel immediately
await uniweb.subscriptions.resume(subscriptionId); // undo cancel-at-period-end
for await (const subscription of uniweb.subscriptions.listAll({ customerId?, status? })) {}
```

Expected subscription states include `trialing`, `active`, `past_due`, `unpaid`, and `canceled`. Update access from verified webhook events or a trusted server reconciliation job.

Payment links:

```typescript
await uniweb.links.create({
  amount,
  currency,
  name?,
  description?,
  successUrl?,
  cancelUrl?,
  webhookUrl?,
  paymentMethodTypes?,
  metadata?,
});
await uniweb.links.list({ limit?, startingAfter? });
await uniweb.links.get(paymentLinkId);
await uniweb.links.update(paymentLinkId, {
  name?,
  description?,
  successUrl?,
  cancelUrl?,
  webhookUrl?,
  active?,
});
await uniweb.links.deactivate(paymentLinkId);
for await (const link of uniweb.links.listAll()) {}
```

Payment links are reusable permanent `/p/` URLs for one-time payment collection.

Wallet:

```typescript
await uniweb.wallet.current();
await uniweb.wallet.update({ merchantName?, merchantCity?, merchantCountry?, webhookUrl? });
```

Wallet changes affect the user's shared Uniweb wallet. Only generate wallet mutation routes when the user explicitly asks for wallet administration, and protect those routes with project/admin authorization.

Webhooks:

```typescript
await uniweb.webhooks.set(url);       // returns webhook data; store webhookSecret when returned
await uniweb.webhooks.info();         // current wallet webhook URL and hasSecret
await uniweb.webhooks.remove();
await uniweb.webhooks.rollSecret();   // returns new webhookSecret when available
```

The webhook signing secret is wallet-level. PinMe injects the same `UNIWEB_WEBHOOK_SECRET` into all projects owned by the same PinMe user after UniwebPay credentials and the wallet webhook secret are provisioned. Business webhook URLs do not need to be shared across projects: when creating payment links or products, pass the project Worker webhook URL as `webhookUrl`. Do not call `uniweb.webhooks.set`, `uniweb.webhooks.remove`, or `uniweb.webhooks.rollSecret` from ordinary project routes because they mutate the shared wallet fallback webhook and can rotate the shared secret.

## PinMe Security Rules

- Never expose `env.UNIWEB_SECRET`, `env.UNIWEB_WEBHOOK_SECRET`, or any Uniweb secret in responses, logs, metadata, test snapshots, or D1.
- Do not put `UNIWEB_SECRET` or `UNIWEB_WEBHOOK_SECRET` in source code, committed `wrangler.toml`, committed `.dev.vars`, or browser code.
- Do not call old VibeCash APIs or PinMe VibeCash proxy routes.
- Do not call PinMe payment APIs with `X-API-Key` for UniwebPay checkout. The Worker calls UniwebPay directly through the SDK.
- Treat `successUrl` and `cancelUrl` as UX only. Grant access only after verified webhook processing or another explicit server-side verification path.
- Validate user input before SDK calls: amount, currency, quantity, product/price IDs, payment method types, order ownership, and metadata shape.
- For D1-backed orders, persist a pending order before or immediately after creating the link/session, then make fulfillment idempotent.

## Webhooks

PinMe automatically injects `UNIWEB_WEBHOOK_SECRET` after UniwebPay credentials and the wallet webhook secret are provisioned, then the Worker is redeployed. Keep the binding optional in TypeScript because new projects can exist before UniwebPay provisioning or before redeploy.

PinMe may maintain a managed wallet-level fallback webhook URL only to obtain and preserve the signing secret. That fallback is not the project's business webhook endpoint. To route business events to the current Worker project, set a project-specific `webhookUrl` when creating UniwebPay payment links or products.

When implementing webhooks:

- Use `verifyWebhook` from `@uniwebpay/sdk`.
- Read the raw request body exactly once with `request.text()`.
- Use the `uniweb-Signature` header.
- Return `400` for invalid signatures.
- Return `500` for temporary processing failures so UniwebPay retries.
- Enforce idempotency with `event.id`, payment id, checkout session id, or the app's order id.
- Before fulfillment, verify expected amount, currency, metadata, and current order state.

## Persistence Guidance

Only add D1 tables/migrations when the project already uses D1 or the user asks for persistence.

For order flows, store at least:

- local order id
- Uniweb payment link id, checkout session id, payment id, or subscription id as applicable
- amount and currency
- status
- created/updated timestamps
- processed webhook event ids for idempotency

Do not store API keys, webhook secrets, or `UNIWEB_SECRET`.

## Finish Checklist

- `@uniwebpay/sdk` is installed only when Worker/server code imports it.
- `Env` includes the PinMe-injected `UNIWEB_*` bindings used by the code.
- SDK usage follows `/Users/didi/vibecash/skills/skills/uniwebpay/SKILL.md`.
- Code uses `new Uniweb(env.UNIWEB_SECRET, { baseUrl: env.UNIWEB_API_URL, payUrl: env.UNIWEB_PAY_URL })`.
- No VibeCash or PinMe payment proxy routes are used for UniwebPay checkout.
- No secret is exposed in source, responses, logs, D1, tests, or docs.
- Amounts and currencies are validated as integer minor-unit payments.
- Fulfillment does not rely on browser redirects.
- Webhook code is raw-body based, verifies with `UNIWEB_WEBHOOK_SECRET`, and payment creation passes a project-specific `webhookUrl` when events are required.
