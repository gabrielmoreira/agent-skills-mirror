---
name: silent-failure-hunter
description: Audits error handling for silent failures, inadequate user feedback, and unjustified fallback behavior. Finds issues in catch blocks, fallbacks, and error paths. Use after modifying error handling code.
argument-hint: "[file or directory to audit]"
user-invocable: true
---

# Silent Failure Hunter

Audit error handling code for silent failures, inadequate user feedback, and unjustified fallback behavior. Every error that occurs without proper logging and user notification is a critical defect.

## Core Principles (non-negotiable)

1. Silent failures are unacceptable — any error without proper logging and user notification is a critical defect.
2. Users deserve actionable feedback — every error message must tell users what went wrong and what they can do.
3. Fallbacks must be explicit and justified — silently falling back to alternative behavior hides problems.
4. Catch blocks must be specific — broad exception catching hides unrelated errors and makes debugging impossible.
5. Mock/fake implementations belong only in tests — production fallbacks to mocks indicate architectural problems.

## Review Process

### 1. Identify All Error Handling Code

Systematically locate:

- All try/catch blocks
- All error callbacks and error event handlers
- All conditional branches that handle error states
- All fallback logic and default values used on failure
- Optional chaining (`?.`) used in error handlers or callbacks where errors should be explicitly handled (not general null-safe property access)

### 2. Scrutinize Each Error Handler

For every error handling location:

**Logging quality**: Is the error logged with appropriate severity and context? Would this log help debug the issue months from now?

**User feedback**: Does the user receive clear, actionable feedback? Is the error message specific enough to be useful?

**Catch block specificity**: Does the catch block catch only the expected error types? List every unexpected error type that could be accidentally suppressed.

**Fallback behavior**: Is the fallback explicitly justified? Does it mask the underlying problem? Would the user be confused by the fallback rather than seeing an error?

**Error propagation**: Should this error propagate to a higher-level handler? Is it being swallowed when it should bubble up?

### 3. Check for Hidden Failure Patterns

- Empty catch blocks (forbidden)
- Catch blocks that only log and continue without user feedback
- Returning null/undefined/default values on error without logging
- Optional chaining (`?.`) used in contexts where an error should be handled explicitly rather than silently skipped
- Retry logic that exhausts attempts without informing the user

## Output Per Issue

- **Location**: file path and line number
- **Severity**: CRITICAL (silent failure, broad catch) / HIGH (poor error message, unjustified fallback) / MEDIUM (missing context)
- **Issue**: what's wrong and why it's problematic
- **Hidden errors**: specific error types that could be suppressed
- **User impact**: how this affects debugging and user experience
- **Recommendation**: specific code changes with example corrected code
