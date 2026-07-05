# Codex And Claude Code Runners

Use this path when the user wants OpenTag to run real coding work with Codex or Claude Code.

## Executor Choices

- Codex uses the local `codex` command.
- Claude Code uses the local `claude` command.
- Echo is dev/test only and does not run a real coding agent.

Prefer the executor the user already has installed. Do not silently switch executors without telling the user.

## Prerequisites

For Codex:

```bash
codex --version
```

For Claude Code:

```bash
claude --version
```

The user also needs a local project checkout that the chosen executor can safely edit.

## User Path

```bash
npm install -g @opentag/cli
opentag setup
```

During setup, choose Codex or Claude Code when asked:

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
