---
name: email
description: "Sends transactional and broadcast email from Next.js/Vercel apps with Resend and React Email templates (domains, batch, webhooks, idempotency). Use when installing resend or react-email, writing React Email templates, or building app/api/send routes. Not for IMAP mailbox CLI (himalaya). Never expose RESEND_API_KEY to the client."
version: 1.0.1
metadata:
  priority: 4
  docs:
    - "https://resend.com/docs"
    - "https://react.email/docs/introduction"
  sitemap: "https://resend.com/sitemap.xml"
  pathPatterns:
    - 'emails/**'
    - 'src/emails/**'
    - 'components/emails/**'
    - 'src/components/emails/**'
    - 'app/api/send/**'
    - 'src/app/api/send/**'
    - 'app/api/email/**'
    - 'src/app/api/email/**'
    - 'app/api/emails/**'
    - 'src/app/api/emails/**'
    - 'lib/resend.*'
    - 'src/lib/resend.*'
    - 'lib/email.*'
    - 'src/lib/email.*'
    - 'lib/email*'
    - 'src/lib/email*'
    - '**/email-template*'
  bashPatterns:
    - '\bnpm\s+(install|i|add)\s+[^\n]*\bresend\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*\bresend\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*\bresend\b'
    - '\byarn\s+add\s+[^\n]*\bresend\b'
    - '\bnpm\s+(install|i|add)\s+[^\n]*@react-email/'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*@react-email/'
    - '\bbun\s+(install|i|add)\s+[^\n]*@react-email/'
    - '\byarn\s+add\s+[^\n]*@react-email/'
    - '\bnpm\s+(install|i|add)\s+[^\n]*react-email\b'
    - '\bpnpm\s+(install|i|add)\s+[^\n]*react-email\b'
    - '\bbun\s+(install|i|add)\s+[^\n]*react-email\b'
    - '\byarn\s+add\s+[^\n]*react-email\b'
---

# Email Integration (Resend + React Email)

Expert guidance for sending emails from Vercel-deployed applications using Resend (native Vercel Marketplace integration) and React Email templates. Covers SDK setup, transactional sends, domain verification, batch sending, broadcasts, webhooks, idempotency, and template patterns.

## When to Use

Activate this skill when any of the following are true:

- You are building an email-sending feature in a Next.js / Vercel application.
- You are installing or configuring the `resend` SDK or `react-email` / `@react-email/components` packages.
- You need to create or modify React Email templates (files under `emails/`, `src/emails/`, or `components/emails/`).
- You are building API routes for sending emails (paths matching `app/api/send/**`, `app/api/email/**`, `app/api/emails/**`).
- You need to set up Resend domain verification, webhooks, broadcasts, or batch sending.
- You see a `lib/resend.*` or `lib/email*` file being created or modified.

## Prerequisites

- A Vercel project with Next.js (App Router recommended).
- Node.js 18+ installed on the development machine.
- On Windows (primary host), use PowerShell for all CLI commands. Paths use backslashes locally (e.g., `~\project\lib\resend.ts`), but project-internal import paths use forward slashes.
- A Resend account (free tier available) or Vercel Marketplace access.
- If sending from a custom domain, DNS access to your domain provider for MX, SPF, and DKIM records.

## Procedure

### 1. Install Resend via Vercel Marketplace (Recommended)

Resend is a native Vercel Marketplace integration with auto-provisioned API keys and unified billing.

```powershell
# Install Resend from Vercel Marketplace (auto-provisions env vars)
vercel integration add resend
```

This auto-provisions the `RESEND_API_KEY` environment variable on your Vercel project. Pull it locally:

```powershell
vercel env pull .env.local
```

### 2. Install SDK Packages

```powershell
# Install the Resend SDK
npm install resend

# Install React Email for building templates
npm install react-email @react-email/components
```

> **SDK version note:** Current Resend SDK version is **6.9.x** (actively maintained, ~1.6M weekly downloads). React Email latest is **5.2.9** with `@react-email/components` **1.0.8**. React Email 5.x supports **React 19.2** and **Next.js 16**.

### 3. Initialize the Resend Client

Create the client singleton so it can be imported across API routes and server actions:

```ts
// lib/resend.ts
import { Resend } from "resend";

export const resend = new Resend(process.env.RESEND_API_KEY);
```

### 4. Create a Basic Send API Route

```ts
// app/api/send/route.ts
import { NextResponse } from "next/server";
import { resend } from "@/lib/resend";

export async function POST(req: Request) {
  const { to, subject, html } = await req.json();

  const { data, error } = await resend.emails.send({
    from: "Your App <hello@yourdomain.com>",
    to,
    subject,
    html,
  });

  if (error) {
    return NextResponse.json({ error }, { status: 400 });
  }

  return NextResponse.json({ id: data?.id });
}
```

### 5. Create React Email Templates

