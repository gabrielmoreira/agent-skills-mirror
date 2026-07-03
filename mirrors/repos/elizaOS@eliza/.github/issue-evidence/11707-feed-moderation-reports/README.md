# Issue 11707 - moderation reports API

## Change

- Added `POST /api/moderation/reports` for authenticated user/post report submission.
- Added `GET /api/moderation/reports` gated by `view_reports` and backed by `GetReportsSchema`.
- Ensured post reports store the post author as `reportedUserId`, so the existing report evaluation pipeline can collect reported-user context instead of returning insufficient evidence for post reports.
- Added real-server integration coverage for unauthenticated GET, user report creation, post report creation, and admin listing.

## Validation

- `bunx @biomejs/biome check --config-path ../../biome.json --vcs-enabled=false --files-ignore-unknown=true --no-errors-on-unmatched apps/web/src/app/api/moderation/reports/route.ts packages/testing/integration/moderation-reports-api.integration.test.ts`
  - Passed; 2 files checked.
- `DATABASE_URL='postgresql://feed:feed_dev_password@localhost:5433/feed' DIRECT_DATABASE_URL='postgresql://feed:feed_dev_password@localhost:5433/feed' bun run --cwd packages/feed scripts/test-integration-with-server.ts packages/testing/integration/moderation-reports-api.integration.test.ts`
  - Passed; 4 tests, 19 assertions.
- `DATABASE_URL='postgresql://feed:feed_dev_password@localhost:5433/feed' DIRECT_DATABASE_URL='postgresql://feed:feed_dev_password@localhost:5433/feed' bun run --cwd packages/feed scripts/test-integration-with-server.ts packages/testing/integration/api-endpoints.integration.test.ts packages/testing/integration/moderation-reports-api.integration.test.ts`
  - The existing endpoint inventory reached and passed `GET /api/moderation/reports - requires auth`, then failed later on unrelated `GET /api/nft/gallery` returning 503.
- `git diff --check`
  - Passed.

## Known Gaps

- `bun run --cwd packages/feed/packages/api typecheck` and `bun run --cwd packages/feed/packages/testing typecheck` are blocked before checking these changes by `packages/feed/packages/tsconfig.base.json` setting `ignoreDeprecations: "6.0"` while the feed workspace resolves TypeScript 5.9.3.
- UI video/screenshot evidence for clicking `ReportModal` was not captured in this pass. The server route exercised by `ReportModal` is covered by the real-server integration test above.
- Real LLM trajectory evidence is N/A for this route wiring change; the existing report evaluation pipeline is dispatched best-effort and was not changed.
