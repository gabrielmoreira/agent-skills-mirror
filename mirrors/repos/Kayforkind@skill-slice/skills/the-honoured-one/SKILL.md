---
name: the-honoured-one
description: "Forces a four-phase context-load protocol (audit unread files, read them, map architecture, then act) before multi-file features, integrations, refactors, or debugging unread code. Use when adding a feature to existing code, integrating X with Y, or asking why unread code fails. Not for isolated single-file edits already read this session. Do not use as a substitute for systematic-debugging's reproduce-then-fix loop."
version: 1.0.1
risk: safe
source: community
date_added: "2026-06-25"
---

# the-honoured-one — Full Context Load Protocol

## Overview

> Gojo at full power means all six eyes open — everything visible, nothing assumed, no blind spots. The Honoured One doesn't act on guesses. This skill enforces the same: the AI must earn the right to act by reading and understanding first.

The most common AI coding failure is **confident wrongness** — the AI proposes or implements something based on how it assumes the code is structured, not how it actually is. It gets the architecture wrong, uses a pattern inconsistent with the rest of the codebase, or integrates with a module it never actually opened. This skill eliminates that failure mode by making context-loading mandatory before any action.

---

## When to Use

- **Use** when modifying multiple files in an existing codebase
- **Use** when designing or modifying a system component
- **Use** when adding a feature that integrates with existing code
- **Use** when debugging a system or component the AI has not yet read
- **Use** when the AI would need to assume how existing code is structured
- **DO NOT** use for isolated single-file tasks where the file has already been read

### Trigger Phrases

- "add this feature to the existing code"
- "integrate X with Y"
- "modify how [system] works"
- "refactor this"
- "why is this not working" (on unread code)
- Any task touching more than one file
- Any task where the AI would need to know how existing code is structured to do it correctly

---

## Prerequisites

- An existing codebase with files the AI can read
- The AI must have file-reading capability in the current environment
- No prior assumptions about codebase structure — this skill exists to eliminate them

---

## Procedure

The protocol runs in four sequential phases. **The AI may not propose solutions, make plans, or write code until all four phases are complete.**

### Phase 1 — Context Audit

When given any complex task, the AI must immediately perform a context audit before proposing anything. It declares three things:

1. **What files are relevant to this task?** — Every file that will be read, changed, or is upstream/downstream of the change
2. **Which of those has the AI actually read this session?** — Honest accounting, no assumptions
3. **What gaps exist?** — Files that are relevant but unread

**Output format:**

```
THE HONOURED ONE — CONTEXT AUDIT
─────────────────────────────────────────
Task: [what was asked]

Relevant files identified:
  - src/auth/middleware.ts       → [why relevant]
  - src/routes/user.ts          → [why relevant]
  - src/models/user.model.ts    → [why relevant]
  - src/utils/token.ts          → [why relevant]

Files read this session:
  - src/routes/user.ts          → ✓ read

Unread but relevant (blind spots):
  - src/auth/middleware.ts       → ✗ not read
  - src/models/user.model.ts    → ✗ not read
  - src/utils/token.ts          → ✗ not read
─────────────────────────────────────────
Cannot proceed — reading blind spots now.
```

> **The AI cannot propose a solution, make a plan, or write any code while blind spots exist.**

### Phase 2 — Mandatory Read Pass

The AI reads every file listed as a blind spot. Not summaries, not assumptions based on filename or folder structure — **actual reads**.

**Rules for this phase:**

1. If a file imports from another file that is also relevant, that file gets added to the read list
2. If reading a file reveals unexpected structure or patterns, the AI notes this before continuing
3. The AI does not form opinions or solutions while reading — this phase is **observation only**
4. **Shortcut rule:** The AI cannot say "I'm familiar with this pattern so I don't need to read it." Familiarity with a pattern is not familiarity with this codebase's implementation of it.

### Phase 3 — Orientation Statement

After all relevant files are read, the AI outputs an orientation statement before proposing anything. This is its proof that it understands the codebase well enough to act:

```
THE HONOURED ONE — CONTEXT LOADED
─────────────────────────────────────────
Files read: [complete list]

Current architecture (what I now know):
  [2-3 sentences describing how the relevant system actually works,
   based on what was read — not assumed]

What this task touches:
  - [file/component 1] → [how it's involved]
  - [file/component 2] → [how it's involved]

Existing patterns I must follow:
  - [naming convention / error handling style / structure pattern observed]
  - [any other conventions seen in the actual code]

Remaining unknowns:
  - [anything still unclear — or "None, ready to proceed"]
─────────────────────────────────────────
```

### Phase 4 — Confidence Gate

After the orientation statement, the AI applies a confidence gate before acting:

**If "Remaining unknowns" is empty:**
→ Proceed. The AI is fully loaded and may propose a solution or begin work.

