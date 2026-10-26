# Set up Comms

The VS Code installer’s **Comms** step lists conversation channels for the selected
runtime and communication tools for eligible Focused/member claws. Select several
different channels or choose **None**. Each claw keeps its own credentials.

A Border owns its conversation channels. Full NetClaw Twilio and Zoom tools belong
to a Focused claw or an explicitly selected **Comms member**. Adding those tools
does not silently give a member the Border’s conversation credentials.

## Before setup

Use a dedicated test account/app when qualifying an installer. Prepare the provider
account, bot/app identity and selected users/rooms first. Enter secrets only in the
native secure prompts. Do not paste a whole `.env` into a plan or an assistant.
The installer stores secrets in the selected home’s private environment file.

Choose explicit allowed user/room IDs. Empty access lists grant no access; wildcard
access is refused. Supported typed group configurations require mentions. Review
any account linking, dependency installation, callback listener and service startup
before applying. Public callbacks require an already prepared, authenticated
endpoint; choosing a channel does not create a tunnel or change shared policy.

## WhatsApp

WhatsApp is included for **both** runtimes. OpenClaw’s WhatsApp channel uses its
account-linking flow. Hermes has two separate choices: **WhatsApp** with its linked
account/bridge, and **WhatsApp Cloud API** with Meta business app credentials and a
prepared HTTPS callback. These are different setup paths; Cloud API credentials do not
replace QR linking for the personal linked-account path. Use the runtime-specific
guides in the inventory below. Pair only the selected test account/home.

## Discord

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
   and create/select the dedicated test application.
2. Add its bot and obtain the **bot token** from the Bot page. Application ID,
   public key and OAuth client secret do not substitute for that token.
3. Follow the selected runtime’s Discord guide for required bot intents and the
   installation scopes/permissions. Install it only in the chosen test server.
4. Use Discord Developer Mode to copy stable user, server and channel IDs. Enter
   only the IDs intended for this claw. The OpenClaw form requires one guild ID
   when group channels are selected.
5. Enter the bot token in the secure prompt. Authentication alone does not prove
   gateway connection, channel permission or message delivery.

## Microsoft Teams

