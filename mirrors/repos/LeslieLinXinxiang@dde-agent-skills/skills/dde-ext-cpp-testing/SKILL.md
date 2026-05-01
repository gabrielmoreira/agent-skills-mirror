---
name: dde-ext-cpp-testing
description: "DDE subordinate extension. C++ test design/execution workflow (CMake/CTest/gtest) with strict DDE write gating."
---

# DDE Extension: C++ Testing

Skill Version: v0.1

## Authority Chain
- Commander: `dde-bootstrap`
- Write gate: `dde-code-guard`
- This skill cannot directly bypass `[APPROVED]` for code writes.

## When to Use
- Add/fix C++ tests
- Investigate C++ test failures/flakiness
- Improve C++ regression coverage

## Execution Scope
Allowed:
- Analyze C++ test gaps
- Propose/prepare test cases and CTest targets
- Run CMake/CTest/gtest commands
- Produce failure diagnosis

Write-sensitive actions:
- Creating/modifying `*.cpp`, `*.h`, `CMakeLists.txt`, test files
- Must go through handoff + `dde-code-guard`

## Mandatory Flow
1. Identify target component and expected behavior.
2. Map existing tests and missing cases.
3. Run focused tests first, then suite.
4. If changes required, emit handoff:

`DDE_EXTENSION_HANDOFF_REQUIRED`

Fields:
- Reason
- Files to modify
- Proposed test cases
- Minimal impact statement

5. Wait for `[APPROVED]` via `dde-code-guard` before write.

## Output Contract
- Test gap summary
- Command results summary
- Proposed test patch plan
- Handoff block when write is needed
