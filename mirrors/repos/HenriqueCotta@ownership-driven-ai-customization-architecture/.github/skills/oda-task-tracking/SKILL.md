---
name: oda-task-tracking
description: Operate ODA GitHub Issues and the ODA Board consistently. Use when creating, updating, listing, moving, or reclassifying tracked work in GitHub for this repository.
---

# ODA Task Tracking

Use this skill for operational work with repository issues and the ODA Board.

This is a workflow for task tracking, not a path-specific coding rule.

## Scope

Repository: `HenriqueCotta/ownership-driven-ai-customization-architecture`

Project: `ODA Board`

Project owner: `HenriqueCotta`

Project number: `4`

## Task Contract

A tracked task is a repository issue that may also be represented by the same issue as a project item.

The project `Status` field is the board status. Use only `Todo`, `In Progress`, or `Done`.

Use existing repository labels when they fit. Do not invent a label taxonomy or create new labels unless the user explicitly asks.

There is no board `Area` field. Do not simulate one in issue text unless the user asks for a planning convention change.

Interpret board authority according to `ownership/repository/oda-board.instructions.md`.

## Workflow

Search for existing issues before creating a new tracked task.

When creating or rewriting an issue, keep the body concise and actionable with outcome, context, acceptance criteria, and verification.

After a create or update operation, keep the issue body, labels, project status, and linked updates coherent.

When moving a task, update the project status to the requested valid value or the closest valid value. Ask one focused question only when ambiguity would change the result.

When listing work or answering what is next, prefer open `Todo` items and explain the priority briefly from board state and repository context.

## Access Failure

If GitHub issue access is unavailable, do not create or update task state.

If project access is unavailable but issue access works, update only the issue when that still satisfies the request and clearly report that board synchronization is blocked.

If the board state could change the answer, treat that part as verification-blocked instead of guessing.

## Guardrails

Never delete issues or project items.

Do not close or mark work `Done` unless the user asks for that change or the repository evidence clearly supports it.

If this tracking workflow changes materially, update `ownership/repository/oda-board.instructions.md` and the `oda-board` supporting-source entry when they carry the same policy.
