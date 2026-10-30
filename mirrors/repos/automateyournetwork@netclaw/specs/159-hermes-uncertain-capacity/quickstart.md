# Verification quickstart

Use a private temporary installation, controlled httpx transport and existing
Node24.19 runtime. Never point test fixtures at an owner's runtime or provider.

1. Run `uv run --with httpx python -m unittest discover -s tests/hermes-hud -p 'test_*.py'`.
2. Run HUD Node tests for runtime recovery, runtime-client and Hermes React UI,
   including Specs157/158 regressions; build HUD with supported Node.
3. Review fixture: four lost admissions; ordinary acknowledgment still full;
   explicit release; restart; one new request accepted. Duplicate nonce and
   original conversation remain blocked; no old POST repeats.
4. Verify cancel, malformed intent, foreign owner, federation, known run,
   terminal/active request and concurrent release rejection/idempotency.
5. Read verification.md for actual outcomes and platform limits.
