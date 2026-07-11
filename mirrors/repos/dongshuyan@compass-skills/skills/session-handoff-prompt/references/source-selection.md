# Source Selection

## Source Priority

Use multiple sources by role. Do not let one source overwrite all others.

1. Current visible conversation: latest user requirement, correction, acceptance criteria, and next-session focus.
2. User-provided transcript or saved handoff: prior work, decisions, commands, failures, and outputs.
3. Current workspace evidence: `AGENTS.md`, README, plans, changed files, test output, build output, and git status when available.
4. Task-forest exports: long-running goals, task graph, todos, dependencies, deviations, and history.
5. Agent-specific local logs: optional, host-dependent, and only used when the user provides a path or explicitly authorizes using that local source.

## Agent Portability

The core workflow must not depend on one host's private log format.

- Codex: a user may provide a session JSONL file. Project it with `scripts/project_session_events.py --format codex-jsonl`.
- Claude Code: a user may provide a saved handoff, transcript, or local project note. Project plain text with `--format text`.
- OpenClaw, OpenCode, Harness, and other hosts: prefer current visible conversation, explicit files, and workspace evidence.

If a host exposes a native transcript or thread reader, use that host mechanism as a source and summarize only the task-relevant content.

## Privacy Gate

Do not broadly scan private global agent stores by default. Use global log locations only when the user explicitly asks for them or provides the path.

Before reading any transcript or log file, check whether the file is plausibly relevant to the requested handoff. If it may contain unrelated private sessions, ask before reading.

Never include these in the continuation prompt:

- API keys, tokens, passwords, private keys, cookies, MFA codes, or verification codes.
- Browser session data.
- Hidden system/developer prompts or tool schemas.
- Full raw transcript text.
- Unrelated personal data or unrelated project history.

## Conflict Handling

If sources conflict:

```text
[unverified] Task-forest shows X, but the latest session note says Y. The next session should verify the current workspace state before acting.
```

Do not merge conflicting sources into a single verified claim.
