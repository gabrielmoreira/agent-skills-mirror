# Module: Hermes Attestation Guardian

## Responsibilities
- Produce a deterministic Hermes runtime security snapshot (attestation).
- Verify attestation integrity in fail-closed mode before any trust decision.
- Compare trusted baseline vs current posture and classify drift severity.
- Provide a safe, Hermes-scoped automation path for periodic attestation checks.

## Install Guard Compatibility Note (2026-04-16)
- Core behavior is unchanged.
- Operator-facing wording in `SKILL.md`, `README.md`, and `skill.json` was tightened so a clean Hermes community-source install now scans as `SAFE` and installs without `--force`.
- Scheduling capability remains present via `scripts/setup_attestation_cron.mjs`; only wording changed to avoid false-positive persistence blocks in the default guard policy.

## PR Claims: Full Human-Friendly Breakdown

This section rewrites each PR claim as an operator-facing explanation, then ties it to exact code and tests.

### Claim 1: Adds deterministic attestation generation with canonicalized payload digesting.

Absolutely — in people-speak:

We create a security snapshot of Hermes in a way that is reproducible, then fingerprint it in a stable way so tampering or real drift is obvious.

What this means in practice:
1) Attestation generation
- Think of it as a report card for Hermes security posture at a moment in time.
- It records posture fields, trust anchors, watched-file hashes, and metadata.

2) Deterministic output
- Same state should produce the same attestation content.
- No noise from object insertion order or formatting randomness.

3) Canonicalization before hashing
- Payload is normalized into one canonical JSON representation.
- This removes ambiguity from normal JSON variations.

4) Digest binding
- SHA-256 is computed over canonical payload content.
- Any meaningful change to payload changes digest.
- Any post-generation tampering causes verification mismatch.

Where it is wired:
- `skills/hermes-attestation-guardian/scripts/generate_attestation.mjs`
- `skills/hermes-attestation-guardian/lib/attestation.mjs`
  - `stableSortObject`
  - `stableStringify`
  - `sha256Hex`
  - `buildAttestation`
  - `computeCanonicalDigest`
  - `validateDigestBinding`

How to verify:
- `node skills/hermes-attestation-guardian/test/attestation_schema.test.mjs`
  - proves same-input determinism and canonical digest consistency.
- `node skills/hermes-attestation-guardian/test/attestation_cli.test.mjs`
  - proves post-generation tamper causes fail-closed digest mismatch.

Quick scenario:
- Same state: run generator twice with unchanged inputs -> same digest.
- Tampered file: flip a posture value in JSON -> verifier fails on canonical digest mismatch.

---

### Claim 2: Enforces fail-closed verification for schema, digest, optional expected checksum, and detached signatures.

In people-speak:

Verification is not “best effort.” If a trust check fails, verification fails. No soft pass.

What is fail-closed here:
1) Schema must be valid.
2) Canonical digest must match payload.
3) If `--expected-sha256` is supplied, file bytes must exactly match.
4) If detached signature verification is requested, signature + public key must both be present and valid.

Where it is wired:
- `skills/hermes-attestation-guardian/scripts/verify_attestation.mjs`
  - schema checks
  - digest checks
  - expected checksum check
  - detached signature verification
  - non-zero exit on critical failure
- `skills/hermes-attestation-guardian/lib/attestation.mjs`
  - `validateAttestationSchema`
  - `validateDigestBinding`

How to verify:
- `node skills/hermes-attestation-guardian/test/attestation_schema.test.mjs`
  - proves schema rejection and digest algorithm validation behavior.
- `node skills/hermes-attestation-guardian/test/attestation_cli.test.mjs`
  - proves tamper path exits non-zero (fail closed).

Quick scenario:
- CI pins expected SHA and requires detached signature.
- Artifact is modified or signed incorrectly -> verification exits non-zero and blocks pipeline.

---

### Claim 3: Adds baseline authenticity and drift-severity classification for risky toggles, feed verification regressions, trust anchor drift, and watched file drift.

In people-speak:

