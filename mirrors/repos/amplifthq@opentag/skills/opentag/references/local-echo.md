# Local Echo Loop

Use this path when the user wants to prove the CLI and local runtime work before connecting a real platform or coding agent.

## What Echo Means

Echo is a dev/test executor. It does not run Codex, Claude Code, or any real code changes. It only proves that OpenTag can save config, start locally, create a run, and return a visible result.

Do not recommend Echo for real use unless the user explicitly wants a smoke test.

## User Path

Install or run the CLI:

```bash
npm install -g @opentag/cli
opentag setup
```

During setup, choose:

```text
Coding agent: Echo
Platform: whichever platform the user wants to test, or the smallest available local path
Project: the local checkout the user wants OpenTag to know about
```

Then start OpenTag:

```bash
opentag start
```

Keep that process running. Stop it with Ctrl-C.

## Verification

Use the CLI status commands first:

```bash
opentag status
opentag doctor
opentag config show
```

For a platform-backed Echo smoke, send a real mention from the connected platform. Expected result:

1. OpenTag receives the mention.
2. The local dispatcher creates a run.
3. Echo completes without changing files.
4. OpenTag replies back to the same platform thread or conversation.

## Success Criteria

- `opentag setup` writes `~/.config/opentag/config.json`.
- `opentag start` reports that the dispatcher and selected listener are running.
- `opentag status` can read the config.
- A real platform mention produces a visible Echo response or a clear actionable error.
