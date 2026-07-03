# Issue #11802 — Cloud files quota and upload fan-out

## Change

- `CloudFilesService.upload` now reserves bytes against `org_storage_quota` before writing to R2.
- Upload quota reservations are released if the R2 write or metadata insert fails.
- Deleting the final active uploaded file reference removes the R2 object and releases the stored byte count.
- `/api/v1/files` rejects multipart requests with more than 10 files before any storage writes.
- `/api/v1/files` maps quota exhaustion to HTTP 413 with the same user-facing quota message as the storage object API.

## Verification

```bash
bun install --ignore-scripts
bun run --cwd packages/core build
bun run --cwd packages/security build
git fetch origin && git rebase origin/develop
bun install
bun test packages/cloud/api/__tests__/cloud-files-route.test.ts
bun test packages/cloud/shared/src/lib/services/cloud-files.test.ts
bun run --cwd packages/cloud/api lint
bun run --cwd packages/cloud/shared lint
bun run --cwd packages/cloud/api typecheck
bun run --cwd packages/cloud/shared typecheck
bun run --cwd packages/cloud/api build
git diff --check
bun run verify
```

Results:

- Rebased onto `origin/develop` at `05cd404a54`.
- `bun install` completed after the rebase; generated artifact-download churn was removed from the tracked diff.
- Cloud files route test: 9 tests passed.
- Cloud files service test: 5 tests passed.
- Cloud API lint, typecheck, and build: passed.
- Cloud shared lint and typecheck: passed after building the local `@elizaos/security` workspace dependency.
- `git diff --check`: passed.
- `bun run verify`: failed before package checks in `audit:type-safety-ratchet`; current `?? ""` count in core/agent/app-core is `616 / 615`.

## Evidence Matrix

- Real request/response trace: covered by the Hono route test for file-count rejection and quota 413 mapping.
- DB state / quota rows: covered by service tests asserting `tryReserveBytes` and `releaseBytes` calls for success, failure cleanup, quota rejection, and delete.
- Auth / tenant isolation: existing route tests in the same file continue to assert authenticated organization scoping for list/get/delete.
- Frontend screenshots/video: N/A - backend API and service change only.
- Live model trajectories: N/A - no model-backed endpoint, prompt, provider, or agent behavior changed.
- Migration up/down: N/A - no schema or migration change; this wires an existing `org_storage_quota` table into an unguarded route.
