---
name: Channels Guide
description: >-
  Configuration, troubleshooting, and operational guide for Research-Claw IM channels
  (Telegram, Discord, WeChat, Feishu, Slack, WhatsApp). Covers dashboard UI flow,
  bot token setup, QR login, config.patch restart behavior, enable/disable/delete,
  common errors (401, ABI, plugins.allow), and diagnostic procedures.
---

<!-- MAINTENANCE NOTES:
     Source: AGENTS.md §8 Channels (extracted during prompt redesign).
     Update here when adding channel types or protocols.
     commands.native=false enforced by sync-global-config.cjs.
     WeChat creds: ~/.openclaw/openclaw-weixin/accounts/
     Dashboard UI: ExtensionsPanel.tsx ChannelCard + ChannelsTab
-->

# IM Channel Configuration

RC can receive/reply via Telegram, Discord, WeChat (微信), Feishu (飞书),
QQ, Slack, WhatsApp. Channels are OC infrastructure — RC reuses them fully.

## Dashboard Channel Management UI

The dashboard has a **complete channel management UI** in the left sidebar.

**Location**: Left sidebar → Extensions panel (🔗 chain-link icon) → **Channels** tab.

### What users can do in the Channels tab:
- View all channels with live status (connected / configured / error / disabled)
- **WeChat / WhatsApp**: Click the **Connect** button → QR code modal opens → scan with phone
- **Enable / Disable** any channel via a toggle switch (triggers `config.patch` → gateway restart)
- **Delete** a channel via the red trash button (with confirmation modal)
- **Add Channel** button at the bottom (sends a chat message asking you for help)
- **Ask Agent to Fix / Configure** button on error/unconfigured channels (sends chat message)

### How to guide users:
- **For WeChat / WhatsApp QR login**: Direct users to the Channels tab:
  "请打开左侧扩展面板 → 通道标签 → 点击微信旁边的 Connect 按钮，在弹出窗口中扫码。"
  Do NOT generate QR codes in the chat — the dashboard QR modal handles it.
- **For bot-token channels** (Telegram, Discord, etc.): Help via chat — guide them to
  get a token, then use `config.patch` to write it. Or they can click "Ask Agent to Configure".
- The `weixin_login` / `whatsapp_login` agent tools are **fallbacks for IM-only contexts**
  (when the user is chatting from Telegram/Discord and has no dashboard access).

## Connection Protocols

### Bot-Token Type (Telegram / Discord / Feishu / QQ / Slack)

1. Guide user to create a bot on the platform and obtain a token.
   - **Telegram**: Talk to @BotFather → `/newbot` → copy token.
   - **Discord**: Discord Developer Portal → Bot section → copy token.
   - **Feishu**: Open platform → create bot → App ID + App Secret.
2. Write config via `config.patch`:
   - Telegram: `{ channels: { telegram: { botToken: "<TOKEN>", enabled: true } } }`
   - Discord: `{ channels: { discord: { token: "<TOKEN>", enabled: true } } }`
   - Feishu: `{ channels: { feishu: { appId: "...", appSecret: "...", enabled: true } } }`
   - Others: see platform OC docs for field names.
3. **After `config.patch`**: Gateway auto-restarts via SIGUSR1 (takes ~3–5s). The dashboard
   reconnects automatically. No manual restart needed.
4. Telegram: user must send "/start" in the bot chat to receive replies.
5. `commands.native` must be `false` (530+ tools exceed IM menu limits).
   `sync-global-config.cjs` auto-fixes this on startup.

### WeChat (微信) — QR Scan

**Prerequisite**: `openclaw-weixin` plugin installed and in `plugins.allow`.

**Primary path (dashboard)**: User clicks Connect in the Channels tab → QR modal → scan.
The dashboard handles `web.login.start` → `web.login.wait` automatically,
then triggers `config.patch` to restart gateway and pick up new credentials.

**Fallback path (IM-only / no dashboard)**: Use the `weixin_login` agent tool:

1. Call `weixin_login { action: "start" }`.
   - Returns QR code URL in markdown: `![weixin-qr](https://...)`.
   - Display the image to the user and prompt them to scan with WeChat.
2. Call `weixin_login { action: "wait", timeoutMs: 120000 }`.
   - Blocks until the user scans or timeout.
   - On success, plugin auto-saves credentials; gateway auto-starts channel.
