# Who Minutes is for

Minutes serves two personas. They overlap on capture and diverge on everything
after it. Naming both keeps the roadmap honest: a feature that is essential for
one can be invisible to the other, and that is fine as long as we know which
one we are building for.

## Persona A — the agent-first second brain

*"Minutes is the capture layer of a local second brain, not a notetaker I sit
in."* — a daily user, August 2026

- **Records selectively:** interviews, 1:1s, consulting discovery, community
  calls, voice memos people send them. Not every internal meeting.
- **Uses the desktop app for one thing:** the "Call detected" banner. Native
  mic + system capture that never loses a stem is the entire value of the app
  for them.
- **Lives in an agent afterwards:** Claude Code, Cursor, Codex, or OpenCode
  calling `search_meetings` / `get_meeting` over MCP, or the CLI. They almost
  never open the raw markdown and do not use the built-in recap; they ask the
  agent.
- **Owns the destination:** an Obsidian vault, a wiki, a "digital brain". They
  run their own ingest pass that turns facts, decisions, and action items into
  interlinked pages.
- **Often local-only by policy:** employers that forbid cloud AI assistants;
  `summarization.engine = "none"` or an agent engine is their normal state, not
  a degraded one.

What matters to them, in order: capture reliability → the MCP/CLI/skill
surface (does the agent actually call Minutes instead of grepping the
folder? does it see meetings still in the processing queue?) → structured,
inspectable frontmatter → a clean path into their vault. In-app chat,
document panes, and recap UI are not on their list.

## Persona B — the desktop notetaker

- Records most meetings from the desktop app and reads results there: the
  transcript, the summary, action items, the Recall pane.
- Wants the app to be a complete tool without wiring up an agent: setup,
  permissions, readiness, error messages that name the stage that failed.
- Windows users are disproportionately in this group today, and Windows is
  where capture parity (native mic + Teams/system audio) is still missing.

What matters to them: first-run success on every platform → clear processing
status and recovery → the in-app surfaces (Recall, documents, Coach) → summary
quality.

## How to use this when triaging

- Say which persona a change serves. "Both" is a valid answer; "not sure" is a
  signal to ask a user.
- Capture reliability and permissions serve both and go first.
- The MCP / CLI / skill surface is Persona A's product, not an integration.
  Bugs there (an agent bypassing the skill, stale search during processing,
  API-key handling) are product bugs.
- Summarization must stay optional at every layer. Features may use a summary
  when present; they must not require one.
- In-app assistant surfaces are Persona B work. Ship them, but budget them as
  such rather than assuming they reach everyone.

## Evidence

This doc distills what users said, in their words, on #856 (a product manager
in a regulated workplace using Claude Code as the interface) and #861 (a
consultant folding meetings into an Obsidian wiki through a Cursor agent), and
the Windows setup report in discussion #811. Update it when the picture
changes; it is meant to be argued with.
