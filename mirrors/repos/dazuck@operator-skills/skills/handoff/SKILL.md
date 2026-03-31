---
name: handoff
description: Session wrap-up and handoff to next agent. Verifies work, updates docs, creates handoff message, runs pre-mortem.
---

# Session Handoff Skill

Use this skill when wrapping up a work session to ensure continuity for the next session/agent.

## When to Use

- End of a significant work session
- Before context gets too long
- When switching to a different task/project
- User says "let's wrap up" or "create a handoff"

## Handoff Protocol

Execute these steps in order:

### 1. Verify Work

```
- Run tests: `pnpm test` (if tests exist)
- Run build: `pnpm build`
- Run lint: `pnpm lint` (if configured)
- Note any failures for handoff
```

### 1.5. Commit Changes

If there are uncommitted changes and verification passed, use the `/commit` skill:

```
- Run `/commit` — this handles staging, conventional commit format, AND post-commit reflection
- The commit skill will also surface any learnings from the session
- Note the commit SHA for diary entries
- Do NOT push unless user explicitly requests
```

This ensures work is preserved and learnings are captured before handoff.

### 2. Update Project Diary

Update `.claude/project-diary.md` (create if missing). The diary captures what git cannot.

**DO add:**

1. **Decisions** - Add rows to the Decisions Log table:

   ```
   | Timestamp | Decision | Choice | Rationale | Revisit If | Commit |
   | 2024-12-25 14:30 | [title] | [choice] | [why] | [trigger] | abc1234 |
   ```

2. **Learnings** - Add entries for insights worth preserving:

   ```
   ### 2024-12-25 14:30 - [Title]
   [What happened and the insight. 1-3 sentences.]

   Optional: Suggested action, relevant commits, links.

   ---
   ```

3. **Open Questions** - Update the checklist with new/resolved items

**DO NOT add:**

- Lists of files created/modified (git has this)
- Quality gate checklists (put in commit message)
- Session play-by-play (git log has this)
- Every minor decision (only significant choices between alternatives)

**Include timestamps** (date + HH:MM) on all entries for correlation with git history.

### 3. Update Build Status

Update `.claude/build-status.md` (if exists):

- Mark completed tasks
- Update phase status
- Adjust "Next Actions"
- Update "Recent Completions"

### 4. Generate Handoff Message

Create a message using **prompting best practices** that the user can copy to start a new conversation. The handoff message should treat the receiving agent as a capable leader, not just a task executor.

**Prompting Best Practices to Apply:**

1. **Define the agent's role and identity** - Give them a clear persona (e.g., "project lead", "orchestrator", "senior engineer")
2. **Set behavioral expectations** - What does good leadership look like in this context?
3. **Establish non-negotiables** - What protocols MUST be followed? (TDD, quality gates, etc.)
4. **Provide clear structure** - Numbered priorities, ordered reading list, explicit first actions
5. **Include mindset/philosophy** - Why does this work matter? What's the human context?
6. **Define success criteria** - What does "done" look like?
7. **Use imperative, direct language** - "Start now", "Do this first", not "You might want to..."

**Handoff Message Template (streamlined):**

```
You are [ROLE] for [PROJECT] at [PATH].

CONTEXT:
- Current state: [phase, what's working, what's not]
- Recent work: [1-2 sentence summary]
- Key files: [list 2-3 files to read first]

NEXT ACTIONS:
1. [First thing to do]
2. [Second thing]
3. [Third thing]

WATCH OUT FOR:
- [Gotcha or risk from pre-mortem]

Start by reading [specific file].
```

**Key Principles:**

- Keep it short - the next agent has access to all the docs
- Frontload what's different or non-obvious
- End with a clear first action

### 5. Surface Team Learnings

If you used `/commit` in Step 1.5, learnings were already captured during that skill's reflection phase. Review what was produced:

- **Repo-specific learnings** should have been routed to project docs (AGENT.md, CLAUDE.md, etc.)
- **Cross-cutting learnings** should have been appended to `AGENT-LEARNINGS.md` at the repo root

If you did NOT use `/commit` (e.g., no code changes this session), briefly self-reflect:

- Any non-obvious insights about the codebase, APIs, or tools?
- Any gotchas or dead-ends worth documenting?

If yes, append to `AGENT-LEARNINGS.md` using the format defined there. If no learnings, skip this step.

### 6. Pre-Mortem Analysis

Ask yourself:

- What could go wrong when the next agent picks this up?
- What context might they be missing?
- Are there any "landmines" in the code?
- Is any documentation stale or misleading?

Report findings and suggest mitigations.

### 7. System Improvement Suggestions

Consider if any of these should be updated:

- Project `CLAUDE.md`
- Global `~/.claude/CLAUDE.md`
- Skills
- Guides in `~/.claude/guides/`
- This handoff skill itself

Propose specific changes if warranted.

### 8. Consider Documentation for Publication

If the session involved:

- Significant building or learning
- Insights worth sharing externally
- Artifacts that could be shown (code, configs, processes)
- Decisions or approaches others might benefit from

Suggest running `/writeup` before closing:

> "This session had some learnings that might be worth documenting for your audience. Want to run `/writeup` before closing?"

The `/writeup` skill will assess the work and recommend an appropriate format (tweet, thread, week notes, or full blog post).

## Output Format

Output should be terminal-friendly (minimal markdown, plain text where possible).

Present in this order:

### Part 1: Session Summary (brief)

**Work done:**

- What was accomplished (2-3 bullets max)

**Handoff housekeeping:**

- Verification results (one line: "Tests: ✓ | Build: ✓ | Lint: N/A")
- Commits made (SHA + one-line summary)
- Docs updated (list file names only)

### Part 2: Risks & Improvements (if any)

- Pre-mortem: What could trip up the next agent? (bullets)
- System improvements: Anything worth changing in CLAUDE.md, skills, etc.?
- Writeup suggestion: If session had shareable learnings, mention `/writeup`

Keep this section short. Skip entirely if nothing notable.

### Part 3: Go-Forward Prompt (last, easy to copy)

Put the handoff message in a code block at the very end.
User should be able to scroll up slightly and copy it cleanly.
