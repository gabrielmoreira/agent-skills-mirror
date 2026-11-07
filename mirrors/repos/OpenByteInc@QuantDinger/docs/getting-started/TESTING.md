# Testing Policy

All major functionality and security-sensitive fixes must add or update an
automated test. A pull request should identify the commands used and explain any
test that could not be run.

## Backend

From `backend_api_python/`:

```bash
python -m pip install --no-deps -r requirements.lock
python -m pip install -r requirements-dev.txt
python -m pytest -m "not integration and not stress" --cov=. --cov-branch
```

Database integration and release-gate tests are run separately in Backend CI.
The workflow shards the main suite and reports statement and branch coverage to
Codecov.

## MCP server

From the repository root:

```bash
python -m pip install -e './mcp_server[dev]'
python -m pytest mcp_server/tests -q
```

## Required CI

The default branch uses GitHub Actions for linting, tests, OpenAPI validation,
dependency auditing, secret scanning, CodeQL, and release checks. Required
checks must pass before a pull request is merged, unless a maintainer records an
explicit emergency bypass and follow-up issue.

