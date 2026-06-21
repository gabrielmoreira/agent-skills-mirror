---
name: cpp-code-format
description: Use when writing, editing, reviewing, or comparing C++/C code and task-local style decisions matter, especially for formatting, naming, headers and includes, comments, error handling, logging messages, or C++20-specific syntax choices. Primary target is the ShapeReconstruction codebase (mvrmesh).
---

# C++ Code Format

## When to Use

Use this skill when the task involves C++/C code authoring, modification, or review and local style choices need to be made consistently.

Trigger it when the work touches:
- line wrapping, indentation, braces, blank lines, or spacing
- naming
- header files, include order, or header guards
- comments
- error handling, exception messages, or user-facing runtime messages
- logging output
- C++20-specific style decisions

Primary target: the ShapeReconstruction sub-project (`mvrmesh`) of the MedSim2Learn workspace. Other C++ code in the workspace (e.g. DeformSim) may adopt these rules later, but this skill does not govern it yet unless the task explicitly says so.

Do not use it for repository-wide C++ version governance, CI, linter or formatter rollout, pre-commit setup, or broad refactors unrelated to the current task.

## Baseline

Within this skill and its related reference documents, C++20 is the language and style baseline (`CMAKE_CXX_STANDARD 20`, `CMAKE_CXX_STANDARD_REQUIRED ON`, `CMAKE_CXX_EXTENSIONS OFF`, MSVC `/std:c++20`). Code shared with or destined for DeformSim must additionally compile as C++17 (that project's current floor).

This baseline applies only to the `cpp-code-format` skill system and its documents. It does not by itself declare a workspace-wide C++ upgrade or revise historical version statements elsewhere.

C++20 modules and `import std` are out of baseline: not mature on the CMake+MSVC toolchain and no dependency ships module interfaces. Revisit when a stable `/std:c++23` and non-experimental `import std` land.

## Workflow

1. Confirm that the task is a C++/C writing, editing, or review task rather than unrelated repository policy work.
2. Follow direct user instructions and any narrower task-local constraints first.
3. Keep changes minimal and stay close to the surrounding code unless the task explicitly asks for a style correction.
4. Apply the priority order below when multiple acceptable choices exist.
5. Read `references/cpp-code-format-research.md` whenever a specific rule, ambiguity, or edge case needs to be resolved.
6. Prefer the option that both matches the reference and preserves local consistency with nearby code.
7. When editing a region that contains one of the known inconsistencies listed in the reference, normalize it to the canonical form as part of the edit; never launch a bulk reformat for its own sake.

## Priority Order

1. Format and layout
2. Naming
3. Headers and includes
4. Comments
5. Error handling, logging, and runtime messages
6. C++20-specific style details

## Boundaries

This skill does not:
- declare a workspace-wide C++20 migration or change DeformSim's C++17 pin
- revise historical version statements in unrelated documents
- introduce CI, linters, formatters, pre-commit hooks, or other automation (tooling rollout is a separate, explicitly requested task)
- justify unrelated bulk formatting or broad style-only refactors (the workspace forbids unbounded refactors)
- override the workspace communication rules (code comments, identifiers, and commit messages in English; no emoji)

## Reference Guide

Use `references/cpp-code-format-research.md` as the detailed rule source.

Consult the relevant sections there for:
- line length, indentation, blank lines, spaces, and braces
- naming (full identifier-kind table)
- headers, include order, and `#pragma once`
- namespaces and file-local linkage
- comments and TODO format
- error handling, exception types, message wording, and the `[[noreturn]]`/`[[nodiscard]]` attributes
- logging tags and stream routing
- modern C++20 idiom (auto, enum class, const placement)
- known ShapeReconstruction inconsistencies and their canonical forms
- the Intel oneAPI exemplar and the cross-guide disagreement register
