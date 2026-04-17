# Changelog

## [0.0.1] - 2026-04-15

- Implemented deterministic Hermes attestation generator CLI (`scripts/generate_attestation.mjs`).
- Implemented fail-closed verifier CLI with schema, canonical digest, expected checksum, and optional detached signature checks (`scripts/verify_attestation.mjs`).
- Implemented meaningful baseline diff engine with stable severity mapping for risky toggle regressions, feed verification regressions, trust anchor drift, and watched file drift (`lib/diff.mjs`).
- Implemented Hermes-only cron setup helper with print-only default and managed-block apply mode (`scripts/setup_attestation_cron.mjs`).
- Added shared attestation library for canonicalization, schema validation, digest generation, and policy parsing (`lib/attestation.mjs`).
- Expanded tests for schema determinism, diff behavior, generator/verifier fail-closed behavior, and cron helper Hermes-only output.
- Updated metadata/docs to match actual implemented behavior and ClawSec release pipeline expectations.
