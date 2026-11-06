---
name: telegram-bot-broadcast
description: Use when user says "tg bot api", "telegram broadcast", "telegram bot", "tg bot", "mass post", "channel post", "sendMessage", "member count", "subscriber", "subscribe post", "telegram keywords". Validates Telegram bot tokens, discovers the bot's channels/groups and their real member counts, identifies which chats the bot is administrator of, and broadcasts/mass-posts via the Telegram Bot API. Burmese triggers: "tg", "broadcast", "bot token", "channel", "post á€á€„á€º", "sub á€œá€¯á€•á€º".
---

# Telegram Bot API â€” Validate, Discover & Broadcast

Full workflow to take a list of Telegram bot tokens and turn them into working broadcast posts against the channels/groups the bots actually control.

## TRIGGER
Activate when the user provides Telegram `bot tokens` (format `NNNNNN:AAAAAAAA...`) and wants to:
- validate which tokens are alive
- see each bot's access flags (`is_bot`, `can_join_groups`, `can_read_all_group_messages`, `supports_inline_queries`)
- discover the chats (channels/groups) the bot belongs to and their **real member counts**
- find which chats the bot is **administrator** of (post capability)
- broadcast a message / post an ad to those channels

## ENVIRONMENT (Windows + PowerShell)
- Run Python via `python -` with a heredoc (`@"..."@ | python -`).
- Wrap stdout to avoid cp1252 console Unicode errors:
  ```python
  import io,sys
  sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
  ```
- Use `ssl.CERT_NONE` context and `Mozilla/5.0` User-Agent for HTTPS.
- Save large results to temp files (`C:\Users\YOURUS~1\AppData\Local\Temp\opencode\...`) and read them back, rather than printing huge lists to the console.

## TOKENS FILE FORMAT (3 columns)
Source files are usually `token | @username | groups-or-private-only`.
Extract with regex on each line:
```python
m=re.match(r'(\d+:[A-Za-z0-9_-]{20,})\s*\|\s*@(\S+)\s*\|\s*(.*)', line)
```

## HTTP HELPER (reuse this every time)
```python
import io,sys,json,ssl,urllib.request,urllib.parse,concurrent.futures,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA='Mozilla/5.0'
def api_call(bottoken, method, **params):
    url=f'https://api.telegram.org/bot{bottoken}/{method}'
    try:
        if params:
            data=urllib.parse.urlencode(params).encode()
            req=urllib.request.Request(url,data=data,headers={'User-Agent':UA,'Content-Type':'application/x-www-form-urlencoded'})
        else:
            req=urllib.request.Request(url,headers={'User-Agent':UA})
        with urllib.request.urlopen(req,timeout=20,context=ctx) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except: return {'ok':False,'error_code':e.code,'description':str(e)}
    except Exception as ex:
        return {'ok':False,'error':'NETERR','desc':str(ex)[:80]}
```

## STEP 1 â€” VALIDATE TOKENS
Call `getMe` on each token.
- `{'ok':True}` â†’ valid bot. Capture `username`, `first_name`, and flags:
  `is_bot`, `can_join_groups`, `can_read_all_group_messages`, `supports_inline_queries`.
- HTTP `401` â†’ invalid/revoked token.
- `NETERR` â†’ transient, retry.
Save valid set as a Python literal for reuse:
```python
open(r'...\tg_valid_tokens.py','w',encoding='utf-8').write("VALID="+repr(valid)+"\n")
```

## STEP 2 â€” DISCOVER CHATS + MEMBER COUNTS
`getMe` does NOT return audience counts. To find a bot's chats and their real member counts:
1. For **no-webhook bots**, call `getUpdates(offset=-200, limit=100, timeout=2)`.
   Parse `message`/`channel_post`/`my_chat_member` to collect `chat.id`s.
2. For each discovered `chat_id`, call `getChatMemberCount(chat_id=...)` for the real count.
3. Cache bot tokens from `getUpdates` must come with `allowed_updates` if needed.

**Limit (important):** Bot API only exposes chats via the pending update buffer. Webhook bots (or bots whose updates were already consumed) reveal nothing this way. The result is always a subset â€” never claim full coverage. `getChatMemberCount` needs the bot to be a member/admin of the chat.

## STEP 3 â€” IDENTIFY ADMIN (POST-CAPABLE) CHATS
`getChat` succeeding on a public channel does NOT mean admin â€” any bot can resolve a public channel.
To confirm real post capability, check the bot's own membership:
- `getChatMember(chat_id, user_id=<bot_id>)` â†’ status `administrator`/`creator` = can post.
- `getChatAdministrators(chat_id)` lists admins; look for the bot itself.
- `getChat(chat_id)` returns `invite_link`, `username`, `title`, `description`.

Interpret errors:
- `"Bad Request: member list is inaccessible"` â†’ bot is NOT a member/admin; **cannot post** there.

## STEP 4 â€” BROADCAST (sendMessage)
Only post to chats where the bot is a confirmed admin/python. Use `sendMessage`:
```
sendMessage(chat_id=<id>, text=<msg>, disable_web_page_preview=false)
```
- Build the message as a `list` of lines then `"\n".join(lines)`.
- Emojis: use `\U0001F680` (8-digit) escapes, NOT surrogate pairs (`\uD83C\uDFFB` fails utf-8 encode). âœ… `\U0001F3FB` âŒ `\uD83C\uDFFB`.
- A successful result returns `message_id` and `chat.title`.

For an effective "subscribe" ad (psychology for conversion):
- Social proof (`10,000+ smart members already leveling up`), scarcity (`before it's full`), clear benefits (bullet list), one strong CTA with the invite link (`Tap below and SUBSCRIBE now`), avoid spammy caps everywhere.

## STEP 5 â€” SOURCE OF TRUTH / USER TARGET
When the user says "post to my channel @X", do NOT assume the file's bots admin that channel:
- Test with `getChatMember` for the bot's own ID â€” `member list inaccessible` = not admin.
- You can only broadcast through bots that are admins; you cannot post to a channel the bot doesn't control.
- Ask which channel/bot to target, and which channels the user wants the ad placed in.

## ERRORS / RATE LIMITS
- `429` â†’ throttle (increase sleep between calls, lower worker count).
- `401` â†’ invalid token.
- `409 Conflict` on `getUpdates` â†’ bot uses a webhook; getUpdates won't work, use `getWebhookInfo` to see it.
- `400 member list is inaccessible` â†’ not a member â†’ no posting rights.

## OUTPUT CONVENTIONS
- Reply in Burmese (á€™á€¼á€”á€ºá€™á€¬) when the user writes in Burmese.
- Save full lists to temp files; print only counts + top findings.
- Always confirm before broadcasting to large third-party channels (owners can revoke bot admin and delete the post).