**If "Remaining unknowns" is non-empty:**
→ The AI must resolve every unknown before proceeding. Options:
1. Ask the user the specific question
2. Read another file that would answer it
3. Acknowledge the unknown, state the assumption being made, and get user confirmation before continuing

> **The AI cannot proceed with known blind spots.** Stating "I'll assume X" and moving forward without user confirmation is not allowed.

### Self-Ask Before Acting

Before writing any code or making any proposal, the AI must answer all four questions:

| # | Question | Required Answer |
|---|---|---|
| 1 | Have I read every file this task touches? | Yes — or stop and read |
| 2 | Do I understand how this codebase handles [relevant pattern]? | Yes, from reading — not assuming |
| 3 | Am I following the conventions I actually observed in the code? | Yes — or flag the deviation |
| 4 | Do I have any remaining blind spots? | No — or resolve them first |

### Quick Reference

| Phase | Action | May Propose/Code? |
|---|---|---|
| 1 — Audit | List relevant files, identify blind spots | ❌ No |
| 2 — Read | Read all blind spot files | ❌ No |
| 3 — Orient | Output orientation statement | ❌ No |
| 4 — Gate | Confirm no unknowns remain | ✅ Yes, if gate passes |

---

## Hard Rules (Never Violated)

- **No proposing solutions before reading.** Proposals based on assumptions are not proposals — they are guesses.
- **No "I assume this file does X."** If you haven't read it, you don't know what it does.
- **No skipping files because their names look obvious.** A file called `utils.ts` can contain anything.
- **No importing or calling code from files that haven't been read.** You cannot use what you haven't seen.
- **No "familiar pattern" shortcuts.** The pattern may be implemented differently here.
- **No acting with known unknowns.** Resolve them or get user confirmation before proceeding.

---

## Pitfalls

- **Problem:** The AI assumes an implementation matches a common pattern without reading it.
  **Solution:** Enforce Phase 2 (Mandatory Read Pass) without exceptions.

- **Problem:** The AI skips reading a file because its name seems obvious (e.g., `utils.ts`, `helpers.js`).
  **Solution:** File names are not content. Every blind spot file must be read regardless of how predictable its name appears.

- **Problem:** The AI states "I'll assume X" and proceeds without user confirmation.
  **Solution:** Phase 4 Confidence Gate requires explicit user confirmation for any assumption. No silent assumptions allowed.

- **Problem:** The AI forms opinions or solution ideas during Phase 2 reading, contaminating its observation.
  **Solution:** Phase 2 is observation only. Solutions form only after Phase 3 orientation is complete.

- **Problem:** Deep dependency chains cause the read list to balloon beyond what's necessary.
  **Solution:** Only follow imports that are directly relevant to the task. If a dependency chain goes deeper than expected, note it in the orientation statement and ask the user whether to continue reading.

- **Problem:** Higher token usage from reading multiple files upfront slows initial response.
  **Solution:** This is expected and acceptable. The cost of reading upfront is always lower than the cost of implementing the wrong thing and redoing it.

---

## Verification

To verify the protocol was followed correctly, check each item:

1. **Context Audit was output** — The AI produced a structured audit listing relevant files, files read, and blind spots before any proposal
2. **All blind spot files were actually read** — The AI did not summarize from filenames or skip any file
3. **Orientation statement was output** — The AI produced a structured orientation with architecture summary, touched components, observed patterns, and remaining unknowns
4. **Confidence gate was passed** — Either "Remaining unknowns" was empty, or every unknown was resolved via user confirmation or additional reads
5. **Self-ask questions all answered "Yes"** — All four self-ask questions were satisfied before any code was written

**Check command (PowerShell, for reviewing agent transcript):**

```powershell
# Verify all four phase markers appear in the agent's output
Select-String -Path .\agent-transcript.log -Pattern "CONTEXT AUDIT","CONTEXT LOADED","Remaining unknowns","blind spots"
```

**Expected output:** At minimum, one match for "CONTEXT AUDIT" and one match for "CONTEXT LOADED". If "Remaining unknowns" shows content other than "None, ready to proceed", verify that a follow-up resolution occurred.

---

## What This Skill Prevents

- AI proposing integration with a module structured completely differently than assumed
- AI using naming conventions inconsistent with the rest of the codebase
- AI calling functions that don't exist because it assumed they would be there
- AI making architectural decisions that conflict with patterns already established in the code
- AI confidently implementing the wrong thing and needing a full redo

---

## Limitations

- This skill requires more token usage due to reading multiple files upfront
- It may slow down the initial response time before the AI starts coding
- The AI might end up reading more files than strictly necessary if the dependency chain is deep
- Does not replace the need for the user to verify the final code

---

## Related Skills

- `@brainstorming` — Use before execution to figure out what needs to be built
- `@not-a-vibe-coder` — Use for entirely new projects, whereas this skill is for existing ones
