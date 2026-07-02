# Slack Setup

Use this path when the user wants Slack mentions to run a local OpenTag coding agent and reply in the same Slack thread.

Read the repository guide as the source of truth before giving credential steps:

```text
docs/platforms/slack.en.md
```

## Recommended Mode

Prefer Slack Socket Mode for local CLI users. It lets `opentag start` receive Slack events over a WebSocket, so the user does not need a public URL.

Use Public Events API only when the user intentionally wants a hosted endpoint or a tunnel-based setup.

## What The User Needs

For Socket Mode:

- Slack App-Level Token, starts with `xapp-`
- Slack Bot User OAuth Token, starts with `xoxb-`
- Slack Team ID
- Slack Channel ID
- The app invited to the target channel

For Public Events API:

- Slack Signing Secret
- Slack Bot User OAuth Token
- A public URL that forwards to the local Slack listener
- Slack Team ID
- Slack Channel ID

Never invent these values. Walk the user through Slack's app page and ask them to paste the values when ready.

## User Path

```bash
npm install -g @opentag/cli
opentag setup
```

During setup, choose:

```text
Platform: Slack
Connection mode: Local Socket Mode, unless the user explicitly wants Public Events API
Coding agent: Codex or Claude Code for real work; Echo only for dev/test
Project: the local checkout OpenTag should operate on
```

Then:

```bash
opentag start
```

Keep it running and mention the Slack app in the configured channel.

## Verification

```bash
opentag status
opentag doctor
opentag config show
```

In Slack:

```text
@OpenTag investigate this
```

Use the app's actual Slack display name. If the app is not in the channel, invite it first:

```text
/invite @OpenTag
```

## Success Criteria

- Socket Mode connects, or Public Events API receives the Slack request.
- A Slack `app_mention` creates a run.
- The selected local executor starts.
- OpenTag replies in the same Slack thread.

If the reply includes a pull request action, GitHub PR creation needs a GitHub repository target and token too. Slack credentials alone prove Slack delivery, not GitHub write access.
