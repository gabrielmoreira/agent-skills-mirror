---
name: telegram-bot-cloudflare
description: Deploy Telegram bots to Cloudflare Workers with proper secret configuration. Use ONLY when user asks to create/deploy/fix Telegram bot on Cloudflare Workers.
---

# Telegram Bot on Cloudflare Workers

Deploy Telegram bots to Cloudflare Workers serverless platform.

## Prerequisites

- Telegram Bot Token from @BotFather
- Cloudflare account with Workers enabled
- Workers.dev subdomain configured

## Step-by-Step Deployment

### 1. Get Bot Token

User gets token from @BotFather:
```
/newbot
Bot name: My Bot
Username: mybot_bot
Token: 123456789:ABCdefGHI...
```

### 2. Configure Workers.dev Subdomain

**CRITICAL:** Must configure subdomain BEFORE deploying worker.

```javascript
// Check if subdomain exists
GET /accounts/{account_id}/workers/subdomain

// If 404, create subdomain
PUT /accounts/{account_id}/workers/subdomain
Body: {"subdomain": "your-subdomain"}
```

Example subdomain: `yatal`, `mybots`, etc.

### 3. Deploy Worker Script

**Use vanilla JavaScript** (no external imports - Cloudflare Workers doesn't support ESM imports from URLs).

```javascript
export default {
  async fetch(request, env) {
    if (request.method === 'GET') {
      return new Response('Bot is running!')
    }

    const update = await request.json()
    const BOT_TOKEN = env.BOT_TOKEN
    
    async function sendMessage(chatId, text, options = {}) {
      const body = { chat_id: chatId, text, parse_mode: 'Markdown', ...options }
      await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
    }

    // Handle /start
    if (update.message?.text === '/start') {
      await sendMessage(update.message.chat.id, 'Hello!')
    }

    return new Response('OK', { status: 200 })
  }
}
```

Deploy via Cloudflare MCP:
```javascript
cloudflare.request({
  method: 'PUT',
  path: `/accounts/${accountId}/workers/scripts/bot-name`,
  body: multipart_form_data_with_script,
  contentType: 'multipart/form-data; boundary=...',
  rawBody: true
})
```

**Metadata must include:**
```json
{
  "main_module": "worker.js",
  "compatibility_date": "2024-01-01"
}
```

### 4. Set Environment Variables (CRITICAL!)

**WRONG WAY (will encrypt values):**
```javascript
// This creates encrypted secrets that worker can't read!
cloudflare.request({
  method: 'PUT',
  path: `/accounts/${accountId}/workers/scripts/bot-name/secrets`,
  body: { name: 'BOT_TOKEN', text: 'xxx', type: 'secret_text' }
})
```

**CORRECT WAY:**
```javascript
// Method 1: Use secrets endpoint correctly
cloudflare.request({
  method: 'PUT',
  path: `/accounts/${accountId}/workers/scripts/bot-name/secrets`,
  body: { name: 'BOT_TOKEN', text: 'token-value', type: 'secret_text' }
})

// If this creates "Value encrypted" issue, DELETE and re-add:
// DELETE /accounts/{account_id}/workers/scripts/{script}/secrets/{secret_name}
// Then PUT again
```

**Verification:** Check in dashboard that variables show actual values (or "Secret" for secret_text type), NOT "Value encrypted".

### 5. Set Webhook

Worker URL format: `https://{script-name}.{subdomain}.workers.dev`

Example: `https://my-bot.yatal.workers.dev`

```bash
curl "https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://my-bot.yatal.workers.dev"
```

### 6. Test & Debug

**Check webhook status:**
```bash
curl "https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
```

**Common errors:**

| Error | Cause | Fix |
|---|---|---|
| 404 Not Found | Subdomain not configured | Create subdomain first |
| SSL handshake failure | New subdomain (cert pending) | Wait 5 min or use custom domain |
| Value encrypted | Wrong secret API usage | Delete secret, re-add correctly |
| Bot not responding | env.BOT_TOKEN undefined | Check secrets in dashboard |

**Test worker directly:**
```bash
# Should return "Bot is running!"
curl https://my-bot.yatal.workers.dev
```

**Check if bot received updates:**
```bash
curl "https://api.telegram.org/bot{TOKEN}/getUpdates"
```

## Common Patterns

### Inline Keyboard Buttons

```javascript
const keyboard = {
  inline_keyboard: [
    [
      { text: 'Button 1', callback_data: 'btn1' },
      { text: 'Button 2', callback_data: 'btn2' }
    ]
  ]
}

await sendMessage(chatId, 'Choose:', { reply_markup: keyboard })
```

### Handle Button Callbacks

```javascript
if (update.callback_query) {
  const data = update.callback_query.data
  const chatId = update.callback_query.message.chat.id
  
  // Answer callback (removes loading state)
  await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/answerCallbackQuery`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ callback_query_id: update.callback_query.id })
  })
  
  // Send response
  await sendMessage(chatId, `You clicked: ${data}`)
}
```

### Forward to Admin

```javascript
bot.on('message:text', async (ctx) => {
  if (ctx.message.text.length > 30) {
    await sendMessage(
      env.ADMIN_CHAT_ID,
      `New message from ${ctx.from.first_name}:\n${ctx.message.text}`
    )
  }
})
```

## Full Deployment Checklist

- [ ] Get bot token from @BotFather
- [ ] Check/create workers.dev subdomain
- [ ] Deploy worker script with correct metadata
- [ ] Set BOT_TOKEN secret (verify not "Value encrypted")
- [ ] Set ADMIN_CHAT_ID if needed
- [ ] Set webhook URL
- [ ] Test: Send /start to bot
- [ ] Check webhook info for errors
- [ ] If SSL error: wait or use custom domain

## Troubleshooting Commands

```javascript
// List all workers
cloudflare.request({ method: 'GET', path: `/accounts/${accountId}/workers/scripts` })

// Get worker details
cloudflare.request({ method: 'GET', path: `/accounts/${accountId}/workers/scripts/bot-name` })

// Check subdomain
cloudflare.request({ method: 'GET', path: `/accounts/${accountId}/workers/subdomain` })

// Delete worker (start over)
cloudflare.request({ method: 'DELETE', path: `/accounts/${accountId}/workers/scripts/bot-name` })
```

## Security Notes

- Never commit bot tokens to git
- Use secret_text type for sensitive values
- Validate admin_chat_id before forwarding
- Add rate limiting for production bots

## Alternative: Custom Domain (Recommended for Production)

If SSL issues persist with workers.dev:

1. Add domain to Cloudflare
2. Create DNS record: `bot.example.com` → Worker route
3. Use `https://bot.example.com` as webhook URL
4. SSL works immediately (no waiting)

---

**Remember:** The most common mistake is incorrect secret configuration. Always verify in dashboard that secrets are accessible to the worker, not showing "Value encrypted" error.