3. WeChat cannot send proactive messages — replies only (contextToken mechanism).

### WhatsApp — QR Scan

**Primary path**: Same as WeChat — user clicks Connect in the Channels tab.

**Fallback path (IM-only)**: Use the `whatsapp_login` agent tool:

1. Call `whatsapp_login { action: "start" }`.
   - Returns QR code as base64 data URL in markdown: `![qr](data:image/png;base64,...)`.
2. Call `whatsapp_login { action: "wait", timeoutMs: 120000 }`.
   - Blocks until the user scans or timeout.

## Config & Restart Behavior

Understanding this is critical for troubleshooting:

1. **`config.patch`** → gateway receives SIGUSR1 → drains active tasks (up to 90s)
   → restarts → channels reload from new config. Dashboard auto-reconnects.
2. **Enable/Disable switch** in dashboard → calls `config.patch` with
   `{ channels: { <id>: { enabled: true/false } } }` → restart.
3. **Delete button** → calls `config.patch` with `{ channels: { <id>: null } }` → restart.
4. If a channel has an **invalid token** (e.g., placeholder `<YOUR_TOKEN>`), the channel
   will crash on startup with 401 Unauthorized and enter an **auto-restart loop**
   (exponential backoff: 5s → 10s → 20s → ... up to 10 attempts). This is normal;
   it stops after 10 failures. Fix: provide correct token or disable the channel.
5. **Drain can be slow** (up to 90s) if there are active agent tasks or embedded runs.
   This is by design — gateway waits for work to complete before restarting.

## In-Channel Behavior

- All RC tools (library, tasks, workspace, monitor) are **fully available**.
- Keep replies under 2000 characters (IM message limit).
- Do not use Markdown tables (most IM clients do not render them).
- `approval_card` degrades to text: "需要审批: xxx. 回复 yes/no".
- Media requires absolute paths via the media parameter.
- Peer ID formats differ: WeChat `xxx@im.wechat`, Telegram numeric IDs.

## Troubleshooting

### Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401: Unauthorized` loop | Invalid or placeholder bot token | Provide real token via `config.patch` or disable channel |
| "not configured" | No credentials found for channel | For bot-token: set token in config. For WeChat: re-scan QR |
| "Provider not running" | Channel configured but crashed | Check logs for error. Common: token expired, network issue |
| Channel not visible | Plugin not in `plugins.allow` or `plugins.load.paths` | Add to both in config. See 4-point sync below |
| `better-sqlite3` crash | Native module ABI mismatch | Rebuild under conda Node 22 (gateway's Node version) |
| WeChat "not configured" after QR | Old default account has no token | Re-scan QR. Dashboard uses best account for status |

### Diagnostic Steps

When a channel shows Error or Not Configured:

1. **Check the token**: Read config via `config.get` or ask user. Is it a real token
   or a placeholder like `<YOUR_TOKEN>`? Placeholder = 401 errors.
2. **Check `plugins.allow`**: The channel plugin ID must be in `plugins.allow` array.
   Example: `openclaw-weixin` for WeChat, `telegram` for Telegram (OC built-in).
3. **Check credentials path** (WeChat only): Stored at
   `~/.openclaw/openclaw-weixin/accounts/<accountId>.json`. If missing, user needs to re-scan QR.
4. **Check gateway logs**: Look for `[telegram]`, `[openclaw-weixin]` etc. in terminal output.
   Common patterns:
   - `401: Unauthorized` → invalid token
   - `ENOTFOUND` / `ETIMEDOUT` → network/VPN issue
   - `channel exited` → channel crashed, will auto-restart
5. **Restart gateway** if needed: `gateway.restart` (requires `approval_card`).
   Or user can Ctrl+C and re-run `run.sh`.

### 4-Point Plugin Sync (for new channel plugins)

When adding a new channel plugin, it must be registered in 4 places:
1. `config/openclaw.json` → `plugins.allow` array
2. `config/openclaw.json` → `plugins.load.paths` array
3. `scripts/ensure-config.cjs` → `REQUIRED_ALLOW` array
4. `dashboard/src/utils/config-patch.ts` → `RC_CONFIG_DEFAULTS.plugins.allow`
Plus the runtime global `~/.openclaw/openclaw.json`.
