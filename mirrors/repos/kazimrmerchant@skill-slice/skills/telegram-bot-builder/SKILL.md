---
name: telegram-bot-builder
description: "Implements Telegram Bot API clients in Telegraf or aiogram: commands, inline keyboards, invoices, polling, and webhook Express deploy. Use when the user asks for a Telegram bot, Bot API, or tg bot. Not a Telegram Mini App scaffold and not for Slack or Discord bots."
version: 1.0.1
---

## When to Use
- User mentions or implies: telegram bot, bot api, telegram automation, chat bot telegram, tg bot.
- Building bots from simple automation to complex AI-powered bots.
- Designing bot architecture, UX, monetization, and scaling.

## Prerequisites
- Node.js (v18+) or Python (v3.9+) installed.
- A Telegram Bot token obtained from @BotFather. Store it in an environment variable `BOT_TOKEN`.
- Windows host (PowerShell) is primary. Set environment variables using:
  ```powershell
  $env:BOT_TOKEN = "YOUR_BOT_TOKEN"
  ```

## Procedure
1. **Choose Stack**: Select a language and library (e.g., Node.js with `telegraf` or Python with `aiogram`).
2. **Initialize Project**: Create project structure.
   ```powershell
   mkdir telegram-bot
   cd telegram-bot
   npm init -y
   npm install telegraf
   ```
3. **Implement Bot Logic**: Set up command handlers, text handlers, and inline keyboards.
   ```javascript
   import { Telegraf } from 'telegraf';

   const bot = new Telegraf(process.env.BOT_TOKEN);

   bot.start((ctx) => ctx.reply('Welcome!'));
   bot.help((ctx) => ctx.reply('How can I help?'));

   bot.on('text', (ctx) => {
     ctx.reply(`You said: ${ctx.message.text}`);
   });

   bot.launch();

   process.once('SIGINT', () => bot.stop('SIGINT'));
   process.once('SIGTERM', () => bot.stop('SIGTERM'));
   ```
4. **Add Inline Keyboards**: For interactive flows.
   ```javascript
   import { Markup } from 'telegraf';

   bot.command('menu', (ctx) => {
     ctx.reply('Choose an option:', Markup.inlineKeyboard([
       [Markup.button.callback('Option 1', 'opt_1')],
       [Markup.button.callback('Option 2', 'opt_2')],
     ]));
   });

   bot.action('opt_1', (ctx) => {
     ctx.answerCbQuery('You chose Option 1');
     ctx.editMessageText('You selected Option 1');
   });
   ```
5. **Implement Monetization (Optional)**: Use Telegram Payments or freemium models.
   ```javascript
   bot.command('buy', (ctx) => {
     ctx.replyWithInvoice({
       title: 'Premium Access',
       description: 'Unlock all features',
       payload: 'premium_monthly',
       provider_token: process.env.PAYMENT_TOKEN,
       currency: 'USD',
       prices: [{ label: 'Premium', amount: 999 }], // $9.99
     });
   });
   ```
6. **Deploy to Production**: Switch from polling to webhooks for scalability.
   ```javascript
   import express from 'express';
   import { Telegraf } from 'telegraf';

   const bot = new Telegraf(process.env.BOT_TOKEN);
   const app = express();

   app.use(express.json());
   app.use(bot.webhookCallback('/webhook'));

   bot.telegram.setWebhook('https://your-domain.com/webhook');

   app.listen(3000);
   ```

## Pitfalls
- **Hardcoded Bot Token (HIGH)**: Never hardcode the bot token. Always use environment variables (e.g., `process.env.BOT_TOKEN`).
- **No Global Error Handler (HIGH)**: Add `bot.catch()` to handle errors gracefully.
- **No Rate Limiting (MEDIUM)**: Telegram has API limits. Add throttling using a library like `Bottleneck`.
- **In-Memory Sessions in Production (MEDIUM)**: State will be lost on restart. Use Redis or a database-backed session store.
- **No Typing Indicator (LOW)**: For better UX, add `ctx.sendChatAction('typing')` before slow operations.

## Verification
- Check if the bot responds to `/start` and `/help` commands in Telegram.
- Verify inline keyboards render correctly and callback queries are handled.
- Ensure the bot token is loaded from environment variables and not present in the source code.
- For webhooks, verify the endpoint returns `200 OK` and receives updates.

## Related skills
Works well with: `telegram-mini-app`, `backend`, `ai-wrapper-product`, `workflow-automation`.
