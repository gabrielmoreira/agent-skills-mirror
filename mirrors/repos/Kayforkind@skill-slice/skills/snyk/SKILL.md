---
name: snyk
description: "Runs Snyk CLI audits with snyk test (SCA), snyk code test (SAST), snyk container test, snyk iac test, and optional snyk monitor or GitHub Actions gates. Use for lockfile CVEs, image OS packages, or Terraform/Kubernetes misconfig. Never write Semgrep YAML here; not a pre-commit formatter or generic Node project-setup chair."
version: 1.0.1
---

# Snyk Security Audit Toolkit

Use this skill to run Snyk CLI scans across dependencies (SCA), source code (SAST), container images, and Infrastructure-as-Code (IaC). Covers installation, authentication, core commands, CI/CD integration, and failure handling.

## When to Use

- Auditing package dependencies for known vulnerabilities (SCA).
- Running static code security checks on custom source (SAST).
- Inspecting Docker container layers and OS packages.
- Correcting IaC security misconfigurations (Terraform, Kubernetes, CloudFormation).
- Setting up Snyk in GitHub Actions CI/CD pipelines.

**Route elsewhere:**
- `/setup-pre-commit` for formatting hooks.
- `/nodejs-best-practices` for general Node.js project configuration.

## Prerequisites

- Node.js 22/24 installed and available on PATH.
- A Snyk account or service account token.
- For dependency scans: a populated `node_modules` directory (run `npm install` / `pnpm install` first).
- For container scans: Docker runtime available and the target image pulled or built locally.
- Windows host is primary (PowerShell). Use PowerShell-compatible syntax for env vars and path separators.

## Procedure

### 1. Install the Snyk CLI

```powershell
# Install globally via NPM
npm install -g snyk

# Alternative (macOS/Linux): Homebrew
brew install snyk-cli
```

### 2. Authenticate

**Interactive (local dev):**

```powershell
snyk auth
```

This opens a browser login flow.

**Non-interactive (CI/CD or automated systems):**

Set the `SNYK_TOKEN` environment variable to a service account API token.

```powershell
# PowerShell
$env:SNYK_TOKEN = "YOUR_KEY"

# CI/CD (GitHub Actions): inject via repository secrets
# env:
#   SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

> **HARD RULE:** Never commit `SNYK_TOKEN` directly into shell scripts or repository YAML files. Always inject via CI environment secrets.

### 3. Scan Application Dependencies (SCA)

```powershell
# Basic project scan
snyk test

# Monorepo with multiple manifest files
snyk test --all-projects

# Fail only on high or critical severity
snyk test --severity-threshold=high

# Reachability analysis (verify if vulnerable deps are actually imported)
snyk test --reachability=true

# Continuous monitoring: upload package mappings to Snyk dashboard
snyk monitor
```

### 4. Scan Custom Source Code (SAST)

```powershell
snyk code test
```

### 5. Scan Container Images

```powershell
# Remote public image
snyk container test node:22-alpine

# Local image with Dockerfile for root-layer tracing
snyk container test custom-app:latest --file=Dockerfile
```

> **HARD RULE:** Run container scans using the active deployment Dockerfile to ensure layer trace visibility.

### 6. Scan Infrastructure-as-Code (IaC)

```powershell
snyk iac test ./infrastructure/terraform/
```

### 7. GitHub Actions CI/CD Integration

```yaml
# .github/workflows/snyk-security.yml
name: Snyk Security Verification
on:
  pull_request:
    branches: [main, release]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Configure Node.js Environment
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'

      - name: Clean Install Package Dependencies
        run: npm ci

      - name: Run Snyk Dependency Audit
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --exit-code=1
```

### 8. Output Contract (Standard Scan Summary JSON)

```json
{
  "ok": false,
  "vulnerabilities": [
    {
      "id": "SNYK-JS-LIBRARYNAME-123456",
      "title": "Prototype Pollution",
      "severity": "high",
      "packageName": "library-name",
      "version": "1.0.0",
      "fixedIn": ["1.0.4"]
    }
  ]
}
```

## Pitfalls

- **Raw Token Storage:** Committing `SNYK_TOKEN` into shell scripts or repo YAML. Always use CI environment secrets.
- **Scanning Missing Trees:** Running `snyk test` before installing packages (`npm install` / `pnpm install`). Snyk requires a populated dependency tree on disk to map imports accurately.
- **Pipeline Over-testing:** Running full scans on every push across minor dev branches. This exhausts monthly free-tier API quotas. Run scans on PR validation gates instead.
- **Lockfile Integrity:** Modifying `package.json` without regenerating the lockfile breaks dependency integrity tests. Always update lockfiles directly.
- **Severity Noise:** Default scans surface low-severity warnings that can fail pipelines unnecessarily. Use `--severity-threshold=high` (or critical) in build scripts.
- **API Quota Block:** If unauthenticated rate limit blocks execution, verify `SNYK_TOKEN` is set and valid.

## Verification

### Confirm CLI is installed and authenticated

```powershell
snyk --version
```

Expected: a version string (e.g. `1.1290.0` or similar).

### Confirm authentication status

```powershell
snyk auth status
```

Expected: confirmation that the current token is valid and linked to an organization.

### Run a test scan and inspect output

```powershell
snyk test --severity-threshold=high
```

Expected: JSON or human-readable summary with `"ok": true` when no high/critical vulnerabilities are found, or a list of vulnerabilities with `id`, `severity`, `packageName`, `version`, and `fixedIn` fields.

### Verify CI integration

Trigger a pull request against `main` or `release` and confirm the `Snyk Security Verification` workflow runs and either passes or blocks based on `--severity-threshold=high --exit-code=1`.

## Related skills

- `setup-pre-commit` — establish formatting and lint hooks.
- `nodejs-best-practices` — general Node.js project configuration and lockfile management.

## Source Anchors

- Snyk CLI Help Center: https://docs.snyk.io/snyk-cli
- Snyk Vulnerability Database: https://security.snyk.io/

## Changelog

- **2026-05-30**: Modernized skill layout. Documented SAST, container, and IaC check syntax, integrated reachability options, and aligned monorepo command parameters.
- **2026-05-31**: Rewritten to production-grade SKILL.md with numbered procedures, hard rules, and verification steps.
