# Audit verification quickstart

From the repository root on branch 124-flagship-audit:

```bash
python3 scripts/verify-spec-artifacts.py
python3 scripts/reconcile-mcp.py --surface catalog --surface dependencies --surface docs --surface meraki-ids --surface packages --surface portability
python3 scripts/run-contract-tests.py --list
python3 scripts/run-contract-tests.py --suite runner
python3 scripts/run-contract-tests.py --suite contract --prepare
```

Inspect each selected harness before running it. The runner strips declared live credentials but is itself in audit scope; do not assume every legacy harness is offline. Prepare and execute other reviewed suites separately. Use the HUD package's Node tests and build after installing its isolated dependencies. Flutter/simulator checks require the mobile toolchain.

For each change, record a failing reproduction, apply the task-linked fix, rerun targeted checks, then the affected suite. For each breaking change, execute preview, normal migration, repeat invocation, interrupted/failing input, and recovery against preserved fixtures.

Do not run the full installer against the active home to obtain a baseline. Use isolated temporary homes/worktrees and explicit service targets. Ask John for a named lab only with a concrete test procedure.
