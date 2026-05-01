# Learned Patterns

This file is auto-populated through the self-correction loop.
When Claude makes a mistake and gets corrected, the lesson goes here.

## Format

### [Date] - Category: [Brief Title]
**Mistake:** What went wrong
**Correction:** What should have happened
**Rule:** The pattern to follow going forward

---

## Examples

### 2025-01-15 - Testing: Always run related tests
**Mistake:** Made changes to utility function without running tests
**Correction:** User pointed out tests were broken
**Rule:** After editing any .ts file, run `npm test -- --related` before marking complete

### 2025-01-20 - Git: Don't commit sensitive files
**Mistake:** Almost committed .env file
**Correction:** User caught in review
**Rule:** Never stage .env, credentials.*, or *.pem files. Check `git status` carefully.

---

## Active Patterns

(Add patterns below as they're learned)
