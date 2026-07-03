# Issue #11800 - Advertising Account Spend Cap Concurrency

## Summary

Fixed account-level advertising spend cap write-skew by serializing cap-sensitive
allocation changes per ad account and by locking the account row during serve
spend checks.

## Verification

- `bun install --ignore-scripts` - pass during initial setup
- `bun install` - pass after rebasing onto `origin/develop`; artifact sync
  side effects were removed from the branch because they are unrelated to this
  fix
- `bun run --cwd packages/core build` - pass
- `bun run --cwd packages/security build` - pass
- `bunx @biomejs/biome check --write packages/cloud/shared/src/db/repositories/ad-accounts.ts packages/cloud/shared/src/db/repositories/ad-campaigns.ts packages/cloud/shared/src/db/repositories/ad-slots.ts packages/cloud/shared/src/lib/services/advertising/index.ts packages/cloud/shared/src/lib/services/__tests__/ad-account-approval.test.ts packages/cloud/shared/src/lib/services/__tests__/ad-campaign-credit-reconciliation.test.ts` - pass, no fixes applied
- `bun test packages/cloud/shared/src/lib/services/__tests__/ad-campaign-credit-reconciliation.test.ts` - pass, 14 tests
- `bun test packages/cloud/shared/src/lib/services/__tests__/ad-account-approval.test.ts` - pass, 20 tests
- `bun test packages/cloud/shared/src/lib/services/__tests__/ad-inventory.test.ts` - pass
- `bun run --cwd packages/cloud/shared lint` - pass
- `bun run --cwd packages/cloud/shared typecheck` - pass
- `git diff --check` - pass
- `bun run verify` - fails before workspace lint/typecheck on the existing repo
  `audit:type-safety-ratchet` baseline: ``?? ""`` is `616 / 615` (confirmed
  both before and after rebase).

## Evidence Notes

- Frontend screenshots/video: N/A - backend repository/service concurrency fix.
- Real LLM trajectories: N/A - no agent, prompt, model, or provider behavior.
- Domain artifacts: focused tests exercise credit deduction/refund behavior,
  provider rollback after a cap race, cap setter rejection, and PGlite inventory
  serve debit paths.
