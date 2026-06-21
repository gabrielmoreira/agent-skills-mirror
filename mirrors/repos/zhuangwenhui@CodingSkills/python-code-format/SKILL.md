---
name: python-code-format
description: Use when writing, editing, reviewing, or comparing Python code and task-local style decisions matter, especially for formatting, naming, docstrings, logging, resource handling, or Python 3.12-specific syntax choices.
---

# Python Code Format

## When to Use

Use this skill when the task involves Python code authoring, modification, or review and local style choices need to be made consistently.

Trigger it when the work touches:
- line wrapping, indentation, blank lines, or spacing
- naming
- comments or docstrings
- logging messages or user-facing error messages
- file, socket, or similar resource handling
- Python 3.12-specific style decisions

Do not use it for repository-wide Python version governance, CI, linter or formatter rollout, pre-commit setup, or broad refactors unrelated to the current task.

## Baseline

Within this skill and its related reference documents, Python 3.12 is the language and style baseline.

This baseline applies only to the `python-code-format` skill system and its documents. It does not by itself declare a repository-wide Python upgrade or revise historical version statements elsewhere.

## Workflow

1. Confirm that the task is a Python writing, editing, or review task rather than unrelated repository policy work.
2. Follow direct user instructions and any narrower task-local constraints first.
3. Keep changes minimal and stay close to the surrounding code unless the task explicitly asks for a style correction.
4. Apply the priority order below when multiple acceptable choices exist.
5. Read `references/python-code-format-research.md` whenever a specific rule, ambiguity, or edge case needs to be resolved.
6. Prefer the option that both matches the reference and preserves local consistency with nearby code.

## Priority Order

1. Format and layout
2. Naming
3. Comments and docstrings
4. Logging and runtime messages
5. Python 3.12-specific style details

## Boundaries

This skill does not:
- declare a repository-wide Python 3.12 migration
- revise historical version statements in unrelated documents
- introduce CI, linters, formatters, pre-commit hooks, or other automation
- justify unrelated bulk formatting or broad style-only refactors

## Reference Guide

Use `references/python-code-format-research.md` as the detailed rule source.

Consult the relevant sections there for:
- line length, indentation, blank lines, and spaces
- shebang and string rules
- files, sockets, getters, and setters
- naming
- comments and docstrings
- Python 3.12 additions from PEP 701, PEP 695, and PEP 698
