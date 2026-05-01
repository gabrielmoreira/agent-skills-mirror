# Security Patterns

## OWASP Top 10 Quick-Reference

| # | Category | What to Check |
|---|----------|--------------|
| A01 | Broken Access Control | Verify authorization on every endpoint; deny by default |
| A02 | Cryptographic Failures | No plaintext secrets; use strong hashing (bcrypt/argon2) |
| A03 | Injection | Parameterized queries; no string concatenation for SQL/commands |
| A04 | Insecure Design | Threat model for new features; validate business logic |
| A05 | Security Misconfiguration | No default credentials; disable debug in production |
| A06 | Vulnerable Components | Pin dependency versions; audit with `npm audit` / `pip audit` |
| A07 | Auth Failures | Rate-limit login; enforce strong passwords; secure session management |
| A08 | Data Integrity Failures | Verify signatures on updates; validate serialized data |
| A09 | Logging Failures | Log security events; never log secrets or PII |
| A10 | SSRF | Validate/allowlist outbound URLs; block internal network access |

## Input Validation Checklist
1. Validate type (string, number, boolean — reject unexpected types).
2. Validate length/range (max string length, min/max numeric values).
3. Validate format (regex for emails, UUIDs; reject malformed input).
4. Sanitize for output context (HTML-encode for DOM, parameterize for SQL).
5. Reject unexpected fields (use allowlists, not denylists).
6. Validate at the boundary (API handler, form processor, file parser).

## Auth/Authz Boundary Checklist
1. Authenticate before authorize — verify identity first.
2. Check authorization on every request (not just initial page load).
3. Use role-based or attribute-based access control (RBAC/ABAC).
4. Deny by default — require explicit grants.
5. Validate resource ownership — user can only access their own data.
6. Log access decisions — audit trail for sensitive operations.

## Secrets Management
- **Never** hardcode secrets in source code.
- Use environment variables or secret managers (Vault, AWS Secrets Manager).
- Rotate secrets on a schedule and after any suspected breach.
- Use `.gitignore` and pre-commit hooks to prevent accidental commits.
