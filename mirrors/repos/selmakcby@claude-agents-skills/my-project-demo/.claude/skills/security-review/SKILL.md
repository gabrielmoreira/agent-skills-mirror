---
name: security-review
description: AI-powered security vulnerability detection. Use PROACTIVELY after writing code that handles user input, authentication, API endpoints, payments, or sensitive data. Flags OWASP Top 10 issues with diff-aware scanning.
---

<!--
  Source: anthropics/claude-code-security-review (official)
  File:   https://github.com/anthropics/claude-code-security-review/blob/main/.claude/commands/security-review.md
  Used by: reviewer agent
-->

# Security Review

## When to trigger
- After writing code touching auth, payments, API endpoints, file I/O, or user input
- Before commit on security-sensitive changes
- When user asks `/security-review`

## Scanning mode

**Diff-aware:** only analyze changed files in the current PR/commit.
Focus on real vulnerabilities — filter out false positives aggressively.

## What to check (OWASP Top 10 mapping)

### 1. Injection
- SQL injection → parameterized queries?
- NoSQL injection → $where clauses, user-controlled operators?
- Command injection → `exec()` with user input?
- **Prompt injection** (AI-specific) → user input flowing into system prompts?

### 2. Broken authentication
- Missing auth checks on protected routes
- Weak password hashing (bcrypt/argon2 required)
- JWT misuse — missing signature verification, weak secrets, `none` algorithm accepted
- Session fixation, missing session rotation on login

### 3. Sensitive data exposure
- Hardcoded secrets in code
- API keys in client bundles (import in `"use client"` components)
- PII in logs
- Missing HTTPS enforcement
- Secrets in error messages

### 4. XML/XXE
- XML parsers with external entity processing enabled

### 5. Broken access control
- Missing authorization (authenticated but not authorized)
- IDOR (accessing other users' data by changing an ID)
- Privilege escalation paths

### 6. Security misconfiguration
- Default credentials
- Debug endpoints exposed in prod
- Missing security headers (CSP, HSTS, X-Frame-Options)

### 7. XSS
- `dangerouslySetInnerHTML` with user input
- Rendering LLM output without sanitization
- URL parameters reflected without escaping

### 8. Insecure deserialization
- `JSON.parse` with user-controlled content (usually fine in JS, but watch for prototype pollution)

### 9. Using components with known vulnerabilities
- Run `npm audit` mentally — are any flagged deps in critical paths?

### 10. Insufficient logging
- Security events unlogged (failed logins, permission denials)
- Overlogging (logging PII, tokens, passwords)

## AI-specific checks

- **Webhooks:** signature verification present? (Stripe, GitHub, etc.)
- **Rate limiting:** on public endpoints? On AI endpoints especially?
- **Input length:** max length on LLM inputs?
- **Output validation:** Zod schema on LLM responses before rendering?
- **CORS / CSRF:** properly configured for auth endpoints?

## Severity (same as code-review)

- **CRITICAL** — exposed secret, missing auth, unverified webhook, SQL injection, missing rate limit on AI endpoint
- **HIGH** — missing input validation, weak crypto
- **MEDIUM** — logging gaps, overly verbose errors
- **LOW** — defense-in-depth suggestions

## Output format

```markdown
## CRITICAL
- [`<file>:<line>`] <vulnerability> (OWASP: <category>)
  - Impact: <what an attacker could do>
  - Fix: <specific mitigation>

## HIGH / MEDIUM / LOW
- ...

## Verdict
PASS | BLOCK (CRITICAL count: N)
```

## Rules

- **Never hand-wave.** "This might be a risk" is not enough — say if it is or isn't, with evidence.
- **Every finding:** severity, OWASP category, file + line, attacker scenario, specific fix.
- **Rotate suspected exposed secrets immediately** and flag at top of report.
- **False positives are worse than no review** — if you're not sure, don't flag it.
- **AI endpoints get extra scrutiny** — token limits, output sanitization, rate limits.
