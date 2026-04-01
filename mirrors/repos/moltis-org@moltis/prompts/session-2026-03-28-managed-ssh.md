# Managed SSH keys and onboarding

Implemented managed outbound SSH in Moltis.

## What landed
- Credential store support for managed SSH keys and named SSH targets.
- Vault-aware encryption for SSH private keys, plus migration of pre-vault plaintext keys on unseal.
- Remote exec integration so `tools.exec.host = "ssh"` can use the default managed SSH target when no per-session override exists.
- HTTP API for SSH key generation/import, target create/delete/default/test.
- Settings UI for deploy key generation/import, public key copy, named targets, default target selection, and connectivity tests.
- Docs updates across README, configuration, nodes, and vault pages.

## Validation
- `just format`
- `cargo check -p moltis-auth -p moltis-gateway -p moltis-httpd -p moltis-web -p moltis-tools -p moltis-vault`
- `cargo test -p moltis-auth test_credential_store_ssh_keys_and_targets -- --nocapture`
- `cargo test -p moltis-auth test_first_ssh_target_becomes_default_and_delete_promotes_replacement -- --nocapture`
- `cargo test -p moltis-auth test_reset_all_removes_managed_ssh_material -- --nocapture`
- `cargo test -p moltis-vault migration -- --nocapture`
- `cargo test -p moltis-httpd generated_key_material_round_trips -- --nocapture`
- `cargo test -p moltis-httpd imported_key_is_validated -- --nocapture`
- `cargo test -p moltis-gateway node_exec -- --nocapture`
- `cd crates/web/ui && npx playwright test e2e/specs/ssh-settings.spec.js e2e/specs/settings-nav.spec.js`
- `biome check --write crates/web/src/assets/js/page-settings.js crates/web/ui/e2e/specs/settings-nav.spec.js crates/web/ui/e2e/specs/ssh-settings.spec.js`

## Notes
- `just lint` was attempted after the targeted checks.
- Managed SSH keys currently require unencrypted imported private keys.
- System OpenSSH mode remains available next to managed-key mode.
