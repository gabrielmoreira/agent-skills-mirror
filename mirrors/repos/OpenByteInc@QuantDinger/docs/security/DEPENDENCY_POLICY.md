# Dependency Management Policy

QuantDinger selects dependencies using standard ecosystem tooling and minimizes
the number of components required in production.

## Selection

Dependencies must have a clear project use case, a compatible open-source
license, an active maintenance history, and no known unmitigated vulnerability
that would make the proposed use unsafe. Standard Python, Docker, GitHub
Actions, and operating-system package tooling is preferred over custom download
or vendoring mechanisms.

## Recording and locking

- Backend runtime dependencies are declared in
  `backend_api_python/requirements.txt` and locked in
  `backend_api_python/requirements.lock`.
- Development and test dependencies are declared in
  `backend_api_python/requirements-dev.txt`.
- MCP package dependencies are declared in `mcp_server/pyproject.toml`.
- Container base images and GitHub Actions are pinned to immutable digests or
  commit SHAs where supported.

Changes to production dependencies are reviewed like source changes and must
include the reason for the addition or upgrade.

## Monitoring

Dependabot checks Python, Docker, and GitHub Actions dependencies weekly.
Security CI runs `pip-audit` against the backend lock file, CodeQL and Bandit
against source code, and Gitleaks against repository history. Confirmed
exploitable vulnerabilities are handled under [SECURITY.md](../../SECURITY.md).

## Release treatment

Known exploitable dependency vulnerabilities of medium or higher severity must
be resolved before a normal release. An exception requires a documented risk
assessment, a compensating control, and a time-bounded remediation owner.