Organize templates in an `emails/` directory at the project root:

```
emails/
  welcome.tsx
  invoice.tsx
  reset-password.tsx
```

Example template:

```tsx
// emails/welcome.tsx
import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Link,
  Preview,
  Text,
} from "@react-email/components";

interface WelcomeEmailProps {
  name: string;
}

export default function WelcomeEmail({ name }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to our platform</Preview>
      <Body style={{ fontFamily: "sans-serif", backgroundColor: "#f6f9fc" }}>
        <Container style={{ padding: "40px 20px", maxWidth: "560px" }}>
          <Heading>Welcome, {name}!</Heading>
          <Text>
            Thanks for signing up. Get started by visiting your{" "}
            <Link href="https://yourdomain.com/dashboard">dashboard</Link>.
          </Text>
        </Container>
      </Body>
    </Html>
  );
}
```

### 6. Send with a React Email Template

```ts
// app/api/send/route.ts
import { NextResponse } from "next/server";
import { resend } from "@/lib/resend";
import WelcomeEmail from "@/emails/welcome";

export async function POST(req: Request) {
  const { name, email } = await req.json();

  const { data, error } = await resend.emails.send({
    from: "Your App <hello@yourdomain.com>",
    to: email,
    subject: "Welcome!",
    react: WelcomeEmail({ name }),
  });

  if (error) {
    return NextResponse.json({ error }, { status: 400 });
  }

  return NextResponse.json({ id: data?.id });
}
```

### 7. Preview Templates Locally

```powershell
# Start the React Email dev server to preview templates
npx react-email dev
```

This opens a browser preview at `http://localhost:3000` with hot reload for iterating on email templates.

### 8. Upload Templates to Resend (React Email 5.0+)

```powershell
# Upload templates directly from the CLI
npx react-email@latest resend setup
```

Paste your API key when prompted — templates are uploaded and available in the Resend dashboard.

### 9. Dark Mode Support (React Email 5.x)

React Email 5.x supports dark mode with a theming system tested across popular email clients. Use the `Tailwind` component with Tailwind CSS v4:

```tsx
import { Tailwind } from "@react-email/components";

export default function MyEmail() {
  return (
    <Tailwind>
      <div className="bg-white dark:bg-gray-900 text-black dark:text-white">
        <h1>Hello</h1>
      </div>
    </Tailwind>
  );
}
```

> **Upgrade note (v4 → v5):** Replace all `renderAsync` with `render`. The Tailwind component now only supports Tailwind CSS v4.

### 10. Domain Verification

To send from a custom domain (not `onboarding@resend.dev`):

