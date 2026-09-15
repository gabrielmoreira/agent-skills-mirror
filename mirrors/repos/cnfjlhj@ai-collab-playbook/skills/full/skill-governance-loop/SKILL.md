---
name: skill-governance-loop
description: Use when the user asks to review a skill, analyze skill quality, update or align a skill version, compare local state against a newer variant, or run a repeatable keep/enable/hide/disable/archive decision loop from real failures instead of abstract best practices.
---

# Skill Governance Loop

## Overview

Use this skill for evidence-based governance of one skill or a small target set. It starts from a concrete problem, audits the skill, and ends with an explicit keep, enable, hide, disable, merge, split, or archive decision.

## Rules

- Start from a concrete case such as poor triggering, overlap, bloat, or a version update request.
- Produce three outputs every time: the case, the audit, and the decision.
- Separate static quality from observed usefulness; a pretty skill is not automatically a useful skill.
- Use inventory tooling first when the scope is broad enough to need filesystem evidence.
- For update or alignment requests, separate three questions explicitly: what changed upstream, whether the local copy should adopt it, and whether the resulting skill should be enabled, hidden, or left installed-but-off.
- Record the next hypothesis so the next governance pass has a sharper starting point.

## When to Use

Use when:

- the user asks to review a skill, analyze skill quality, or update a skill version
- a skill may need to be kept, disabled, merged, split, archived, or moved
- the user wants a repeatable governance loop instead of one-off edits
- the task is one skill or a small target set that needs version alignment, visibility changes, or an explicit keep vs enable vs hide decision

Do not use when:

- the task is broad inventory scanning of many skills at once
- the work is simple skill authoring with no governance decision
- the request is only to discover whether a skill exists
