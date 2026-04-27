# Picoclaw Self Pen Testing

## Summary

Current package version: `v0.0.1`.

`picoclaw-self-pen-testing` is a standalone Picoclaw package that runs local, read-only self-pen-testing style checks from a generated Picoclaw posture profile.

This package is intentionally separate from `picoclaw-security-guardian` so moderation-sensitive findings can be shipped independently.

## What it checks

- Public Web UI exposure
- Disabled Web UI auth
- Unrestricted workspace/tooling posture
- Unsafely unsigned verification mode
- MCP trust-boundary review needs
- Scheduler persistence review
- Plaintext secret markers
- Multi-channel auth review

## Usage

```bash
node skills/picoclaw-self-pen-testing/scripts/self_pen_test.mjs \
  --profile ~/.picoclaw/security/clawsec/current-profile.json
```

## Validation

```bash
python utils/validate_skill.py skills/picoclaw-self-pen-testing
node skills/picoclaw-self-pen-testing/test/self_pen_test.test.mjs
```

## Source references

- `skills/picoclaw-self-pen-testing/skill.json`
- `skills/picoclaw-self-pen-testing/SKILL.md`
- `skills/picoclaw-self-pen-testing/README.md`
- `skills/picoclaw-self-pen-testing/lib/self_pen_test.mjs`
- `skills/picoclaw-self-pen-testing/lib/format.mjs`
- `skills/picoclaw-self-pen-testing/scripts/self_pen_test.mjs`
- `skills/picoclaw-self-pen-testing/test/self_pen_test.test.mjs`