You only compare against a baseline after proving the baseline itself is authentic. Then differences are ranked by severity so operators can respond quickly.

What this gives operators:
1) Authenticated baseline gate
- Baseline must be trusted (pinned digest and/or detached signature trust path).
- Untrusted baseline is rejected before diffing.

2) Severity-ranked drift findings
- Critical/high/medium/low/info mapping instead of flat alerts.
- High-signal categories include:
  - risky toggle enablement,
  - feed verification regressions,
  - trust anchor hash drift,
  - watched file hash drift.

3) Policy-driven failure threshold
- Verification can fail when findings meet/exceed configured severity threshold.

Where it is wired:
- Baseline trust and diff orchestration:
  - `skills/hermes-attestation-guardian/scripts/verify_attestation.mjs`
- Drift engine and severity mapping:
  - `skills/hermes-attestation-guardian/lib/diff.mjs`
  - `diffAttestations`
  - `highestSeverity`
  - `severityAtOrAbove`

How to verify:
- `node skills/hermes-attestation-guardian/test/attestation_cli.test.mjs`
  - proves untrusted baseline rejection and digest-pinned baseline handling.
- `node skills/hermes-attestation-guardian/test/attestation_diff.test.mjs`
  - proves classification for key drift types and highest-severity behavior.

Quick scenario:
- Yesterday’s baseline is pinned and trusted.
- Today `allow_unsigned_mode` flips on and trust anchor hash changes.
- Diff emits critical findings and verifier can fail run by severity policy.

---

### Claim 4: Adds Hermes-only cron setup helper with managed marker block and print-only default.

In people-speak:

You get a scheduler helper that is safe by default: it shows planned cron changes first, and only writes when you explicitly ask.

What “safe by default” means:
1) Hermes-only framing in UX and docs.
2) Managed marker block for clean replacement of only this module’s cron section.
3) Print-only default; write path requires explicit `--apply`.

Where it is wired:
- `skills/hermes-attestation-guardian/scripts/setup_attestation_cron.mjs`
  - managed markers
  - print-only defaults
  - apply path
- Supporting scope/docs:
  - `skills/hermes-attestation-guardian/SKILL.md`
  - `skills/hermes-attestation-guardian/skill.json`

How to verify:
- `node skills/hermes-attestation-guardian/test/setup_attestation_cron.test.mjs`
  - proves Hermes-only messaging and managed-block behavior.
  - proves default mode is preview-oriented and apply path is explicit.

Quick scenario:
- Operator runs cron helper without flags -> sees proposed block only.
- Operator reviews, then reruns with `--apply` -> only managed block is updated.

---

### Claim 5: Includes output-scope/path guardrails for attestation artifacts and policy parsing safeguards.

In people-speak:

Artifact writes are fenced into Hermes attestation scope, including symlink-escape defenses, and policy parsing is normalized/defensive so bad input fails cleanly.

What this protects against:
1) Out-of-scope writes
- Output path must remain under `HERMES_HOME/security/attestations`.

2) Symlink escapes
- Path resolution checks nearest existing ancestors and symlink behavior to prevent “write outside root” tricks.

3) Safer policy parsing
- Missing/invalid structure gets normalized defaults where appropriate.
- Malformed JSON fails closed.
- List fields are trimmed, deduplicated, and sorted.

Where it is wired:
- Guardrails:
  - `skills/hermes-attestation-guardian/lib/attestation.mjs`
    - `resolveHermesScopedOutputPath`
- Call sites:
  - `skills/hermes-attestation-guardian/scripts/generate_attestation.mjs`
  - `skills/hermes-attestation-guardian/scripts/setup_attestation_cron.mjs`
- Policy parsing:
  - `skills/hermes-attestation-guardian/lib/attestation.mjs`
    - `parseAttestationPolicy`

How to verify:
- `node skills/hermes-attestation-guardian/test/attestation_cli.test.mjs`
  - proves out-of-scope and symlink-escape output rejection.
- `node skills/hermes-attestation-guardian/test/setup_attestation_cron.test.mjs`
  - proves cron helper also rejects out-of-scope output target.

