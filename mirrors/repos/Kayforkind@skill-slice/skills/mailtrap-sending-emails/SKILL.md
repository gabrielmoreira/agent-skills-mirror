---
name: mailtrap-sending-emails
description: "Configures Mailtrap live delivery via Email API or SMTP, picking transactional vs bulk hosts and optional /api/batch. Trigger when integrating send.api.mailtrap.io, bulk.api.mailtrap.io, or live.smtp.mailtrap.io. Not a sandbox capture skill; skip SPF/DKIM-only domain setup and Campaigns UI."
version: 1.0.1
risk: critical
source: community
date_added: "2026-06-19"
---

## Overview

Mailtrap sends live email over **Email API** (REST) or **SMTP**. Two **streams** apply for API/SMTP: **Transactional** (non-promotional, app-generated) and **Bulk** (promotional / marketing volume). **Batch** is not a third stream: it is how you submit **many messages in one request** on whichever stream matches the content. **Campaigns** are a separate product path for promotional mail to **Mailtrap contacts**.

Pair this skill with the official [Transactional](https://docs.mailtrap.io/developers/email-sending/transactional.md) and [Bulk](https://docs.mailtrap.io/developers/email-sending/bulk.md) developer pages when building or debugging integrations.

## When to Use

Use when integrating, configuring, or troubleshooting Mailtrap live email sending with:
- Email API (REST `POST /api/send` or `POST /api/batch`)
- SMTP relay
- Transactional streams
- Bulk streams
- Batch requests (up to 500 messages per request)

**Trigger keywords:** mailtrap send, mailtrap api, mailtrap smtp, transactional email, bulk email, mailtrap batch, mailtrap token, mailtrap integration, send.api.mailtrap.io, bulk.api.mailtrap.io, live.smtp.mailtrap.io.

## When NOT to Use

- **Sandbox only** — capturing mail without delivery, reading messages in a sandbox. Use `mailtrap-testing-with-sandbox`.
- The main ask is **webhooks**, **step-by-step Campaigns UI setup**, or **deliverability deep-dives**.
- **Exhaustive API reference** — once the user's path is clear, link the official send docs for full schemas, optional fields, and edge cases.
- Domain verification before sending — use `mailtrap-setting-up-sending-domain`.

## Prerequisites

1. **Mailtrap account** with Email Sending enabled.
2. **Sending domain verified** in Mailtrap (SPF/DKIM/DMARC). Complete the **Sending Domains** setup and compliance first. See related skill `mailtrap-setting-up-sending-domain`.
3. **API token** with the correct stream scope. Store it in an environment variable:
   ```powershell
   # PowerShell (Windows host — primary)
   $env:MAILTRAP_API_TOKEN = "YOUR_TOKEN"
   ```
   ```bash
   # Bash (if on Linux/macOS)
   export MAILTRAP_API_TOKEN="YOUR_TOKEN"
   ```
4. **No live secrets in code.** Always reference `$MAILTRAP_API_TOKEN` or a secrets manager. Rotate tokens when access changes.

## Procedure

### Step 1 — Choose integration approach (preference order)

1. **Plugin or integration for the user's platform** (no-code or minimal-config) where available.
2. **Official SDK** for your language when one exists (maintained clients, typed helpers, less room for URL/auth mistakes).
3. **HTTP Email API** when there is no SDK or the SDK does not fit (direct `POST` to `/api/send` or `/api/batch` with JSON).
4. **SMTP** only when you really need it (legacy stack, host/platform that only speaks SMTP, or hard constraints that rule out HTTP).

### Step 2 — Identify the correct stream

| Content type | Stream | API host | SMTP host |
|---|---|---|---|
| App-generated (password resets, receipts, notifications, alerts) | **Transactional** | `send.api.mailtrap.io` | `live.smtp.mailtrap.io` |
| Promotional / marketing volume to contacts you manage | **Bulk** | `bulk.api.mailtrap.io` | `bulk.smtp.mailtrap.io` |

**HARD RULE:** Promotional/bulk content must use the bulk host (`bulk.api.mailtrap.io` or `bulk.smtp.mailtrap.io`). Never send promotional content through `send.api.mailtrap.io`.

### Step 3 — Send via Email API (REST)

#### Quick reference — API endpoints

| Stream | Send Endpoint | Batch Endpoint | Authorization |
|---|---|---|---|
| Transactional | `POST https://send.api.mailtrap.io/api/send` | `POST https://send.api.mailtrap.io/api/batch` | `Authorization: Bearer $MAILTRAP_API_TOKEN` |
| Bulk | `POST https://bulk.api.mailtrap.io/api/send` | `POST https://bulk.api.mailtrap.io/api/batch` | `Authorization: Bearer $MAILTRAP_API_TOKEN` |

The same token works on both hosts as long as its scope covers the stream. `Api-Token: ...` header is also accepted as an alternative to `Authorization: Bearer ...`.

#### 3a. Single message — Transactional (non-template)

```bash
curl -X POST https://send.api.mailtrap.io/api/send \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"email": "hello@yourdomain.com", "name": "Your App"},
    "to": [{"email": "user@example.com"}],
    "subject": "Hello",
    "text": "Plain text body"
  }'
```

#### 3b. Single message — Bulk (non-template)

Same JSON shape, different host:

```bash
curl -X POST https://bulk.api.mailtrap.io/api/send \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"email": "hello@yourdomain.com", "name": "Your App"},
    "to": [{"email": "user@example.com"}],
    "subject": "Promotional",
    "html": "<p>HTML body</p>"
  }'
```

#### 3c. Batch (up to 500 messages per request)

Batch is **not** a stream — it is a submission method. Use on whichever stream matches content:

```bash
curl -X POST https://send.api.mailtrap.io/api/batch \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"from":{"email":"a@example.com"},"to":[{"email":"b@example.com"}],"subject":"One","text":"..."}]}'
```

For bulk batch, use `https://bulk.api.mailtrap.io/api/batch`.

#### 3d. Template-based send

Use `template_uuid` and `template_variables` instead of raw `text`/`html`:

```bash
curl -X POST https://send.api.mailtrap.io/api/send \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"email": "hello@yourdomain.com", "name": "Your App"},
    "to": [{"email": "user@example.com"}],
    "template_uuid": "your-template-uuid",
    "template_variables": {"user_name": "Jane"}
  }'
```

#### JSON body fields

- **Required:** `from`, `to`, `subject`, and `text` and/or `html` (unless using a template).
- **Optional:** `category`, `custom_variables`.
- **Template:** `template_uuid`, `template_variables`.
- Full schemas: [Transactional send](https://docs.mailtrap.io/developers/email-sending/transactional.md#post-api-send) and [Bulk send](https://docs.mailtrap.io/developers/email-sending/bulk.md#post-api-send).

### Step 4 — Send via SMTP (only when necessary)

| Setting | Transactional | Bulk |
|---|---|---|
| Host | `live.smtp.mailtrap.io` | `bulk.smtp.mailtrap.io` |
| Port | 587 (also 25, 2525, 465 with SSL) | 587 (also 25, 2525, 465 with SSL) |
| Username | `api` | `api` |
| Password | API token (`$MAILTRAP_API_TOKEN`) | API token (`$MAILTRAP_API_TOKEN`) |

**HARD RULE:** SMTP username is `api`, not an email address. Password is the API token.

**HARD RULE:** Never use sandbox SMTP host for live sending. Live sending uses `live.smtp.mailtrap.io` or `bulk.smtp.mailtrap.io`.

### Step 5 — Use an official SDK (if available)

Before generating SDK code: **read the README** of the relevant SDK repository for current method signatures, constructor options, and examples. Do not rely on memory.

- [Node.js](https://github.com/mailtrap/mailtrap-nodejs)
- [Python](https://github.com/mailtrap/mailtrap-python)
- [PHP](https://github.com/mailtrap/mailtrap-php)
- [Ruby](https://github.com/mailtrap/mailtrap-ruby)
- [Java](https://github.com/mailtrap/mailtrap-java)
- [.NET](https://github.com/mailtrap/mailtrap-dotnet)
- [CLI](https://github.com/mailtrap/mailtrap-cli)

**HARD RULE:** Do not invent constructors or method names. Read the SDK README and OpenAPI-linked examples first.

### Step 6 — Handle rate limits and errors

| Scope | Limit | Window |
|---|---|---|
| Sending API (per token) | 150 requests | 10 seconds |

Implement exponential backoff on HTTP `429`.

### Step 7 — Suppressions

Mailtrap automatically manages suppressions for addresses that hard bounce, report spam, or unsubscribe. Mailtrap will not send emails to suppressed recipients again. See [Suppressions documentation](https://docs.mailtrap.io/developers/email-sending/suppressions.md).

## Examples

### Choosing how to send

| Approach | Use when |
|---|---|
| **Transactional, single message** | Email generated by your app (password resets, receipts, notifications, alerts). One logical message per `POST https://send.api.mailtrap.io/api/send`. |
| **Bulk** | Promotional email to contacts that you manage on your side, sent at volume through Mailtrap. Not the same as "batch": bulk is the stream, not the batch endpoint. |
| **Batch** | Multiple different messages to hand off at the same time (up to 500 per request). Cuts HTTP overhead; can be applied to both transactional and bulk. |
| **Campaigns** | Promotional email to recipients stored as Mailtrap contacts, using Mailtrap Campaigns (audiences, scheduling, reporting in the product). Recommended to avoid implementing contact management and email sending logic; requires UI setup before sends flow — this skill does not replace that workflow. |

## Pitfalls

| Mistake | Fix |
|---|---|
| Confusing **batch** with **bulk** | **Batch** = many messages in one `/api/batch` request. **Bulk** = promotional stream/host and token. |
| Promotional API mail on transactional host | Use bulk base URL (`bulk.api.mailtrap.io`) and bulk token for promotional content you generate in code. |
| Bulk traffic on `send.api.mailtrap.io` | Promotional/bulk stream uses `bulk.api.mailtrap.io`. |
| Using sandbox SMTP host for live sending | Live sending uses `live.smtp.mailtrap.io` or `bulk.smtp.mailtrap.io`. |
| SMTP username is an email address | Username is `api`; password is the API token. |
| Sending before domain is verified | Complete **Sending Domains** setup and compliance first (see `mailtrap-setting-up-sending-domain`). |
| Guessing SDK API from memory | Read the SDK README and OpenAPI-linked examples; do not invent constructors or method names. |
| Choosing **SMTP first** for a greenfield app | Prefer **platform integration** if one exists, then **SDK**, then **HTTP API**; SMTP only when necessary. |
| No backoff on 429 | Implement exponential backoff; limit is 150 requests per 10 seconds per token. |
| Hardcoded tokens in source | Store tokens in environment variables or a secrets manager; rotate when access changes. |

## Verification

1. **Confirm token is set:**
   ```powershell
   echo $env:MAILTRAP_API_TOKEN
   ```
   Should print a non-empty token string (never commit this to source).

2. **Send a test transactional email and check the HTTP response:**
   ```bash
   curl -s -o response.json -w "%{http_code}" -X POST https://send.api.mailtrap.io/api/send \
     -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "from": {"email": "hello@yourdomain.com", "name": "Your App"},
       "to": [{"email": "test@example.com"}],
       "subject": "Verification test",
       "text": "This is a test from Mailtrap."
     }'
   ```
   - **Expected:** HTTP `200` or `201` with a JSON response containing a message ID.
   - **`429`** = rate limited; implement backoff.
   - **`401` / `403`** = token missing, invalid, or lacks stream scope.
   - **`422`** = validation error (bad `from` domain, missing fields, etc.).

3. **Verify SMTP connectivity (PowerShell):**
   ```powershell
   Test-NetConnection -ComputerName live.smtp.mailtrap.io -Port 587
   ```
   `TcpTestSucceeded: True` confirms the host/port is reachable.

4. **Check Mailtrap dashboard:**
   - Go to **Email Sending → Email Logs** in the Mailtrap UI.
   - Confirm the test message appears with a delivered status.
   - Check for suppressions if a recipient does not receive mail.

5. **Batch verification:** Send a 2-message batch and confirm the response includes per-message success/failure entries.

## Related skills

- `mailtrap-testing-with-sandbox` — safe testing in a sandbox inbox without live delivery.
- `mailtrap-setting-up-sending-domain` — domain verification (SPF/DKIM/DMARC) before sending.

## Limitations

- This skill summarizes Mailtrap sending choices; use Mailtrap's current API docs for exhaustive schemas and product limits.
- Campaigns UI setup is out of scope; link to Mailtrap product documentation for that workflow.
