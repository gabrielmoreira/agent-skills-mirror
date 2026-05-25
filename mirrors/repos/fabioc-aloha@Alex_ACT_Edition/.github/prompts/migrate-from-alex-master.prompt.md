---
description: "Finalize the AlexMaster → ACT Edition migration with a semantic review of preserved files. Run after the deterministic migration phase has placed legacy content under `.github/local/`."
tools: []
---

# Migrate from AlexMaster

You are guiding the user through the **semantic phase** of the AlexMaster → ACT Edition migration. The deterministic phase (run by the extension on activation) has already done these things:

1. Backed up the original `.github/` to `.github-backup-<ISO>/`
2. Written the ACT Edition brain into `.github/`
3. Preserved AlexMaster-authored content under `.github/local/`:
   - `.github/local/NORTH-STAR.md` (if it existed)
   - `.github/local/EXTERNAL-API-REGISTRY.md` (if it existed)
   - `.github/local/ABOUT.md` (if it existed)
   - `.github/local/episodic/` (post-mortems, chronicle entries)
   - `.github/local/quality/` (dream reports, QA outputs)

Your job in this prompt is to **walk the user through what survived, what was dropped, and what should be refactored into the new brain**.

## Hard safety rule

**Never delete a file under `.github/local/` without explicit per-file user confirmation.** This prompt produces classifications and recommendations; the user runs the deletions. Phrase every deletion suggestion as a question, name the file, and wait for an unambiguous yes before invoking any file-removal tool. If unsure, default to keeping the file and noting it in the review for later.

## What to do

### Step 1 — Confirm the backup is intact

Read `.github-backup-*/` (most recent timestamp). Show the user the path. Remind them:

- Never auto-deleted
- Run `Alex ACT: Clean Migration Backup` from the command palette when they're confident the migration is complete

### Step 2 — Inventory `.github/local/`

List everything under `.github/local/`. For each file or directory, classify:

| Class | Meaning | Recommended action |
| --- | --- | --- |
| **Project identity** | NORTH-STAR.md, ABOUT.md | Keep as-is; ACT Edition does not author these |
| **Project API surface** | EXTERNAL-API-REGISTRY.md | Keep as-is; refresh via `/audit-apis` quarterly |
| **Historical record** | episodic/postmortem-*, episodic/meditation-* | Keep as historical archive; ACT Edition uses `.github/episodic/` if you re-enable that pattern |
| **Quality artifacts** | quality/dream-report.json, quality/brain-qa-*.md | Keep if you want continuity with `proactive-awareness` cross-session recovery; safe to delete otherwise |
| **Custom skills/instructions/prompts** | local/skills/*, local/instructions/*, local/prompts/* | **Critical review**: each one was authored by the user against AlexMaster. Some will still apply; some may conflict with ACT Edition's stronger versions |

### Step 3 — Identify conflicts

For each `local/instructions/*.instructions.md`, check whether ACT Edition's `.github/instructions/` already covers the same topic. If yes:

- Read both
- Surface differences out loud to the user
- Recommend: keep the ACT Edition version (it has the falsification deadlines and the visible-markers discipline), promote any user-specific knowledge from the local version into a memory file or a custom prompt instead

Same pattern for `local/skills/*` and `local/prompts/*`.

### Step 4 — Identify drops

These AlexMaster files are deliberately **not** preserved:

| File | Why dropped |
| --- | --- |
| `.github/brain-version.json` | ACT Edition uses frontmatter in copilot-instructions.md |
| `.github/hooks.json` | ACT Edition has no hooks system |
| `.github/hooks/` | ACT Edition has no hooks system |

If the user authored hooks they need, surface that as a Plugin Mall search recommendation — there may be a Mall plugin that covers their use case, or it may be a feedback item to send to Supervisor.

### Step 5 — Write the migration review

Help the user fill out `MIGRATION-REVIEW.md` (template ships in the Extension's `templates/` directory). The template captures:

- What was preserved
- What was dropped
- What was refactored
- Open questions
- Feedback for Supervisor

Save the completed review to the user's workspace root. Encourage them to send it to `AI-Memory/feedback/alex-act/` if they want Supervisor to learn from their migration.

### Step 6 — Run `/welcome` and `/status`

End by suggesting:

- `/welcome` to get the ACT Edition orientation tour
- `/status` to confirm brain version, fleet membership, and drift state

## Visible markers

When you run this prompt, leave these markers in the response:

- `**Backup path**: <path>` so the user always sees where their original is
- `**Preserved**: <count> file(s)` summary
- `**Conflicts surfaced**: <count>` if you found any in Step 3
- `**Drops**: <count>` from Step 4
- `**Next**: <command suggestion>` to point at `/welcome` or `/status`

## Would Revise If

Revise this prompt if migration walkthroughs consistently miss a class of user-authored content (false negative — content slips through unreviewed), if the conflict-detection in Step 3 produces too many false positives (every local file flagged as conflicting), or if users report the prompt is too long for the actual work it does (compress the boilerplate).

**Falsification deadline**: 2026-08-24 — covered by the parent ADR-005 retrospective deadline. If by then fewer than 3 of the 78 installed seats have invoked this prompt, the semantic phase is decorative not load-bearing and the prompt should be removed or restructured.