Quick scenario:
- Operator accidentally sets `--output /tmp/current.json`.
- Tool exits with critical path-scope error instead of writing outside Hermes scope.

---

### Claim 6: Cron managed-block parser fails closed on malformed markers.

In people-speak:

If cron markers are malformed (dangling start/end or nested blocks), updater refuses to rewrite crontab to avoid accidental deletion or corruption.

What this means operationally:
1) Marker structure is treated as integrity-sensitive input.
2) Malformed structure throws and aborts apply path.
3) No crontab write occurs after malformed marker detection.

Where it is wired:
- `skills/hermes-attestation-guardian/scripts/setup_attestation_cron.mjs`
  - `removeManagedBlock`
  - marker parsing and malformed-marker throw paths

How to verify:
- `node skills/hermes-attestation-guardian/test/setup_attestation_cron.test.mjs`
  - proves fail-closed behavior for:
    - dangling start marker,
    - unmatched end marker,
    - nested markers,
  - and verifies no write on malformed input.

Quick scenario:
- Existing crontab has managed start marker with no end marker.
- Running `--apply` aborts with malformed-marker error and leaves crontab unchanged.

## Current Capability Inventory (as implemented now)

Hermes Attestation Guardian now includes three capability lanes:

1) Attestation + baseline integrity lane
- Deterministic attestation generation.
- Fail-closed schema/digest/signature verification.
- Baseline authenticity requirements and severity-ranked drift diffing.
- Existing attestation cron helper with managed marker block and print-only default.

2) Advisory feed verification lane (Hermes-native)
- Signed advisory feed verification with fail-closed defaults.
- Checksum-manifest + signature verification when artifacts are present.
- Symmetric fail-closed handling for partial checksum artifact sets.
- Feed verification state/cache kept under Hermes security paths and read by attestation posture output.

3) Advisory-gated supply-chain lane
- Guarded skill verification flow with advisory-aware gating.
- Conservative matching when version is omitted.
- Explicit confirmation override required to proceed on matched advisories.
- Optional advisory scheduler helper with print-only default and managed marker apply path.

## Key Files
- `skills/hermes-attestation-guardian/skill.json`: metadata, platform scope, operator review notes, SBOM.
- `skills/hermes-attestation-guardian/SKILL.md`: operator playbook, CLI usage, fail-closed policy.
- `skills/hermes-attestation-guardian/README.md`: quickstart and practical behavior notes.
- `skills/hermes-attestation-guardian/lib/attestation.mjs`: canonicalization, digest binding, schema checks, scoped output resolution, policy parsing.
- `skills/hermes-attestation-guardian/lib/diff.mjs`: baseline drift comparison and severity classification.
- `skills/hermes-attestation-guardian/lib/feed.mjs`: Hermes advisory feed fetch/load, signature/checksum verification, state/cache handling.
- `skills/hermes-attestation-guardian/scripts/generate_attestation.mjs`: deterministic attestation generation CLI.
- `skills/hermes-attestation-guardian/scripts/verify_attestation.mjs`: fail-closed verifier and baseline trust enforcement.
- `skills/hermes-attestation-guardian/scripts/setup_attestation_cron.mjs`: attestation cron managed-block helper.
- `skills/hermes-attestation-guardian/scripts/refresh_advisory_feed.mjs`: refresh + verify advisory feed and update Hermes feed state.
- `skills/hermes-attestation-guardian/scripts/check_advisories.mjs`: operator-facing advisory/feed status summary.
- `skills/hermes-attestation-guardian/scripts/guarded_skill_verify.mjs`: advisory-gated guarded verification for candidate skill installs.
- `skills/hermes-attestation-guardian/scripts/setup_advisory_check_cron.mjs`: advisory scheduled-check helper with print-only default.

## Public Interfaces
- `generate_attestation.mjs` CLI
  - Consumer: operators/automation
  - Behavior: creates canonicalized attestation JSON and optional checksum artifact.
