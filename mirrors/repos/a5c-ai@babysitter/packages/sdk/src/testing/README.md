# Testing Utilities

The helpers in `packages/sdk/src/testing` provide a deterministic harness for exercising runs without the real orchestrator. They cover three pillars:

1. Seed clocks/ULIDs so every journal file, state snapshot, and effect invocation key is reproducible.
2. Spin up disposable run directories that already contain a `RUN_CREATED` event and cleaned-up tmp roots.
3. Capture structured snapshots plus per-iteration execution logs from the fake runner harness.

## Seeding clocks and ULIDs

```ts
import { installFixedClock, installDeterministicUlids } from "@a5c-ai/babysitter-sdk/testing";

const clock = installFixedClock({ start: "2025-01-01T00:00:00Z", stepMs: 250 });
const ulids = installDeterministicUlids({ randomnessSeed: 42 });

// .. run your test ..

clock.restore();
ulids.restore();
```

- `installFixedClock` overrides the storage clock used by run metadata/journaling. Call `clock.apply()` when you need it active (helpers like the harness do this for you) and `clock.reset()` if you want to rewind without reallocating.
- `installDeterministicUlids` swaps the ULID factory used by journal writers. Pass `{ preset: [...] }` to replay a known sequence or rely on the deterministic Crockford-base32 generator.

## Deterministic run harness

```ts
import { createDeterministicRunHarness } from "@a5c-ai/babysitter-sdk/testing";

const harness = await createDeterministicRunHarness({
  processSource: `
    export async function process(inputs, ctx) {
      return ctx.task(/* ... */);
    }
  `,
  inputs: { start: 1 },
});

try {
  await runToCompletionWithFakeRunner({
    runDir: harness.runDir,
    resolve,
    clock: harness.clock,
    ulids: harness.ulids,
  });
} finally {
  await harness.cleanup();
}
```

`createDeterministicRunHarness`:

- Accepts either `processPath` or inline `processSource`, spins up a disposable runs root, calls `createRunDir`, and appends `RUN_CREATED`.
- Installs deterministic clock/ULID providers that remain active until `cleanup()`.
- Returns `clock`/`ulids` handles you can pass into the fake runner harness or manage manually (call `reset()` if you start a brand-new run without reallocating the harness).

## Fake runner execution logs

`runToCompletionWithFakeRunner` now accepts two optional fields:

- `clock`: a handle from `installFixedClock` to keep `ctx.now()` deterministic.
- `ulids`: a handle from `installDeterministicUlids` so new journal entries keep using the seeded generator.

Every invocation returns `executionLog`, an array describing each iteration:

```ts
const { executionLog } = await runToCompletionWithFakeRunner({ /* ... */ });

executionLog[0];
// {
//   iteration: 1,
//   status: "waiting",
//   pending: [{ effectId, invocationKey, schedulerHints }],
//   executed: [{ effectId, taskId, schedulerHints }],
//   metadata: { ...iterationMetadata }
// }
```

Use it to assert deterministic ordering, scheduler hints (e.g., `parallelGroupId`), and pending slices after partial resolutions.

## Snapshot helpers

After a fake run you can diff the entire run directory with one helper:

```ts
import { captureRunSnapshot } from "@a5c-ai/babysitter-sdk/testing";

const snapshot = await captureRunSnapshot(harness.runDir);
expect(snapshot.journal).toMatchInlineSnapshot();
expect(snapshot.state?.effectsByInvocation).toMatchObject({
  "task#alpha": { status: "resolved_ok" },
});
```

- `readJournalSnapshot` and `readStateSnapshot` expose the individual pieces when you only need one.
- The snapshots are safe to compare directly across OSes because the clock/ULID seeding above strips nondeterminism from `recordedAt`, filenames, and effect IDs.

## Keeping docs + harness examples in sync

Sections 10.5 and 13 of `sdk.md`, the CLI walkthrough (`docs/cli-examples.md`), and the SDK quickstart in `README.md` quote the APIs above verbatim. Before changing this README or any referenced snippet:

1. **Run the harness doc suite.**

```bash
pnpm --filter @a5c-ai/babysitter-sdk run docs:testing-readme
```

This command executes every fenced example in this file (and any referenced fixtures under `packages/sdk/src/testing/__examples__`) using the deterministic clock/ULID helpers. It produces `_ci_artifacts/testing-harness/<platform>/report.json` so reviewers can diff execution logs, pending counts, and seeds.

2. **Sync with `sdk.md` and `docs/cli-examples.md`.**
   - Snippets extracted from sdk.md §§8–13 and this README are compiled via `pnpm --filter @a5c-ai/babysitter-sdk run docs:snippets:tsc`.
   - The CLI walkthrough records real runs with `pnpm --filter @a5c-ai/babysitter-sdk run smoke:cli` and links back to this README when it references `runToCompletionWithFakeRunner` or `captureRunSnapshot`.

3. **Capture artifacts and hashes.**
   - Store execution logs, snapshot archives, and deterministic seed data under `_ci_artifacts/testing-harness/`.
   - Include a short note in your PR describing which snippets were regenerated and how to reproduce them (see `part7_test_plan.md` for the full checklist).

4. **Respect redaction + platform notes.**
   - Keep examples redacted unless explicitly describing the `BABYSITTER_ALLOW_SECRET_LOGS` guard (sdk.md §12.4).
   - Mention that CLI output uses POSIX-style paths even on Windows; tests here should normalize separators to match the docs.

Following this workflow ensures the SDK docs, README quickstart, and CLI walkthrough stay consistent with the deterministic harness delivered in `packages/sdk`.
