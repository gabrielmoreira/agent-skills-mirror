# ACP Coding-Agent Runners

Use this path when the user wants OpenTag to run real coding work with Codex, Claude Code, Cursor, OpenCode, Hermes, or OpenClaw.

## Executor Choices

- Codex uses the bundled `codex-acp` adapter and the user's existing Codex login.
- Claude Code uses the bundled `claude-agent-acp` adapter and the user's existing Claude login.
- Hermes uses the installed `hermes` ACP server with a fixed profile whose provider is already configured.
- Cursor uses the installed `cursor-agent acp` command and an existing Cursor login.
- OpenCode uses the pinned `opencode-ai` ACP server and an authenticated provider.
- OpenClaw uses the installed Gateway ACP bridge. It currently reports `cancel=no`; inspect provider-owned processes after cancellation before starting conflicting work.
- Echo is dev/test only and does not run a real coding agent.

Prefer the executor whose authentication or Hermes provider is already ready. Do not silently switch executors without telling the user.

## Prerequisites

For Codex, Claude Code, Cursor, OpenCode, and OpenClaw:

```bash
opentag doctor
```

For Hermes:

```bash
hermes profile list
```

The user also needs a local project checkout that the chosen executor can safely edit.

## User Path

```bash
npm install -g @opentag/cli
opentag setup
```

During setup, choose Codex, Claude Code, Cursor, OpenCode, Hermes, or OpenClaw when asked:

```text
Which coding agent should OpenTag use?
```

Then:

```bash
opentag start
```

Keep it running while testing a real mention from Slack, GitHub, GitLab, Lark / Feishu, Telegram, or Discord.

## Working Tree Rule

Before asking OpenTag to perform write-capable work, check the target repository:

```bash
git status --short
```

If there are unrelated dirty changes, ask the user how to proceed. Do not discard user changes.

## GitHub Pull Requests

Creating a pull request from a run needs more than a coding executor:

- A GitHub repository target in OpenTag config.
- A GitHub token for comments and pull requests.
- Local git remote credentials that can push run branches.

The normal flow is:

1. The executor changes files.
2. OpenTag prepares and pushes a run branch.
3. OpenTag shows a `create_pull_request` action.
4. The user replies `apply 1`.
5. OpenTag creates the pull request.

Do not promise PR creation unless those conditions are met.

## Verification

```bash
opentag executors
opentag status
opentag doctor
```

Success means OpenTag can see the configured executor, start the local runtime, receive a real platform mention, and return either a completed result or a clear actionable error.
