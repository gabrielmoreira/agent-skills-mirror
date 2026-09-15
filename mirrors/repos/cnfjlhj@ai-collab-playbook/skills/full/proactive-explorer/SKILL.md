---
name: proactive-explorer
description: Use when missing context may be recoverable from local code, files, logs, or environment evidence before asking the user or making assumptions.
---

# Proactive Explorer

## Overview

Use this skill to reduce avoidable user questions.

Core principle: search local context before asking the user to restate information the system can gather on its own.

## Rules

- Start with local exploration when the request is ambiguous but likely answerable from the workspace.
- Prefer fast local tools first: `rg`, targeted file reads, and focused shell commands.
- Ask the user only for true product decisions, missing credentials, private preferences, or unresolved contradictions.
- Stop exploring once you have enough evidence to act. Do not turn simple tasks into a ceremony.
- Before asking a question, summarize what you already checked and what gap remains.

## When to Use

Use when any of the following are true:

- a missing implementation detail may be recoverable from code, config, docs, tests, or logs
- you can likely resolve an ambiguous file, function, dependency, or workflow reference locally
- a bug report or execution choice should be narrowed with workspace evidence before you ask
- the user message is compressed, but the missing structure is probably already in local context

Do not use when:

- the answer depends on a decision only the user can make
- the missing fact is external, time-sensitive, or account-specific
- the task is already explicit enough to act without more search

## Exploration Order

1. Read local rules and nearby docs such as `AGENTS.md`, project docs, and relevant config.
2. Search filenames, code, tests, and logs with `rg` and targeted reads.
3. Inspect runtime state with shell commands when needed.
4. Use web search only when the missing fact is outside the workspace.
5. Ask the user only for the remaining gap.

## Output Pattern

Before asking a clarifying question, be able to state:

- what you searched
- what you found
- what remains unknown
- why that unknown blocks the next step

## Common Mistakes

- asking for information that local search would reveal in seconds
- exploring indefinitely after the uncertainty is already low
- using web search before exhausting local evidence
- asking broad questions instead of one concrete unresolved decision

## Quick Reference

- Need implementation context: search code and tests first.
- Need runtime state: inspect logs, processes, ports, and environment.
- Need design intent: read local rules, docs, and nearby examples.
- Need outside facts: search the web after local evidence is exhausted.
