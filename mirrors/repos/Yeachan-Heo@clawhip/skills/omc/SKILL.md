# clawhip × OMC (oh-my-claudecode)

Launch [OMC](https://github.com/Yeachan-Heo/oh-my-claudecode) coding sessions with automatic Discord notifications via clawhip.

## What you get

- Legacy-compatible `agent.started`, `agent.finished`, and `agent.failed` wrapper emits via `clawhip emit`
- clawhip-side normalization of richer native OMC/OMX events into the canonical `session.*` routing contract
- Session keyword alerts (error, PR created, complete, etc.)
- Stale session detection (no output for N minutes)
- All notifications routed to the correct Discord channel
- Direct Slack/Discord notifications inside OMC/OMX should be treated as deprecated in clawhip-integrated setups

## Prerequisites

- [clawhip](https://github.com/Yeachan-Heo/clawhip) installed and daemon running
- [OMC](https://github.com/Yeachan-Heo/oh-my-claudecode) installed
- tmux

## Usage

### Create a session

```bash
./create.sh <session-name> <worktree-path> [prompt] [channel-id] [mention]
```

```bash
# Basic — uses clawhip default channel
./create.sh issue-123 ~/my-project/worktrees/issue-123

# Start a session and auto-send an initial prompt after the TUI initializes
./create.sh issue-123 ~/my-project/worktrees/issue-123 "Fix the bug in src/main.rs and create a PR to dev"

# With prompt, specific channel, and mention
./create.sh issue-123 ~/my-project/worktrees/issue-123 "Fix the bug in src/main.rs and create a PR to dev" 1234567890 "<@user-id>"
```

`create.sh` now emits lifecycle notifications directly from the OMC shell session, so you no longer need a separate lifecycle watcher command. If you pass a prompt, the script waits 10 seconds for the TUI to initialize, then sends the prompt via `tmux send-keys -l` before pressing Enter.

### Send a prompt

```bash
./prompt.sh <session-name> "Fix the bug in src/main.rs and create a PR to dev"
```

`prompt.sh` sends prompt text in tmux literal mode (`send-keys -l`) and presses Enter separately so quotes, punctuation, and leading dashes are preserved exactly.

### Monitor output

```bash
./tail.sh <session-name> [lines]
```

## Customization

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAWHIP_OMC_KEYWORDS` | `error,Error,FAILED,PR created,panic,complete` | Comma-separated keywords to monitor |
| `CLAWHIP_OMC_STALE_MIN` | `30` | Minutes before stale alert |
| `CLAWHIP_OMC_FLAGS` | `--openclaw --madmax` | Extra flags passed to `omc` |
| `CLAWHIP_OMC_ENV` | *(empty)* | Extra env vars prepended to omc command |
| `CLAWHIP_OMC_PROJECT` | detected from the git common dir (fallback: worktree name) | Override the project name sent in lifecycle events |

### Config defaults

Set defaults in `~/.clawhip/config.toml`:

```toml
[skills.omc]
channel = "1234567890"
mention = "<@your-user-id>"
keywords = "error,Error,FAILED,PR created,complete"
stale_minutes = 30
flags = "--openclaw --madmax"
```
