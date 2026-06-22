---
applyTo: "src/**/*.ts,src/**/*.tsx"
description: "Baseline security and accessibility rules applied to all source code, regardless of which agent is active"
---

# Security & Accessibility Baseline

These are minimums every change must meet, even outside an explicit security/a11y review. For deep audits, use the `security-reviewer` or `accessibility-auditor` agents.

## Security baseline
- Validate all external input with `zod` before use — no exceptions for "internal" or "trusted" routes.
- Never interpolate user input directly into a query string, shell command, or `dangerouslySetInnerHTML`.
- Never log secrets, tokens, passwords, or full payment/PII details.
- Auth/authorization check is the first thing a handler does, not an afterthought.

## Accessibility baseline
- Every interactive element is keyboard-operable and has a visible focus state.
- Every `<img>`/`next/image` has meaningful `alt` (or `alt=""` if purely decorative).
- Every form input has an associated, programmatically-linked `<label>`.
- Color is never the sole indicator of state (errors, selection, status).
