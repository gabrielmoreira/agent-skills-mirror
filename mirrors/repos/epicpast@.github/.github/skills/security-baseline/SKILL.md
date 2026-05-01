---
name: security-baseline
description: Audit and implement security best practices for GitHub repositories. USE THIS SKILL when user says "security audit", "check security", "add gitleaks", "secret scanning", "dependency audit", or needs security hardening.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Security Baseline Skill

Implement and audit security controls for GitHub repositories.

## Trigger Phrases

- "audit repository security"
- "add secret scanning"
- "check for vulnerabilities"
- "security hardening"
- "add pre-commit hooks"
- "configure dependabot"

## Security Audit Checklist

### GitHub Actions Security
- [ ] All actions SHA-pinned
- [ ] Minimal `permissions:` declared
- [ ] No secrets in logs
- [ ] OIDC instead of static credentials
- [ ] Untrusted input sanitized

### Repository Security
- [ ] Branch protection enabled
- [ ] Required reviews
- [ ] Status checks required
- [ ] Force pushes blocked
- [ ] CODEOWNERS defined

### Secret Management
- [ ] No hardcoded secrets
- [ ] .env files ignored
- [ ] Gitleaks configured
- [ ] GitHub secret scanning enabled
- [ ] Pre-commit hooks installed

### Dependency Security
- [ ] Dependabot enabled
- [ ] Lock files committed
- [ ] No critical CVEs
- [ ] Regular audits scheduled

## SHA Pinning Validation

```bash
# Check for unpinned actions
grep -rn "uses:.*@v[0-9]" .github/workflows/
grep -rn "uses:.*@main" .github/workflows/
```

## Safe Permission Patterns

```yaml
# Minimal (default)
permissions:
  contents: read

# For PR comments
permissions:
  contents: read
  pull-requests: write

# For releases
permissions:
  contents: write
  packages: write
```

## OIDC Authentication

```yaml
# AWS
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@...
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
```

## Secret Scanning Setup

### Gitleaks Configuration

```toml
# gitleaks.toml
[allowlist]
paths = [
  '''\.example$''',
  '''test/fixtures''',
]
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

## Dependency Audit Commands

```bash
# Python
uv pip audit

# Node.js
pnpm audit

# Go
go list -json -m all | nancy sleuth

# Rust
cargo deny check advisories
```

## Required Security Files

| File | Purpose |
|------|---------|
| `SECURITY.md` | Vulnerability reporting |
| `dependabot.yml` | Automated updates |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `gitleaks.toml` | Secret patterns |
| `CODEOWNERS` | Review requirements |

## Vulnerability Response

| Severity | Response Time |
|----------|---------------|
| Critical | Immediate |
| High | 24 hours |
| Medium | 1 week |
| Low | Next release |

## Quick Security Commands

```bash
# Run gitleaks
gitleaks detect --source . --verbose

# Check git history
gitleaks detect --source . --log-opts="--all"

# Find workflows without permissions
for f in .github/workflows/*.yml; do
  grep -q "^permissions:" "$f" || echo "Missing: $f"
done
```
