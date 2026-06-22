---
description: Run a full security audit of current changes or a specified area
agent: security-reviewer
---

Audit ${input:scope:the current uncommitted changes} for security issues following the OWASP-style checklist: injection, broken auth/authorization, secret leakage, SSRF, XSS, insecure dependencies. Run `pnpm audit` as part of the review. Output findings grouped by Critical/High/Medium/Low/Informational with concrete fixes.
