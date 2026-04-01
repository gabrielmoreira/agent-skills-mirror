# Remote exec doctor and status UX

Expanded the Nodes page into a proper remote-exec status surface.

## What landed
- Added `/api/ssh/doctor` for backend-aware remote exec checks.
- Added `/api/ssh/doctor/test-active` to probe the active SSH route from the Nodes page.
- Added a `Remote Exec Status` card in the Nodes page showing backend mode, paired-node inventory, SSH inventory, doctor checks, and active-route testing.
- Documented the Nodes page doctor behavior in `docs/src/nodes.md`.

## Validation
- `just format`
- `cargo test -p moltis-httpd ssh_routes -- --nocapture`
- `cargo check -p moltis-httpd -p moltis-web -p moltis-gateway`
- `cd crates/web/ui && npx playwright test e2e/specs/settings-nav.spec.js`

## Follow-up
- CLI parity is tracked in `moltis-6b7`.
