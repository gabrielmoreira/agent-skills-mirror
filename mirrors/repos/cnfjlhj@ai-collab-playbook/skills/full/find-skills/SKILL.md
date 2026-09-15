---
name: find-skills
description: "Use when the user asks whether a skill exists, wants help finding or installing one, or asks how to extend agent capabilities with a reusable skill. Start with `npx skills find`; if that fails, use a GitHub-aware fallback before concluding no good match exists."
---

# Find Skills

## Overview

This skill discovers reusable skills before you reinvent one locally. The preferred route is fast registry search first, then a GitHub-aware fallback only if the registry does not surface a good candidate.

## Rules

- Start with `npx skills find <query>` and use a concrete query, not an empty interactive search.
- Disable telemetry when using the CLI in an agent context.
- If the registry misses, do a GitHub-aware fallback before saying no skill exists.
- Prefer installable candidates with a clear skill directory and recent maintenance.
- If a good match exists, report the exact install command.
- If no good match exists, say so plainly and continue with direct help instead of stalling.

## When to Use

Use when:

- the user asks for a skill for a task or domain
- the user asks how to extend the agent with a reusable capability
- the user wonders whether a specialized workflow already exists
- the user wants you to search the skills ecosystem before building something new

Do not use when:

- the user already named the exact local skill to use
- the task is a one-off action better handled directly
- the request is to create or edit a local skill rather than discover one
- the user explicitly does not want external skill discovery

## Search Flow

1. Form a specific query from the task and run `DISABLE_TELEMETRY=1 npx -y skills find <query>`.
2. If the registry finds a strong candidate, present the skill name, what it does, and the install command.
3. If the registry misses, do a GitHub-aware fallback such as a GitHub search or skills repo listing.
4. If a promising repo appears, list or install the specific skill with `npx -y skills add`.

## Output Contract

Always report:

- the query you searched
- whether the registry found a good candidate
- whether a GitHub fallback was actually used
- the best candidate or repo, if any
- the exact install command when installation is possible
