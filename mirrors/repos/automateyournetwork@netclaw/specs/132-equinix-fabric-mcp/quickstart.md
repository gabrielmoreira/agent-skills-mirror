# Quickstart

See ../../docs/EQUINIX.md for operator setup and the gated execution sequence.

Offline verification from repository root:

```bash
python3 -m pytest tests/unit/test_equinix.py -q
python3 scripts/reconcile-mcp.py --surface catalog
python3 scripts/reconcile-mcp.py --surface docs
python3 scripts/reconcile-mcp.py --surface portability
python3 scripts/check-server-startup.py --only equinix-mcp
python3 scripts/verify-spec-artifacts.py
npm --prefix ui/netclaw-visual run build
```

Keep live acceptance separate. Do not create a paid resource merely for a smoke test.
