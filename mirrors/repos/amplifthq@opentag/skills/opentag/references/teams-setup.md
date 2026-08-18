# Microsoft Teams Setup

Use this path for the Microsoft Teams preview. Teams ingress currently runs
only in the local runtime; hosted/custom relay mode does not mount the webhook.
Use `docs/platforms/teams.en.md` for the Azure Bot, Teams app package, tunnel,
Messaging endpoint, and permission checklist.

## Safe Setup

Use the interactive prompt so the Azure Bot client secret does not enter shell
history:

```bash
opentag setup --platform teams
```

Do not put `--teams-app-password` and its value in a command, chat message,
issue, screenshot, or committed file. Have the user enter it locally when
prompted.

Configure the Azure Bot Messaging endpoint as public HTTPS ending in
`/teams/messages`, install the Teams app in the target team/channel, then keep
`opentag start` running or use the background service.

## Channel Binding

Capture the tenant ID and base channel conversation ID from an authenticated
Teams activity. Use `activity.conversation.id` as `conversationId`, removing only a trailing `;messageid=<root>` suffix when present.
Do not use `channelData.channel.id` or `channelData.teamsChannelId` as
`conversationId`.

There is currently no standalone Teams channel-binding CLI command. Use the
deployment's operator-controlled local config or dispatcher API to create the
binding, following `docs/platforms/teams.en.md`. Do not invent an endpoint or
config shape. A repository target is optional for general ACP work and required
for repository-backed coding or `apply 1`.

## Verify

```bash
opentag service status
opentag doctor
opentag status
```

Send a read-only `@OpenTag investigate ...` mention first. Confirm Teams posts
to `/teams/messages`, OpenTag accepts the activity, a run starts in the intended
checkout or scratch workspace, and the reply returns to the same channel
thread.
