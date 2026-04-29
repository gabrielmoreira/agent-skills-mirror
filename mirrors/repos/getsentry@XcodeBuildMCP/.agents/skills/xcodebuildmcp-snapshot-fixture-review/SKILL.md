---
name: xcodebuildmcp-snapshot-fixture-review
description: Use when reviewing XcodeBuildMCP snapshot fixture changes for MCP, CLI, and JSON output contract integrity.
---

# XcodeBuildMCP Snapshot Fixture Review

Review guardrails for fixture and snapshot contract integrity.

## Review scope

- Review-only by default.
- Do not edit product code unless the user explicitly requests implementation changes.

## Files to inspect

- `src/snapshot-tests/__fixtures__/**`
- `src/snapshot-tests/contracts.ts`
- `src/snapshot-tests/fixture-io.ts`
- `src/snapshot-tests/__tests__/fixture-io.test.ts`
- `src/snapshot-tests/__tests__/json-normalize.test.ts`
- `src/snapshot-tests/__tests__/json-fixture-schema.test.ts`
- `xcodebuildmcp.com/app/docs/_content/testing.mdx`

## Guardrails

- Fixture updates map to intentional behavior changes.
- Do not update fixtures only to make tests pass.
- MCP, CLI, and JSON fixture updates stay aligned.
- JSON fixtures preserve stable structured output envelopes.
- Volatile values are normalized in code, not patched ad hoc in fixtures.
- Missing fixtures are generated through the snapshot update flow.

## Validation

- `npm run test:snapshots`
- `npm run test:schema-fixtures`
- `npm test -- src/snapshot-tests/__tests__/fixture-io.test.ts`
- `npm test -- src/snapshot-tests/__tests__/json-normalize.test.ts`
- `npx skill-check .agents/skills/xcodebuildmcp-snapshot-fixture-review`