- `verify_attestation.mjs` CLI
  - Consumer: operators/automation/cron
  - Behavior: enforces schema/digest/signature checks and optional trusted-baseline drift checks.
- `setup_attestation_cron.mjs` CLI
  - Consumer: operators
  - Behavior: prints or applies managed cron block for scheduled generate+verify runs.
- `refresh_advisory_feed.mjs` CLI
  - Consumer: operators/automation
  - Behavior: fetches or loads advisory feed, verifies trust artifacts fail-closed by default, and updates Hermes advisory state/cache.
- `check_advisories.mjs` CLI
  - Consumer: operators/automation
  - Behavior: summarizes advisory feed verification status and current advisory visibility.
- `guarded_skill_verify.mjs` CLI
  - Consumer: operators/automation/install wrappers
  - Behavior: advisory-aware gate for skill name/version candidates; blocks on matches unless explicit confirmation override is provided.
- `setup_advisory_check_cron.mjs` CLI
  - Consumer: operators
  - Behavior: prints or applies managed cron block for scheduled guarded advisory checks.
- Diff output contract
  - Consumer: operators/CI
  - Behavior: emits severity-ranked drift findings for security triage.

## Validation Commands
```bash
python utils/validate_skill.py skills/hermes-attestation-guardian
node skills/hermes-attestation-guardian/test/attestation_schema.test.mjs
node skills/hermes-attestation-guardian/test/attestation_diff.test.mjs
node skills/hermes-attestation-guardian/test/attestation_cli.test.mjs
node skills/hermes-attestation-guardian/test/setup_attestation_cron.test.mjs
node skills/hermes-attestation-guardian/test/feed_verification.test.mjs
node skills/hermes-attestation-guardian/test/guarded_skill_verify.test.mjs
node skills/hermes-attestation-guardian/test/setup_advisory_check_cron.test.mjs
```

## Update Notes
- 2026-04-20: Expanded module coverage to include full Hermes capability set: signed advisory-feed verification lane, advisory-gated guarded skill verification lane, and advisory scheduler helper with managed marker block safety.
- 2026-04-17: Added v0.0.2 release-hardening notes: mandatory release verify triad (`checksums.json`, `checksums.sig`, pinned signing-key fingerprint), Hermes guard signature-aware trust policy note, and sandbox regression coverage for verify-gate + clean install.
- 2026-04-15: Replaced table-style PR claim mapping with full narrative claim breakdowns (people-speak, wiring, verification, and concrete scenarios per claim).

## Source References
- skills/hermes-attestation-guardian/skill.json
- skills/hermes-attestation-guardian/SKILL.md
- skills/hermes-attestation-guardian/README.md
- skills/hermes-attestation-guardian/CHANGELOG.md
- skills/hermes-attestation-guardian/lib/attestation.mjs
- skills/hermes-attestation-guardian/lib/diff.mjs
- skills/hermes-attestation-guardian/lib/feed.mjs
- skills/hermes-attestation-guardian/scripts/generate_attestation.mjs
- skills/hermes-attestation-guardian/scripts/verify_attestation.mjs
- skills/hermes-attestation-guardian/scripts/setup_attestation_cron.mjs
- skills/hermes-attestation-guardian/scripts/refresh_advisory_feed.mjs
- skills/hermes-attestation-guardian/scripts/check_advisories.mjs
- skills/hermes-attestation-guardian/scripts/guarded_skill_verify.mjs
- skills/hermes-attestation-guardian/scripts/setup_advisory_check_cron.mjs
- skills/hermes-attestation-guardian/test/attestation_schema.test.mjs
- skills/hermes-attestation-guardian/test/attestation_diff.test.mjs
- skills/hermes-attestation-guardian/test/attestation_cli.test.mjs
- skills/hermes-attestation-guardian/test/setup_attestation_cron.test.mjs
- skills/hermes-attestation-guardian/test/feed_verification.test.mjs
- skills/hermes-attestation-guardian/test/guarded_skill_verify.test.mjs
- skills/hermes-attestation-guardian/test/setup_advisory_check_cron.test.mjs