Use a dedicated single-tenant bot identity. The runtime-specific forms require
application/client ID, tenant ID and client secret; enter the secret securely.
A Teams-managed bot can avoid an Azure Bot resource when available to the account.
The [Teams CLI creation guide](https://microsoft.github.io/teams-sdk/cli/commands/app/create/)
describes that option. An Azure-managed bot also requires an accessible Azure
subscription and appropriate resource permissions.

Prepare the Teams app package and authenticated `/api/messages` endpoint according
to the runtime guide. App upload/install policies and admin consent are separate
prerequisites. A successful bot registration or Bot Framework token request does
not prove the app was installed in Teams. Do not weaken tenant policy to complete
an installer check. Optional Graph/delegated OAuth features need their own consent.

The Hermes form writes a loopback listener, mention requirement and an explicit
Entra user allowlist; an empty list denies access. It installs the pinned SDK
before activation. The prepared HTTPS callback is a prerequisite, and its
reachability remains a separate check. OpenClaw has its own typed Teams form and
pinned plugin; its application settings and welcome-message controls are audited
separately from Hermes. Do not copy one runtime's configuration into the other.
The pinned OpenClaw Teams plugin binds its reviewed callback port on all local
interfaces. The review identifies this public listener; it is not a loopback-only
listener. Prepare the authenticated HTTPS endpoint and host access restrictions
before enabling the gateway. Setup does not create firewall rules or tunnels.

## Twilio

The catalog distinguishes three surfaces:

- **Native SMS** in OpenClaw or Hermes uses the runtime’s Twilio SMS adapter and its
  own account SID/auth token/sender/callback contract. An API-key secret is not an
  account auth token. The pinned OpenClaw SMS plugin does not advertise MMS.
- **Runtime telephony** is a separate optional OpenClaw plugin or Hermes skill,
  with separate setup and operational qualification.
- **NetClaw Twilio tools** are the existing core MCP, voice MCP and skills on a
  Focused claw or Comms member. Core MCP uses the reviewed API-key credential path.
  The inbound voice webhook is a distinct process and routing contract.

Use an existing approved test sender and explicit recipients for any separately
reviewed live test. Number purchase, route replacement, SMS, MMS and calls are not
installer checks. Submission and delivery are different outcomes. Signed callbacks
must be validated before delivery evidence is accepted. This spec’s owner excluded
real Twilio use/key resets from installer acceptance; live results remain unverified.

Hermes SMS setup requires the exact public `/webhooks/twilio` URL, keeps its local
listener on loopback and retains signature validation. The auth token stays in
the selected private environment. OpenClaw SMS has a separate pinned plugin and
typed form. The optional Hermes text test reviews its exact sender/recipient and
content, then checks only the returned message identity for delivery evidence.
An unknown send requires reconciliation; it never triggers an automatic resend.

The NetClaw core MCP installs its committed package lock before registration and
loads API-key credentials through the selected home's private launcher. Both
runtimes can discover it. The existing NetClaw voice gateway is OpenClaw-specific;
Hermes does not receive that voice registration. Managed voice cannot fall back to
another model, direct device commands or a neighboring memory service.

## Zoom

Zoom is an existing NetClaw meeting integration, not an invented native chat
channel. Select the full component on a Focused claw or Comms member. Where meeting
input targets a Border, use the same-plan, same-host loopback binding; it generates
a dedicated secret for the two selected homes. A Border supports one such binding
in this baseline. Remote exposure and borrowed mesh credentials are not supported.

The RTMS webhook secret, application credentials, panel feed and Border binding
are distinct setup checks. Account credentials required by an optional REST-trigger
path are not a blanket requirement for every RTMS flow. Historical meeting search
and camera overlay remain separate optional capabilities. Their absence cannot be
reported as a working connection.

Installer MCP discovery is transient and inert: it starts no Zoom webhook, panel,
bridge client or capture, and refuses tool calls. Active operation uses the existing
single process/meeting registry. MCP startup owns the background services and MCP
shutdown closes them; importing the module does not start services. Local lifecycle
checks do not establish provider ingress, meeting capture or historical access.
Listing tools is not evidence of active meeting ingress.

## Read the result correctly

The installer reports configuration, authentication, transport, inbound receipt
and outbound delivery separately. A saved token is configuration, not successful
authentication. A running process is not a connected channel. A provider submission
receipt is not final delivery. A missing safe probe is **unverified**.

Any optional live test identifies its owner, channel, direction, destination and
content for native review. Cancelling sends nothing. An unknown outcome pauses
before another attempt; resuming must not replay a possibly completed send.

Choosing tier 5 opens a per-channel test selection. Only implemented test paths
are offered; imported requests retain their direction and destination reference.
The actual destination and message are reviewed privately at execution. No message
is sent when drafting a request. Current native send receipts prove submission;
they do not claim final delivery. Changing configuration invalidates earlier
message evidence for the current setup report.

## Complete runtime-specific inventory

The entries below come from the official OpenClaw/Hermes guides and were compared
with the pinned sources recorded in Spec155. An option’s presence in documentation
is separate from its availability in a pinned release and its installer qualification.
Use the Comms card’s current disposition; unfinished paths cannot activate services.

### OpenClaw channels

| Option | Native ID | Guide |
| --- | --- | --- |
| A2A | `a2a` | [Official guide](https://docs.openclaw.ai/channels/a2a) |
| Buzz | `buzz` | [Official guide](https://docs.openclaw.ai/channels/buzz) |
| ClickClack | `clickclack` | [Official guide](https://docs.openclaw.ai/channels/clickclack) |
| Discord | `discord` | [Official guide](https://docs.openclaw.ai/channels/discord) |
| Feishu | `feishu` | [Official guide](https://docs.openclaw.ai/channels/feishu) |
| Google Chat | `googlechat` | [Official guide](https://docs.openclaw.ai/channels/googlechat) |
| iMessage | `imessage` | [Official guide](https://docs.openclaw.ai/channels/imessage) |
| IRC | `irc` | [Official guide](https://docs.openclaw.ai/channels/irc) |
| LINE | `line` | [Official guide](https://docs.openclaw.ai/channels/line) |
| Matrix | `matrix` | [Official guide](https://docs.openclaw.ai/channels/matrix) |
| Mattermost | `mattermost` | [Official guide](https://docs.openclaw.ai/channels/mattermost) |
| Microsoft Teams | `msteams` | [Official guide](https://docs.openclaw.ai/channels/msteams) |
| Nextcloud Talk | `nextcloud-talk` | [Official guide](https://docs.openclaw.ai/channels/nextcloud-talk) |
| Nostr | `nostr` | [Official guide](https://docs.openclaw.ai/channels/nostr) |
| QQ bot | `qqbot` | [Official guide](https://docs.openclaw.ai/channels/qqbot) |
| Raft | `raft` | [Official guide](https://docs.openclaw.ai/channels/raft) |
| Reef | `reef` | [Official guide](https://docs.openclaw.ai/channels/reef) |
| Signal | `signal` | [Official guide](https://docs.openclaw.ai/channels/signal) |
| Slack | `slack` | [Official guide](https://docs.openclaw.ai/channels/slack) |
| SMS (Twilio) | `sms` | [Official guide](https://docs.openclaw.ai/channels/sms) |
| Synology Chat | `synology-chat` | [Official guide](https://docs.openclaw.ai/channels/synology-chat) |
| Telegram | `telegram` | [Official guide](https://docs.openclaw.ai/channels/telegram) |
| Tlon | `tlon` | [Official guide](https://docs.openclaw.ai/channels/tlon) |
| Twitch | `twitch` | [Official guide](https://docs.openclaw.ai/channels/twitch) |
| WebChat | `webchat` | [Official guide](https://docs.openclaw.ai/web/webchat) |
| WeChat | `openclaw-weixin` | [Official guide](https://docs.openclaw.ai/channels/wechat) |
| WeCom | `wecom` | [Official guide](https://docs.openclaw.ai/channels/wecom) |
| WhatsApp | `whatsapp` | [Official guide](https://docs.openclaw.ai/channels/whatsapp) |
| X / Twitter | `x` | [Official guide](https://docs.openclaw.ai/channels/x) |
| Yuanbao | `yuanbao` | [Official guide](https://docs.openclaw.ai/channels/yuanbao) |
| Zalo | `zalo` | [Official guide](https://docs.openclaw.ai/channels/zalo) |
| Zalo ClawBot | `openclaw-zaloclawbot` | [Official guide](https://docs.openclaw.ai/channels/zaloclawbot) |
| Zalo personal | `zalouser` | [Official guide](https://docs.openclaw.ai/channels/zalouser) |

### Hermes channels

| Option | Native ID | Guide |
| --- | --- | --- |
| Telegram | `telegram` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) |
| Discord | `discord` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord) |
| Slack | `slack` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/slack) |
| Google Chat | `google_chat` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/google_chat) |
| WhatsApp | `whatsapp` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp) |
| WhatsApp Business (Cloud API) | `whatsapp_cloud` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud) |
| Signal | `signal` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal) |
| SMS (Twilio) | `sms` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/sms) |
| Email | `email` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/email) |
| Home Assistant | `homeassistant` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/homeassistant) |
| Mattermost | `mattermost` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/mattermost) |
| Matrix | `matrix` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/matrix) |
| DingTalk | `dingtalk` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/dingtalk) |
| Feishu / Lark | `feishu` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/feishu) |
| WeCom (Enterprise WeChat) | `wecom` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/wecom) |
| WeCom Callback (Self-Built App) | `wecom_callback` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/wecom-callback) |
| Weixin (WeChat) | `weixin` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/weixin) |
| BlueBubbles (iMessage) | `bluebubbles` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/bluebubbles) |
| Photon iMessage | `photon` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/photon) |
| QQ Bot | `qqbot` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/qqbot) |
| Yuanbao | `yuanbao` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/yuanbao) |
| Microsoft Teams | `teams` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/teams) |
| LINE | `line` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/line) |
| ntfy | `ntfy` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/ntfy) |
| SimpleX Chat | `simplex` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/simplex) |
| Raft | `raft` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/raft) |
| IRC | `irc` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/irc) |
| Buzz | `buzz` | [Official guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/buzz) |

### Related interfaces and NetClaw tools

| Runtime | Option | Kind | Reference |
| --- | --- | --- | --- |
| openclaw | Voice call plugin (including Twilio) | related-telephony-plugin | [Reference](https://docs.openclaw.ai/plugins/voice-call) |
| openclaw | BlueBubbles removal and the imsg iMessage path | retired-path-reference | [Reference](https://docs.openclaw.ai/announcements/bluebubbles-imessage) |
| hermes | Open WebUI | browser-api-interface | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui) |
| hermes | A2A (Agent-to-Agent) | agent-protocol | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/a2a) |
| hermes | Webhooks | event-ingress | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks) |
| hermes | Hermes Relay | connector-transport | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/relay) |
| hermes | Teams Meetings | meeting-workflow | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/teams-meetings) |
| hermes | Microsoft Graph Webhook Listener | microsoft-365-event-ingress | [Reference](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/msgraph-webhook) |
| openclaw | Webex | explicitly-requested-external-plugin | [Reference](https://github.com/JimiHFord/openclaw-webex/blob/1bc3274f262f946e0929de501d0d40c48bf3ef5a/src/plugin.ts) |
| hermes | Optional telephony skill (Twilio) | related-optional-telephony-skill | [Reference](https://github.com/NousResearch/hermes-agent/blob/818c13be1dc4fd28987e1e881a9408224afd4535/optional-skills/productivity/telephony/SKILL.md) |
| openclaw | Twilio core MCP | outbound-and-account-tools | [Reference](https://github.com/twilio-labs/mcp) |
| hermes | Twilio core MCP | outbound-and-account-tools | [Reference](https://github.com/twilio-labs/mcp) |
| openclaw | NetClaw Twilio Voice MCP | voice-tools-and-separate-webhook-ingress | [Reference](https://www.twilio.com/docs/voice) |
| hermes | NetClaw Twilio Voice MCP | voice-tools-and-separate-webhook-ingress | [Reference](https://www.twilio.com/docs/voice) |
| openclaw | Zoom Meeting Intelligence | meeting-ingress-and-context-tools | [Reference](https://developers.zoom.us/docs/rtms/meetings/getting-started/) |
| hermes | Zoom Meeting Intelligence | meeting-ingress-and-context-tools | [Reference](https://developers.zoom.us/docs/rtms/meetings/getting-started/) |

OpenClaw A2A, Buzz, Reef and X are documented but absent from this pinned baseline.
Webex remains visible with its recorded plugin compatibility restriction. Hermes
Home Assistant is Focused-only because its credential also enables device tools.

WebChat uses the OpenClaw Gateway's authenticated loopback connection and Control
UI; it does not install another channel plugin or write the retired `channels.webchat`
section. Connecting a browser is separate from validating the saved configuration.

Prepared native services stay scoped to their selected installation: Signal needs
an already paired loopback daemon; iMessage needs a reviewed local binary, Messages
database path and macOS permissions; Raft needs an External Agent credential/profile;
Buzz needs a reviewed matching native binary. Setup does not borrow an existing
runtime's login or configuration. Hermes WhatsApp and Photon install frozen bridge
dependencies; WhatsApp linking runs only in the selected private native terminal.
Cancelling or losing a pairing outcome pauses that attempt before any retry.
