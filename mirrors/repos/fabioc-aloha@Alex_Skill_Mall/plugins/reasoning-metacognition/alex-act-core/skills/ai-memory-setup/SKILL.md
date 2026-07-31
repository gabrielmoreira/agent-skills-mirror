---
name: ai-memory-setup
description: "Resolve and use the Alex_ACT_Memory sibling repository without silently cloning, syncing, or exposing protected data. Use for announcements, feedback, shared knowledge, and explicit memory setup."
lastReviewed: 2026-07-30
---

# AI Memory Setup

Use the local `Alex_ACT_Memory` Git repository as the shared memory bus. The
store has its own contract and release cycle; Core is a consumer and policy
author, not an implicit sync service.

## Resolve the Store

Discovery order (first match wins):

| State | Action |
| --- | --- |
| Environment variable `ALEX_MEMORY_PATH` points to a clone | Use that explicit path |
| Sibling `../Alex_ACT_Memory` exists (relative to the project root) | Use it without pulling |
| `~/Alex_ACT_Memory` exists | Use it without pulling |
| No clone exists | Report Memory unavailable; ask before cloning or scaffolding |
| Clone has no remote | Local-only operation is valid |

Discovery is read-only. Never run `git pull`, `git push`, clone, scaffold, or
change a remote merely because Memory was mentioned.

## Respect Channel Boundaries

| Channel | Use | Write rule |
| --- | --- | --- |
| `announcements/` | Released guidance and compatibility notices | Authorized release/reporting work only |
| `feedback/` | Abstracted friction, bugs, and success signals | Strip project details and PII first |
| `knowledge/` | Shared reusable technical knowledge | Contract-valid, project-independent content |
| `insights/` | Cross-session analytical insights | Evidence-backed and non-sensitive |
| `profile/` | Encrypted user profile envelopes | On-demand only; never inspect raw secrets |

Only these five directories are approved. The validator rejects unknown
top-level paths, so ad-hoc files at the Memory root (for example a shared
`notes.md`) fail contract validation. Cross-session notes belong in the local
project's `HANDOFF.md`, not in the shared bus.

Do not bulk-copy Memory content into VS Code `/memories/`. User memory stores
workflow preferences; the sibling repository stores shared, contract-governed
content.

## Read Safely

1. Resolve the existing clone.
2. Read `CONTRACT.md` before interpreting channel semantics.
3. Read only the channel needed for the current task.
4. Treat encrypted profile content as unavailable unless the user explicitly
   requests profile use and the authorized local secret flow is already set up.
5. Never print credentials, encryption keys, or decrypted profile content that
   the task did not request.

## Write Safely

Before writing:

1. Apply `pii-memory-filter` and `cross-project-isolation`.
2. Use the destination channel's documented schema and naming convention.
3. Write the smallest self-contained artifact.
4. Run the Memory repository's validator from the Memory root:

   ```pwsh
   npm run validate
   ```

5. Show the diff. Commit or sync only when explicitly requested.

Memory writes and Git synchronization are separate decisions. A valid local
write does not authorize a commit, pull, or push.

## Setup with Consent

When the user explicitly asks to configure Memory:

1. Ask whether they want an existing clone, a clone from a named remote, or a
   local-only repository.
2. Never invent the remote URL or audience.
3. Clone or scaffold only after the user confirms the destination and audience.
4. Run `npm run validate` after setup.
5. Do not configure encrypted profile access unless requested separately.

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Pulling on session start | Discovery is read-only; sync requires explicit intent |
| Writing feedback with project names or paths | Generalize before writing |
| Treating missing Memory as an error on every task | Return unavailable and continue |
| Reading all channels to "get context" | Read the minimum channel needed |
| Committing a valid write automatically | Validation and publication are separate gates |

## Would Revise If

Revisit by **2026-10-28** or sooner if the Memory contract changes its channel
model, the sibling / `ALEX_MEMORY_PATH` discovery order stops matching heir
layouts, the validator entry point changes, or this skill causes an unrequested
clone, sync, or protected-profile read.