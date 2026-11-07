# Secure Development Practices

QuantDinger applies secure-design principles to changes that affect identity,
credentials, tenant data, strategy execution, provider access, and trading.

## Required practices

- Deny access by default and verify authorization against authoritative server
  state instead of trusting claims supplied by a client.
- Validate untrusted input at the boundary and reject unsupported values.
- Keep secrets outside source code and prevent them from entering logs or test
  fixtures.
- Use established open-source cryptographic libraries and protocols; do not
  design custom cryptography.
- Store passwords as salted, adaptive hashes. The standard deployment uses
  bcrypt and never stores plaintext passwords.
- Use cryptographically secure randomness for secrets, tokens, and nonces.
- Use HTTPS/TLS for public deployments and verify remote TLS certificates by
  default.
- Apply least privilege to GitHub Actions, runtime services, provider keys, and
  human access.
- Add regression tests for confirmed security defects and major new behavior.

## Verification

Pull requests run tests, Ruff, CodeQL, Bandit, pip-audit, Gitleaks, dependency
lock checks, OpenAPI checks, and Docker Compose validation as applicable.
High-confidence exploitable findings are fixed before release or documented as
a time-bounded risk exception.

