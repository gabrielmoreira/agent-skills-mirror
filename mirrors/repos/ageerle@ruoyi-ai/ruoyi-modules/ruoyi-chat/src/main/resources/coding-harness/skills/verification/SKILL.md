---
name: verification
description: Prove that a coding task is actually complete. Use this after meaningful code changes, when tests/builds fail or are skipped, before marking a plan or goal complete, and whenever acceptance depends on runtime, security, recovery, performance, or cross-module evidence.
---

# Verification

Turn the task's acceptance criteria into trustworthy evidence. Verification is part of implementation, not a ceremonial final command.

## Build an evidence matrix

For each requirement, identify:

- the observable behavior or invariant;
- the cheapest deterministic check that can falsify it;
- the artifact that records the result (test report, exit code, diff, event ledger, benchmark, or trace);
- gaps that require a broader integration test or human decision.

Use existing repository commands and focused tests first. Add a regression test when the behavior was previously broken or the boundary is subtle.

## Derive semantic boundary cases

Turn every normative sentence in the requirement and relevant repository contract into a falsifiable example before accepting a visible green test.

- For parsers and serializers, preserve delimiter and escape provenance until structural tokenization is complete. Test adjacent escapes, escaped delimiters, whitespace normalization, malformed escapes, exact field counts, duplicates, empty values, and round trips where applicable.
- For idempotent or batched mutations, validate both shape and semantic conflicts across the entire batch and against existing state before the first write. Test same-key/same-payload and same-key/different-payload behavior, serial and concurrent calls, and assert rejected operations leave state unchanged.
- For state machines, test invalid transitions, retries, stale revisions, cancellation, and crash/restart windows rather than only the happy path.
- For resource limits, test the exact boundary, one below, one above, and cumulative accounting after retry or restart.

## Interpret results correctly

- A successful compile does not prove runtime behavior.
- A test command that selects zero tests is not a pass.
- A skipped environment-dependent security test must be identified and covered elsewhere when it matters.
- Tool text beginning with an error, a non-zero exit, timeout, cancellation, incomplete assertion set, or missing artifact cannot count as success evidence.
- Validate streamed/durable systems from committed state and replay, not only the live UI.
- For concurrency and recovery, exercise the race/crash boundary rather than infer correctness from sequential code.

## Coding-agent completion gate

Before completion, check at least:

1. the original requirement and all explicit feedback are addressed;
2. the authoritative plan has no incomplete required step;
3. relevant build/type/lint and focused tests passed and actually ran;
4. the final diff contains only intended changes and preserves user-owned work;
5. security, ownership, cancellation, and persistence invariants affected by the change have evidence;
6. remaining limitations are reported precisely.

Record evidence with stable IDs or artifact hashes so it can survive compaction and restart. Only the Harness/verifier should close acceptance criteria; confident model prose is not evidence.
