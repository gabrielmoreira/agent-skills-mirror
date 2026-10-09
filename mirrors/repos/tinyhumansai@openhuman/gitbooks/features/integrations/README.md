---
description: >-
  Managed OAuth into Gmail, Notion, GitHub, Slack, Stripe, Calendar
  and more - with one-click OAuth and zero API keys.
icon: plug
---

# Third-party Integrations

OpenHuman ships with backend-proxied access to the connector platform's managed-auth catalog, **119 toolkits** as the app knows them. Connecting one through the managed path is a one-click OAuth flow inside the app: no API keys to wire by hand, and no plugin marketplace to navigate.

That figure is the catalog the app ships (`KNOWN_COMPOSIO_TOOLKITS` in `app/src/components/composio/toolkitMeta.tsx`, pinned at 119 by `toolkitMeta.test.tsx`). What you can actually connect is whatever the backend's allowlist returns when the page loads, and the per-toolkit action schemas are fetched live, so no number in this repository bounds the total actions reachable.

Under the hood, the connector layer is powered by [Composio](https://composio.dev). In the default managed mode, OpenHuman's backend owns the Composio API key, OAuth token brokering, rate limits, and trigger webhook fan-out. If you switch to direct mode, the core talks to Composio with your own Composio API key; synchronous tool calls work, but real-time trigger webhooks must be configured on your own webhook infrastructure.

Once a service is connected, it shows up in four places at once:

1. As an **agent tool**, the model can call it directly.
2. As a **profile signal**, your activity across services feeds your personalization.
3. As a **trigger source**, live events (a new email, a new charge, an inbound DM) flow into the [Triggers](triggers.md) pipeline and can fire off agent actions automatically.

## Some of what's in the catalog

The catalog spans productivity, business, social, messaging and Google. A non-exhaustive sample:

| Category                | Examples                                             |
| ----------------------- | ---------------------------------------------------- |
| **Email & calendar**    | Gmail, Outlook, Google Calendar, Apple Calendar      |
| **Docs & storage**      | Google Docs, Google Drive, Notion, Dropbox, Airtable |
| **Code & dev**          | GitHub, Linear, Jira, Figma                          |
| **Comms**               | Slack, Discord, Microsoft Teams, Telegram, WhatsApp  |
| **CRM & sales**         | Salesforce, HubSpot                                  |
| **Commerce & payments** | Stripe, Shopify                                      |
| **Project management**  | Asana, Trello                                        |
| **Social**              | Twitter / X, Spotify, YouTube                        |

## Native vs proxied

Some services have **native providers**. Rust modules that know how to ingest the service into memory directly (e.g. Gmail's native ingest path). Others are exposed as **proxied tools** only: the agent can call them, but there's no automatic ingest yet. New native providers are added as features land.

## How connections work

Click **Connect** on any integration. A browser window opens for OAuth. Once you sign in, the connection becomes active and you can add it as a [memory source](../memory.md) to sync it on a schedule.

Each integration shows its current status:

- **Not connected**: the integration has not been set up.
- **Connected**: the integration is active and being synced.
- **Manage**: an active integration, with options to reconfigure or disconnect.

You can revoke any connection at any time from the **Connections** page.

## Messaging channels

Some integrations are not just something to read from: OpenHuman uses them to _talk back_ to you. Eight channels have a setup flow in the app, and more are available by hand in `config.toml`. The three you are most likely to start with:

- **Telegram**: the usual first choice. Two-way, with a managed one-click connection or your own bot token.
- **Discord**: two-way, by OAuth or your own bot token, with a server and channel picker.
- **Web**: the chat inside the desktop app itself. Messages stay entirely local.

Set your default under **Connections → Channels**. [Messaging Channels](../channels.md) has the full list and what each one can do.

## Beyond the curated catalog: MCP & Skills

The managed OAuth connectors are the curated path. Beyond them, OpenHuman opens up the wider open-tooling ecosystem:

- **MCP servers**: a built-in registry browses thousands of [Model Context Protocol](https://modelcontextprotocol.io) servers (Smithery + the official registry) that install locally as new agent tools.
- **Skills**: a browsable catalog of `SKILL.md` capability bundles aggregated from several public registries, installed from the **Connections → Skills** tab. The old in-app JavaScript sandbox is gone; a skill runs as its own agent session with the interpreters it declares, not as code inside the app.

See [MCP Servers & Skills](mcp-and-skills.md) for the full picture.

## Native voice and tools

Two capabilities ship native rather than as integrations because they're load-bearing for the desktop experience:

- [**Voice**](../native-tools/voice.md): STT in, TTS out, and a live voice agent you can interrupt mid-sentence.
- [**Native tools**](../native-tools/README.md): built-in web search, a web-fetch scraper, and a full filesystem, git, lint, test and grep coder toolset the agent has out of the box.

## Privacy boundary

OpenHuman's core never calls any third-party API directly. All requests go through the OpenHuman backend, which handles OAuth tokens and rate limiting. Your tokens never sit on disk in plaintext on your machine, and the agent only sees the _results_ of tool calls, not the credentials.

If you opt into direct Composio mode, that boundary changes: your local core uses your own Composio API key and you are responsible for the Composio account, rate limits, billing relationship, and any webhook endpoint needed for trigger delivery.

See [Privacy & Security](../privacy-and-security.md) for the full boundary.

## See also

- [Triggers](triggers.md), live events from connected integrations and how they fire agent actions.
- [Memory](../memory.md)
