# Picoclaw Security Guardian

## Summary

Current package version: `v0.0.1`.

`picoclaw-security-guardian` is the core Picoclaw package for:
1. advisory awareness (fail-closed on unverified feed state),
2. deterministic profile generation + drift detection,
3. release artifact supply-chain verification.

Self-pen-testing checks were intentionally split out into `picoclaw-self-pen-testing` so moderation-sensitive logic can be published/managed independently.

## Responsibilities

- Filter Picoclaw-relevant advisories from verified ClawSec feed state/cache.
- Build deterministic posture profiles from Picoclaw config/security files and optional release artifacts.
- Compare baseline vs current profile with severity-ranked findings.
- Verify release artifacts with checksum manifest + required detached signature for passing provenance verdicts.

## Default safety posture

- Read-only by default
- No scheduler creation
- No outbound network by default
- Advisory checks fail closed unless verification state is `verified` (or explicit `--allow-unsigned` override)
- Supply-chain verification requires detached-signature verification for a passing provenance result

## Verification commands

```bash
python utils/validate_skill.py skills/picoclaw-security-guardian
node skills/picoclaw-security-guardian/test/profile.test.mjs
node skills/picoclaw-security-guardian/test/drift.test.mjs
node skills/picoclaw-security-guardian/test/supply_chain.test.mjs
bash -n skills/picoclaw-security-guardian/test/picoclaw_security_guardian_sandbox_regression.sh
```

## Picoclaw-native sandbox regression

`skills/picoclaw-security-guardian/test/picoclaw_security_guardian_sandbox_regression.sh` publishes the package via a local ClawHub-compatible registry, installs through Picoclaw `find_skills` / `install_skill`, validates skill-loader visibility, and runs installed profile/drift/advisory/supply-chain flows against isolated Picoclaw fixtures.

## Related package

- `skills/picoclaw-self-pen-testing/` (optional separate self-pen-testing package)

## Source references

- `skills/picoclaw-security-guardian/skill.json`
- `skills/picoclaw-security-guardian/SKILL.md`
- `skills/picoclaw-security-guardian/README.md`
- `skills/picoclaw-security-guardian/lib/profile.mjs`
- `skills/picoclaw-security-guardian/lib/drift.mjs`
- `skills/picoclaw-security-guardian/lib/advisories.mjs`
- `skills/picoclaw-security-guardian/lib/supply_chain.mjs`
- `skills/picoclaw-security-guardian/scripts/generate_profile.mjs`
- `skills/picoclaw-security-guardian/scripts/check_drift.mjs`
- `skills/picoclaw-security-guardian/scripts/check_advisories.mjs`
- `skills/picoclaw-security-guardian/scripts/verify_supply_chain.mjs`
- `skills/picoclaw-security-guardian/test/profile.test.mjs`
- `skills/picoclaw-security-guardian/test/drift.test.mjs`
- `skills/picoclaw-security-guardian/test/supply_chain.test.mjs`
- `skills/picoclaw-security-guardian/test/picoclaw_security_guardian_sandbox_regression.sh`
