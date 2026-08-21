---
name: research-session-management
description: "Runs thesis/long-form research session startup and shutdown: INDEX, chapter HANDOFF, error log, OPS files, and numbered KB notes for cross-chat continuity. Use when the user says new thesis session, session handoff, continue thesis work, pick up where left off, or end session. Not for software-repo planning (side-project-planning), Karpathy wiki ingest (llm-wiki), or general web research. Never start writing before INDEX, the matching chapter HANDOFF, and the error log are read."
version: 1.0.1
domain: Research-Ideation
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

## When to Use

Use this protocol to manage session boundaries and ensure seamless handoffs between sequential AI chat instances for multi-month thesis or long-form research projects. 

**Trigger Keywords:** 'new thesis session', 'session handoff', 'continue thesis work', 'pick up where left off', 'end session'.

**Routing:**
- Route to `side-project-planning` for software repositories.
- Route to `startup-analyst` for venture analysis.

## Prerequisites

- **Primary OS:** Windows host (PowerShell). Ensure file paths use Windows conventions (e.g., `~\agent-skills\...`).
- **Local-First Agents:** 2026 workflows emphasize repository-level configuration files (e.g., `.pointerrules` or `.claudesession`) to bootstrap the agent context.
- **Required Inputs:** Existing `INDEX.md`, the latest `HANDOFF_conv[N-1]_to_conv[N].md`, and `CLAUDE_ERROR_LOG.md` (or `CLAUDE_ERROR_LOG_V2.md`).

## Procedure

### Session Startup (MANDATORY every session)

Execute in order. Do NOT skip steps. Do NOT begin work before completing all of the following steps:

1. **Read the INDEX file** (or `INDEX_LITE` if the full INDEX exceeds context limitations).
2. **Read the HANDOFF file** relevant to the current chapter/section. Do NOT default to the "most recent handoff" if it refers to a different chapter. If the researcher specifies 3.3.2, search for HANDOFF files referencing Chapter 3 or 3.3 before falling back to the most recent overall handoff.
3. **Read all files** listed in that handoff's mandatory reading list.
4. **Read the Error Log** (`CLAUDE_ERROR_LOG.md` or `CLAUDE_ERROR_LOG_V2.md`). This is NON-NEGOTIABLE. If no error log exists in the Knowledge Base (KB), create one immediately before starting work.
5. **Read the OPS file** for the current chapter (e.g., `CH3_WRITING_OPS.md`) if one exists. Chapter-specific error triggers and Writing Mode decisions live there.
6. **Scan auto-memory for standing rules.** The project's `MEMORY.md` index contains persistent feedback files. Before writing, identify any `feedback_*` entries that apply to the current task and load them. Confirm awareness of standing rules (e.g., docx run-level editing, no mid-batch method switches, mandatory visual check for visual output, define "correct" before writing fix code).
7. **Initiate active research or writing** only after completing steps 1 through 6.

### Session Shutdown (MANDATORY every session)

Execute the following steps at the conclusion of every session:

1. **Save all new notes, data, and analyses** as numbered KB files on the filesystem. Do not leave key information only in the conversation history.
2. **Write a HANDOFF file** for the next session following the Handoff Template below.
3. **Update the INDEX** file by adding a conversation log entry and updating file statuses.
4. **Verify that all files saved correctly** by reading back a few lines from each newly written or modified file.

### File Organization

- **Sequential Numbering:** Prefix KB files with `01_`, `02_`, ... `NN_`. Check the INDEX for the next available number.
- **Subdirectories:** Use subdirectories per chapter: `Chapter_X/cited/`, `Chapter_X/nocite/`, `Chapter_X/archive/`.
- **Ownership:** Markdown notes, JSON files, handoffs, and analyses are AI-maintained. Word documents are researcher-controlled; only modify them upon explicit request.
- **Archiving:** Move superseded versions to the `archive/` directory with a version suffix before overwriting.

### INDEX File Template

```markdown
# Project Knowledge Base  INDEX

## 1. File Manifest
| # | File | Description | Status |
|---|------|-------------|--------|
| 01 | [name] | [description] | Complete / In progress / Needs revision |

## 2. Conversation Log
| Date | Session # | Work Done |
|------|-----------|-----------|

## 3. Next Steps
1. [priority item]
```

### Handoff File Template

Handoff file naming convention: `HANDOFF_conv[N]_to_conv[N+1].md`

```markdown
# Handoff: Session N  Session N+1

## What happened
[2-5 sentences summarizing progress]

## Key decisions
- D1: [decision and rationale]

## Files created or modified
- [filename]  [what changed]

## Unresolved items
- U1: [item, why it matters, suggested approach]

## Mandatory reading for next session
1. [file]  [why]

## Critical lessons
- [mistake made this session to avoid next time]
```

## Pitfalls

- **Missing Handoff:** If the previous handoff is missing, scan the Git log or file modification timestamps for files changed in the last 24 hours to reconstruct the session state.
- **File Collision:** If two files share a sequence number, rename the older version to `_v1` and move it to `archive/`.
- **INDEX vs INDEX_LITE:** Use `INDEX_LITE` if the file manifest contains more than 50 files or the INDEX size exceeds 15,000 tokens.
- **Session End Trigger:** End the session immediately if token count exceeds 50% of the model's optimal prompt caching limit, or if the reasoning latency increases significantly.
- **Context Degradation:** End the session and trigger shutdown when the AI shows signs of context degradation (e.g., forgetting instructions or repeating sentences).
- **Handoff Accuracy:** Do NOT write handoffs from memory. Re-read the actual files before summarizing. Verify all claims against raw data or final output, not earlier planning documents.
- **Source Segregation:** Segregate verified primary sources (citations) from speculative drafts to prevent hallucinations from polluting the core research assets.

## Verification

- **Zero file index numbering collisions.** Check the INDEX before creating new files.
- **Every handoff must cite at least one specific verified document.**
- **The handoff must declare exactly one starting hook** for the subsequent session to prevent cold-start latency.
- **File integrity:** Verify that all files saved correctly by reading back a few lines from each newly written or modified file.
