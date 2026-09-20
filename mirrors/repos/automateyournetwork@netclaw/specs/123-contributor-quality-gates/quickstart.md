# Quickstart: Contributor Quality Gates

All commands may be run from any directory when the script is referenced by absolute or repository-relative path.

## 1. Inspect the Contract Inventory

```bash
python3 scripts/run-contract-tests.py --list
python3 scripts/run-contract-tests.py --matrix
```

Both commands are offline and read-only. The matrix must contain 14 suites.

## 2. Preflight Without Downloads

```bash
python3 scripts/run-contract-tests.py --suite document --json
```

If its environment is absent, the result is `BLOCKED_DEPENDENCY`, not a failed document contract.

## 3. Prepare One Isolated Environment

```bash
python3 scripts/run-contract-tests.py --suite document --prepare
```

Preparation downloads Python packages from the configured package registry and writes only the suite's ignored virtual environment. It never installs into the shared interpreter.

## 4. Run One or All Offline Suites

```bash
python3 scripts/run-contract-tests.py --suite document
python3 scripts/run-contract-tests.py --suite all --prepare
```

The all-suite command can download substantial dependencies. The Kubernetes suite may also fetch its pinned binary. Docker-backed suites report Docker/service posture separately.

## 5. Verify Documentation Claims

```bash
python3 scripts/reconcile-mcp.py --surface docs
```

This protects headline counts, the README project-tree count, and the stated role of `config/openclaw.json`.

## 6. Run Runner Contract Tests

```bash
python3 tests/runner/test_run_contract_tests.py
```

These tests use temporary fake suites and make no package download or live request.

## Live Evidence

Live tests remain opt-in. The runner reports the missing variable names and Docker/service requirements but never prints values. Do not add production credentials to pull-request CI.

