---
name: hermes-attestation-guardian
version: 0.0.1
description: Hermes-only runtime security attestation and drift detection skill for operator-managed Hermes infrastructure.
homepage: https://clawsec.prompt.security
clawdis:
  emoji: "🛡️"
  requires:
    bins: [node]
---

# Hermes Attestation Guardian

IMPORTANT SCOPE:
- This skill targets Hermes infrastructure only (CLI/Gateway/profile-managed deployments).
- This skill is not an OpenClaw runtime hook package.

## Goal

Generate deterministic Hermes posture attestations, verify them with fail-closed integrity checks, and compare baseline drift using stable severity mapping.

## Commands

```bash
# Generate attestation (default output: ~/.hermes/security/attestations/current.json)
node scripts/generate_attestation.mjs

# Generate with explicit policy + deterministic timestamp
node scripts/generate_attestation.mjs \
  --policy ~/.hermes/security/attestation-policy.json \
  --generated-at 2026-04-15T18:00:00.000Z \
  --write-sha256

# Verify schema + canonical digest
node scripts/verify_attestation.mjs --input ~/.hermes/security/attestations/current.json

# Verify with baseline diff (baseline must be authenticated)
node scripts/verify_attestation.mjs \
  --input ~/.hermes/security/attestations/current.json \
  --baseline ~/.hermes/security/attestations/baseline.json \
  --baseline-expected-sha256 <trusted-baseline-sha256> \
  --fail-on-severity high

# Optional detached signature verification
node scripts/verify_attestation.mjs \
  --input ~/.hermes/security/attestations/current.json \
  --signature ~/.hermes/security/attestations/current.json.sig \
  --public-key ~/.hermes/security/keys/attestation-public.pem

# Preview scheduler config without mutating user schedule state
node scripts/setup_attestation_cron.mjs --every 6h --print-only

# Apply managed scheduler block
node scripts/setup_attestation_cron.mjs --every 6h --apply
```

## Attestation payload (implemented)

The generator emits:
- schema_version, platform, generated_at
- generator metadata (skill + node version)
- host metadata (hostname/platform/arch)
- posture.runtime (gateway enabled flags + risky toggles)
- posture.feed_verification status (verified|unverified|unknown)
- posture.integrity watched_files and trust_anchors (existence + sha256)
- digests.canonical_sha256 over a stable canonical JSON representation

## Fail-closed behavior

Verifier exits non-zero when:
- schema validation fails
- canonical digest algorithm is unsupported or digest binding mismatches
- expected file sha256 mismatches (if configured)
- detached signature verification fails (if configured)
- baseline is provided without authenticated trust binding (`--baseline-expected-sha256` and/or baseline signature + public key)
- baseline authenticity or baseline schema/digest validation fails
- baseline diff highest severity is at/above `--fail-on-severity` (default: critical)

Severity messages are emitted as INFO / WARNING / CRITICAL style lines.

## Side effects

- `generate_attestation.mjs` writes one JSON file (and optional `.sha256`) under `$HERMES_HOME/security/attestations`.
- `verify_attestation.mjs` is read-only.
- `setup_attestation_cron.mjs` is read-only unless `--apply` is provided.
- `setup_attestation_cron.mjs --apply` rewrites only the current user managed schedule block delimited by:
  - `# >>> hermes-attestation-guardian >>>`
  - `# <<< hermes-attestation-guardian <<<`

## Notes

- Default output root is `~/.hermes/security/attestations/`.
- No destructive remediation actions (delete/restore/quarantine) are implemented.
- Operator policy file is optional JSON with:
  - `watch_files`: list of file paths
  - `trust_anchor_files`: list of file paths
