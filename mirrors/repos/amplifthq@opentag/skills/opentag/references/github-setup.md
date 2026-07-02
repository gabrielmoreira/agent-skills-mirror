# GitHub Setup

Use this path when the user wants GitHub comments to run a local OpenTag coding agent and reply back on GitHub.

Read the repository guide as the source of truth before giving credential steps:

```text
docs/platforms/github.en.md
```

## Current Product Path

The CLI currently uses a repository webhook. GitHub sends comment events to a public tunnel, OpenTag receives them locally, runs the selected coding agent, and posts replies back to the same GitHub issue or pull request thread.

GitHub App installation is the longer-term product direction, but it is not the default CLI setup yet.

## What The User Needs

- GitHub repository, usually `owner/repo`
- A local checkout of that repository
- A public tunnel to the local GitHub listener
- A repository webhook pointing to that tunnel
- A GitHub token for comments and pull request creation
- Local git credentials that can push branches to `origin` if `apply 1` should create a PR

Never invent tokens, owner names, repository names, webhook secrets, or project paths.

## User Path

```bash
npm install -g @opentag/cli
opentag setup
```

During setup, choose:

```text
Platform: GitHub
Coding agent: Codex or Claude Code for real work; Echo only for dev/test
Project: the local checkout OpenTag should operate on
```

OpenTag can generate the webhook secret and save the local runtime config. The user still needs to create the public tunnel and repository webhook because GitHub cannot call `localhost` directly.

Then:

```bash
opentag start
```

Keep it running while testing GitHub comments.

## PR Action Flow

When the coding agent changes files, OpenTag prepares and pushes a run branch, then shows a `create_pull_request` action in the GitHub thread. The user creates the PR by replying:

```text
apply 1
```

That requires:

- GitHub token saved in OpenTag config.
- The run branch already pushed to the remote repository.
- Local git remote credentials that can push the branch.

If the token is missing, OpenTag may still run the agent but cannot post GitHub comments or create the final pull request.

## Verification

```bash
opentag status
opentag doctor
opentag config show
```

In GitHub, comment on an issue or pull request review thread:

```text
@opentag investigate this
```

Expected result:

1. GitHub delivers the webhook to the tunnel.
2. OpenTag creates a run.
3. The local executor starts.
4. OpenTag posts progress and final result comments.
5. If files changed, `apply 1` creates a pull request.

## First Checks When It Fails

- The tunnel is running and points at the GitHub listener port from `opentag start`.
- The repository webhook URL ends with `/github/webhooks`.
- The webhook uses `application/json`.
- The webhook secret matches the secret saved by OpenTag.
- The webhook subscribes to issue comments and pull request review comments.
- The GitHub token has write access to issues and pull requests.
- The local `origin` remote can push branches.
