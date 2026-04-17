# hermes-attestation-guardian

Hermes-only security attestation and drift detection skill.

Status: implemented (v0.0.1), Hermes-only.

## What it does

- Generates deterministic Hermes runtime posture attestations.
- Verifies attestation schema + canonical digest with fail-closed semantics.
- Optionally verifies detached signatures using a provided public key.
- Fails closed on baseline diffing unless baseline authenticity is verified (trusted digest and/or detached signature).
- Restricts attestation output writes to Hermes attestation scope (`$HERMES_HOME/security/attestations`).
- Compares baseline vs current attestations with stable severity classification.
- Provides an optional Hermes-oriented cron setup helper (print-only by default).

## Scope boundaries

In scope:
- Hermes environment posture snapshots
- deterministic baseline diffing
- fail-closed verification semantics
- Hermes optional scheduling helper

Out of scope / unsupported (v0.0.1):
- OpenClaw runtime hooks (unsupported)
- destructive auto-remediation
- automatic rollback of runtime configuration

## Quickstart

```bash
node scripts/generate_attestation.mjs
node scripts/verify_attestation.mjs --input ~/.hermes/security/attestations/current.json
node scripts/setup_attestation_cron.mjs --every 6h --print-only
```

## Tests

```bash
node test/attestation_schema.test.mjs
node test/attestation_diff.test.mjs
node test/attestation_cli.test.mjs
node test/setup_attestation_cron.test.mjs
```
