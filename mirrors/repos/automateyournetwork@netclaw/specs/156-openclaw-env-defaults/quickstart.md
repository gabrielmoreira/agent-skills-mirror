# Isolated Verification

Run from repository root:

```sh
python3 -m unittest discover -s tests -p test_setup_registration.py
python3 -m pytest tests/unit/test_mcp_env_defaults.py tests/unit/test_installer_mcp_config.py tests/unit/test_hermes_private_config.py
python3 scripts/check-mcp-portability.py
python3 scripts/verify-catalog-coverage.py
```

Use temporary homes and synthetic values only. The native resolver qualification reads a pinned local module without starting OpenClaw. Existing runtime configuration is never a test target. Re-run supported registration after adding an override whose default was previously materialized; inspect generated private config and readiness before any separately authorized restart.
