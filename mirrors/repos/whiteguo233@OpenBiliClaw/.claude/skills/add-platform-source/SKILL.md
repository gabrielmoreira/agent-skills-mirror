---
name: add-platform-source
description: Use when adding, integrating, completing, testing, or releasing a new OpenBiliClaw platform/source adapter, including browser-extension logged-in sources, discover branches, guided init, config pages, recommendation cards, CLI smoke commands, and real end-to-end validation.
---

# Add Platform Source

Read `docs/platform-source-integration.md` from the repository root completely, then follow it as the authoritative checklist.

Key constraints:

- Treat a source as an end-to-end product path: backend, extension/server collection, CLI smoke, guided init, formal discover, config pages, recommendation cards, tests, docs, and release.
- For login-dependent platforms, validate with the installed extension browser that has the real login state. Do not substitute CDP/MCP/browser automation unless explicitly requested.
- Keep smoke tasks non-mutating unless the user asks for memory/profile writes through explicit flags.
- Separate safe E2E from account-mutating E2E: snapshot/scroll/click/share can be run by default; like/favorite/follow/save/upvote need explicit user permission or a test account.
- For search-capable discover sources, wire BOTH halves of the unified keyword pipeline: generation (both the merged-prompt track and the keyword-inspiration axis track) and fetching (`KeywordFetchCoordinator.claim(<slug>)`). Claim/fetch without planner generation — or covering only one generation track — is incomplete. Exact registration points and tests are in the guide's discover section; follow it, don't recall from memory.
- Candidate pool admission must go through the shared admission policy (`discovery/admission.py`); strategies and producers must not invent their own min-score thresholds.
- Verify user-facing surfaces, not only backend fetch: plugin settings, PC web settings, setup/init, source status, source share quota, and recommendation cards on PC/mobile/plugin must all agree with the real implementation.
- Declare the source contract up front for engagement counts (which of view/like/favorite/comment/share/danmaku are mappable vs structurally absent — absent ones stay 0 and unrendered) and for the real login cookie (guest cookies don't count; wire the cookie-sync login-state channel).
- New plugin task endpoints must use the exact `/api/sources/<slug>/{next-task,task-result,kick}` path shape (the init write-guard matches URL segments) and call the backend through the authenticated shared extension API client.
- Eval/profile E2E must use the user's configured local LLM/embedding providers; do not silently substitute mocks, Ollama, or another provider.
- Do not claim completion until unit tests, extension tests/builds, and real E2E checks relevant to the source have been run.
- For releases, verify tag uniqueness, version alignment, CI/package workflows, aggregate release assets, GHCR docker images (new default dependencies must land in the image; new packages need manual public visibility), plugin marketplace submission, and local untracked/ignored artifacts before reporting done.
