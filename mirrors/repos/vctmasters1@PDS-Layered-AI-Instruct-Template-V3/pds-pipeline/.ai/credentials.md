# Credentials — warehousing and .gitignore for pds-pipeline

**Scope**: Authoritative for pds-pipeline/ directory
**Last Updated**: 2026-05-27

> This file extends the root .ai/credentials.md with pds-pipeline-specific patterns.

> **Never commit credentials** — use environment variables or local .env files that are gitignored.

---

## Never Commit Credentials

| Item | Action | Notes |
|------|--------|-------|
| API keys, tokens, passwords | Always gitignore | Store in environment variables |
| Database connection strings | Always gitignore | Use .env.example template instead |
| AWS credentials (.aws/credentials) | Always gitignore | IAM roles recommended for Railway |

> **Never Commit Credentials**: the hard rule on secrets.

---

## .gitignore Requirements

Every module .gitignore MUST include these patterns:

```gitignore
# Secrets and credentials
.env
.env.*
*.local.*
```

# Build output
node_modules/
dist/
build/

# IDE and editor files
.vscode/
.idea/

# Personal machine overrides
*.local.*

# Environment templates are OK to commit
.env.example

# Personal overrides pattern

# For any committed config file that needs local customization:

# Create a sibling file named <original>.local.<ext>

# Example:

# settings.json -> settings.local.json

# Add *.local.* to .gitignore
