# NTM Command Patterns

Use this file when the main `ntm` skill body is not enough and you need the denser
operator command patterns that make NTM powerful in practice.

## Contents

- [Session Lifecycle](#session-lifecycle) — quick, spawn, scale, rebalance, adopt
  - [Agent Count Heuristics](#agent-count-heuristics)
- [High-Leverage Send Patterns](#high-leverage-send-patterns) — targeting, file-backed, smart routing, distribute
- [Monitoring and Output](#monitoring-and-output) — capture, activity, health, diff
  - [Human-Only Surfaces](#human-only-surfaces) — dashboard, palette, bind
- [Work Intelligence](#work-intelligence) — triage, alerts, impact, assign
- [Coordination, Recovery, and Durable State](#coordination-recovery-and-durable-state) — mail, locks, checkpoint, timeline, resume, handoff
  - [Controller Agents](#controller-agents)
- [Reusable Assets](#reusable-assets) — recipes, workflows, templates

---

## Session Lifecycle

```bash
ntm quick myproject --template=go       # template = go | python | node | rust
ntm quick myproject --label frontend

ntm spawn myproject --cc=3 --cod=2 --agy=1
ntm spawn myproject --label frontend --cc=3
ntm spawn myproject --label backend --cc=2 --worktrees
ntm spawn myproject --no-user --cc=5 --cod=5
ntm spawn myproject --stagger-mode=smart   # smart | fixed | none
ntm spawn myproject --cc=3 --verify-boot   # block up to 30s until every agent is ready (no fixed sleeps)
ntm add myproject --cc=2
ntm add myproject --label frontend --cc=1

ntm list                            # --limit/--offset paginate; JSON adds count/total_matches/has_more
ntm status myproject
ntm attach myproject
ntm zoom myproject 1
ntm kill myproject
ntm kill myproject --pane=2         # remove one pane; session and siblings survive
ntm kill --project myproject

# Adjust a running swarm without re-spawning
ntm scale myproject --cc=4
ntm rebalance myproject
ntm respawn myproject           # revive dead panes in place (prompts unless -f; --panes takes bare index or %ID only)
ntm swarm plan                  # dry-run spawn
ntm swarm status
ntm swarm stop <pattern>

# Adopt an existing external tmux session into ntm
ntm adopt <session>
```

> `ntm view` is a human-operator command that retiles the tmux layout. Do not call it from agent code — use `--robot-tail`, `--robot-snapshot`, or `--robot-inspect-pane` instead.

### Agent Count Heuristics

- `--cc=3 --cod=2 --agy=1`: good default mixed swarm
- `--cc=5`: architecture-heavy, lower coordination load
- `--cc=2 --cod=3`: straightforward implementation volume
- `--cc=5 --cod=5`: larger swarm only when the operator loop is already healthy

## High-Leverage Send Patterns

```bash
# Basic targeting
ntm send myproject --cc "Review the API design"
ntm send myproject --cod --agy "Run tests and summarize failures"
ntm --robot-send=myproject --msg="Checkpoint and summarize current state"
ntm send myproject --pane=2 "You own the auth migration."       # single-window shorthand
ntm send myproject --pane=1.0 "You own this exact pane."        # exact window.pane
ntm send myproject --panes=%7,2.0 "Pair on the broken build."   # exact pane ID + window.pane
ntm --robot-send=myproject --panes=%7,%8 --msg="Pair on the broken build."  # exact pane IDs
ntm send myproject --cc --loop-mode "Status check: report blockers"  # repeated tending nudges without a CASS dup prompt

# Broadcast across labeled sessions for one base project
ntm send --project myproject "Sync to main and report blockers."

# File-backed prompts, stdin, and reusable wrappers
ntm send myproject --file prompts/review.md
git diff | ntm send myproject --cc --cod --agy --prefix "Review these changes:"
ntm send myproject --base-prompt-file ./common-instructions.txt --file ./task.txt

# File context and templates
ntm send myproject -c internal/auth/service.go "Refactor this safely"
ntm send myproject -c a.go -c b.go "Compare these implementations"
ntm send myproject -t fix --var issue="nil pointer" --file internal/auth/service.go

# Smart routing and automated distribution
ntm send myproject --smart "Take the next auth follow-up"
ntm send myproject --smart --route=sticky "Continue the migration work"   # strategies: least-loaded, first-available, round-robin, round-robin-available, random, sticky, explicit
ntm send myproject --distribute --dist-strategy=dependency
ntm send myproject --distribute --dist-auto --dist-strategy=balanced

# Batch / randomized sends
ntm send myproject --batch prompts.txt --delay=5s
ntm send myproject --batch prompts.txt --broadcast
ntm send myproject --cc --cod --agy --randomize
```

## Monitoring and Output

```bash
# Output capture
ntm copy myproject:1
ntm copy myproject --all
ntm copy myproject --cc
ntm copy myproject --code
ntm save myproject

# Activity and stream monitoring
ntm activity myproject --watch
ntm health myproject
ntm watch myproject --cc
ntm logs myproject --panes=1,2

# Compare / inspect
ntm extract myproject --lines=200
ntm diff myproject cc_1 cod_1
ntm grep "timeout" myproject -C 3
```

### Human-Only Surfaces

These are excellent for operators, but not for agents driving automation:

```bash
ntm dashboard myproject
ntm palette myproject
ntm bind
ntm tutorial
ntm web                 # v1.25+: HTTP server + embedded web dashboard at / (same as ntm serve --web)
```

## Work Intelligence

```bash
ntm work triage
ntm work triage --by-label
ntm work triage --by-track
ntm work triage --format=markdown --compact
ntm work alerts
ntm work search "JWT authentication"
ntm work impact internal/api/auth.go
ntm work next
ntm work history
ntm work forecast br-123
ntm work graph
ntm work label-health
ntm work label-flow

ntm bugs list                                   # one-shot UBS scan of the project
ntm bugs watch                                  # rerun periodically; new findings nudge the reservation holder ([bugs] push_routing is opt-in)
```

Use `ntm assign` when you want NTM to help push work onto panes instead of just
observing the graph:

```bash
ntm assign myproject --auto --strategy=dependency
ntm assign myproject --beads=br-123,br-124 --agent=codex
```

## Coordination, Recovery, and Durable State

```bash
ntm mail send myproject --all "Report blockers and current file focus."
ntm mail inbox myproject                        # or: ntm mail inbox myproject --json
ntm locks list myproject --all-agents
ntm locks list myproject --check-deadlocks      # detect reservation wait-for cycles (adds 'deadlocks' to --json)
ntm locks renew myproject --extend 30           # minutes
ntm locks force-release myproject 42 --note "agent inactive"
# force-release is approval-gated by default (automation.force_release=approval):
# the first run files a durable approval; a SECOND operator must `ntm approve <id>`
# (self-approval is rejected); rerunning then consumes the approval and executes once.
# Solo operator: `ntm policy automation --force-release auto` permits unattended runs.
ntm coordinator status myproject                # alias: ntm coord status
ntm coordinator digest myproject
ntm coordinator conflicts myproject
ntm coordinator enable auto-assign              # background automation
ntm coordinator enable digest --interval=30m    # --interval is digest-only
ntm coordinator enable mail-nudge               # nudge idle panes with unread Agent Mail (persists to config; restart daemon to apply)

ntm checkpoint save myproject -m "before risky refactor"
ntm checkpoint list myproject
ntm checkpoint restore myproject                # optional <id> positional
ntm checkpoint export myproject <id>            # portable archive
ntm checkpoint import <archive>
ntm checkpoint verify myproject
ntm checkpoint show myproject <id>

ntm timeline list
ntm timeline show <session-id>
ntm timeline stats
ntm history search "authentication error"
ntm history --limit=50                          # --offset counts back from the newest entry
ntm audit show myproject
ntm audit search "<pattern>"
# Pagination (v1.25+): list, history, audit show/search, checkpoint list, and
# approve list all take --limit/--offset and return count/total_matches/has_more
# plus _agent_hints.next_offset in JSON mode.

# changes vs conflicts are TWO separate top-level commands (not a nested form):
ntm changes myproject                           # recent attributable file changes
ntm conflicts myproject --since 6h --limit 10   # files touched by multiple agents

ntm resume myproject

# Cross-session handoff bundles
ntm handoff create myproject
ntm handoff list
ntm handoff show <path>
ntm handoff ledger
```

### Controller Agents

```bash
ntm controller myproject                        # coord agent in pane 1 (default cc)
ntm controller myproject --agent-type=cod       # cc|cod|gmi|agy|cursor|windsurf|ws|aider|oc|ollama
ntm controller myproject --prompt=ctrl.txt      # template vars: {{.Session}} {{.AgentList}} {{.ProjectDir}}
ntm controller myproject --no-prompt            # launch agent but send no initial prompt
```

Worktree-specific commands when repo policy allows them:

```bash
ntm worktrees list
ntm worktrees merge claude_1
ntm worktrees clean --session myproject
```

## Reusable Assets

```bash
ntm recipes list
ntm recipes show full-stack
ntm workflows list
ntm workflows show red-green
ntm workflow run red-green --var feature="parser rewrite"   # v1.25+: actually EXECUTES the
#   coordination loop against live panes through the gated dispatch path (dead-pane gate +
#   composer-verified submission). Accepts the 4 builtins (red-green, review-pipeline,
#   specialist-team, parallel-explore), user TOMLs (~/.config/ntm/workflows/,
#   .ntm/workflows/), or a .toml path. `ntm spawn -t <workflow>` only sizes a session.
ntm template list
ntm template show fix-bug
ntm session-templates list
ntm session-templates show refactor
```

Use these when you want repeatable swarm composition rather than bespoke commands every time.
