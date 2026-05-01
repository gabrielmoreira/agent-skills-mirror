---
name: concise-technical-writing
description: Write, edit, and tighten clear concise technical communication. Use when Codex is asked for commit messages, PR descriptions, changelogs, README sections, design notes, implementation summaries, status updates, release notes, bug reports, comments, or to make text shorter, clearer, less verbose, less AI-sounding, or more direct.
license: MIT
---

# Concise Technical Writing

## Core Workflow

1. Identify audience, purpose, required facts, and action needed.
2. Preserve technical accuracy; remove throat-clearing, filler, repetition, and vague praise.
3. Lead with the change, decision, result, or ask.
4. Use concrete nouns and verbs. Avoid inflated phrases.
5. Keep structure proportional to the artifact: one-line commits, short PR summaries, scoped release notes, direct docs.
6. Include risks, verification, and next steps only when useful.

## Style Rules

- Prefer short sentences.
- Use active voice unless the actor is irrelevant.
- Replace abstract phrasing with specific behavior.
- Remove meta-commentary about why something is important.
- Avoid marketing language in engineering artifacts.
- Use bullets for scan-heavy details; use prose for short summaries.

## Output Patterns

- Commit: imperative verb + object + qualifier.
- PR: summary, key changes, verification, risk.
- Changelog: user-visible change first.
- Status: done, blocked, next.
- Bug report: observed, expected, reproduction, impact, environment.

## Deliverable Shape

For writing/editing work, provide:

- Final concise text first
- Optional brief rationale only when useful
- Preserved technical facts
- Removed ambiguity or verbosity called out only if requested

## References

- Read `references/concise-writing-checklist.md` when editing technical text for clarity.