1. Go to [Resend Domains](https://resend.com/domains).
2. Add your domain.
3. Add the DNS records (MX, SPF, DKIM) to your domain provider.
4. Wait for verification (usually under 5 minutes).

Until your domain is verified, use `onboarding@resend.dev` as the `from` address for testing.

### 11. Batch Sending

```ts
const { data, error } = await resend.batch.send([
  {
    from: "hello@yourdomain.com",
    to: "user1@example.com",
    subject: "Update",
    html: "<p>Content for user 1</p>",
  },
  {
    from: "hello@yourdomain.com",
    to: "user2@example.com",
    subject: "Update",
    html: "<p>Content for user 2</p>",
  },
]);
```

### 12. Server Action Pattern

```ts
"use server";
import { resend } from "@/lib/resend";
import WelcomeEmail from "@/emails/welcome";

export async function sendWelcomeEmail(name: string, email: string) {
  const { error } = await resend.emails.send({
    from: "Your App <hello@yourdomain.com>",
    to: email,
    subject: "Welcome!",
    react: WelcomeEmail({ name }),
  });

  if (error) throw new Error("Failed to send email");
}
```

### 13. Broadcast API (February 2026)

Send emails to audiences (mailing lists) managed in Resend:

```ts
// Send a broadcast to an audience
const { data, error } = await resend.broadcasts.send({
  audienceId: "aud_1234",
  from: "updates@yourdomain.com",
  subject: "Monthly Newsletter",
  react: NewsletterEmail({ month: "March" }),
});

// Create and manage broadcasts programmatically
const broadcast = await resend.broadcasts.create({
  audienceId: "aud_1234",
  from: "updates@yourdomain.com",
  subject: "Product Update",
  react: ProductUpdateEmail(),
});

// Schedule for later
await resend.broadcasts.send({
  broadcastId: broadcast.data?.id,
  scheduledAt: "2026-03-15T09:00:00Z",
});
```

### 14. Idempotency Keys

Prevent duplicate sends on retries by passing an `Idempotency-Key` header:

```ts
const { data, error } = await resend.emails.send(
  {
    from: "hello@yourdomain.com",
    to: "user@example.com",
    subject: "Order Confirmation",
    react: OrderConfirmation({ orderId: "ord_123" }),
  },
  {
    headers: {
      "Idempotency-Key": `order-confirmation-ord_123`,
    },
  }
);
```

Resend deduplicates requests with the same idempotency key within a 24-hour window. Use deterministic keys derived from your business logic (e.g., `order-confirmation-${orderId}`).

### 15. Webhook Management API

Create and manage webhooks programmatically instead of through the dashboard:

```ts
// Create a webhook endpoint
const { data } = await resend.webhooks.create({
  url: "https://yourdomain.com/api/webhook/resend",
  events: ["email.delivered", "email.bounced", "email.complained", "email.suppressed"],
});

// List all webhooks
const webhooks = await resend.webhooks.list();

// Delete a webhook
await resend.webhooks.remove(webhookId);
```

### 16. Webhook for Delivery Events

```ts
// app/api/webhook/resend/route.ts
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const event = await req.json();

  switch (event.type) {
    case "email.delivered":
      // Track successful delivery
      break;
    case "email.bounced":
      // Handle bounce — remove from mailing list
      break;
    case "email.complained":
      // Handle spam complaint — unsubscribe user
      break;
  }

  return NextResponse.json({ received: true });
}
```

## Environment Variables

| Variable | Scope | Description |
|----------|-------|-------------|
| `RESEND_API_KEY` | Server | Resend API key (starts with `re_`). Never expose to the client. Use `YOUR_KEY` as placeholder in examples. |

## Pitfalls

- **Never expose `RESEND_API_KEY` to the client.** Only use it in server-side code (API routes, server actions, server components). Do not prefix with `NEXT_PUBLIC_`.
- **Unverified domain sends will fail.** Until your custom domain is verified in Resend, use `onboarding@resend.dev` as the `from` address. Sending from an unverified domain returns an error.
- **React Email v4 → v5 breaking changes.** Replace all `renderAsync` calls with `render`. The `Tailwind` component only supports Tailwind CSS v4 in v5. If you are on Tailwind v3, you must upgrade or use inline styles instead.
- **`react-email dev` port conflict.** The preview server defaults to `http://localhost:3000`. If your Next.js dev server is already running on port 3000, specify a different port: `npx react-email dev --port 3001`.
- **Batch send limits.** Resend enforces rate limits on batch sends. Check current limits in the Resend dashboard for your plan tier before sending large batches.
- **Idempotency key uniqueness.** Keys must be deterministic and unique per logical send. Reusing a key for different content will return the cached original response, not the new content.
- **`"suppressed"` delivery status.** Resend tracks a `"suppressed"` status for recipients on suppression lists (previous hard bounces or spam complaints). Check for this in webhook events alongside `delivered` / `bounced` / `complained`. Suppressed recipients will not receive emails even if you send to them.
- **Webhook signature verification.** Always verify the Resend webhook signature in production. The example route above omits verification for brevity — do not deploy to production without it.
- **Windows path separators.** When referencing files in PowerShell, use backslashes. Import paths in TypeScript/JavaScript always use forward slashes (e.g., `@/lib/resend`).

## Verification

1. **Verify the SDK is installed:**

   ```powershell
   npm ls resend
   ```

   Expected output should show `resend@6.x.x` installed.

2. **Verify environment variable is set:**

   ```powershell
   # On Windows PowerShell
   echo $env:RESEND_API_KEY
   ```

   Or check `.env.local` contains a line like:

   ```
   RESEND_API_KEY=re_YOUR_KEY
   ```

3. **Test a send via API route:**

   ```powershell
   # Start dev server
   npm run dev
   ```

   Then in another terminal:

   ```powershell
   # Send a test email
   curl -X POST http://localhost:3000/api/send `
     -H "Content-Type: application/json" `
     -d '{\"to\":\"test@example.com\",\"subject\":\"Test\",\"html\":\"<p>Hello</p>\"}'
   ```

   Expected response: `{"id":"<email-id>"}` with HTTP 200.

4. **Verify React Email preview:**

   ```powershell
   npx react-email dev
   ```

   Open `http://localhost:3000` (or your configured port) and confirm templates render correctly.

5. **Verify domain status:**

   Check [Resend Domains](https://resend.com/domains) — your domain should show a green "Verified" badge before sending from it in production.

## Related Skills

- **Marketplace install and env var provisioning** → `⤳ skill: marketplace`
- **API route patterns** → `⤳ skill: routing-middleware`
- **Environment variable management** → `⤳ skill: env-vars`
- **Serverless function config** → `⤳ skill: vercel-functions`

## Official Documentation

- [Resend + Vercel Marketplace](https://vercel.com/marketplace/resend)
- [Resend Documentation](https://resend.com/docs)
- [Resend Next.js Quickstart](https://resend.com/docs/send-with-nextjs)
- [React Email Documentation](https://react.email/docs/introduction)
- [React Email Components](https://react.email/docs/components/html)
