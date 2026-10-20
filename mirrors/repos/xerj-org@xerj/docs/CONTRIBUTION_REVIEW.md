# Contribution review protocol

This protocol turns recurring review findings into a repeatable pre-submission audit. It applies to humans and AI agents. Use the parts relevant to the change, list every section judged not applicable and why, record what was not tested, and never treat a green but unrelated suite as evidence for the behavior being changed.

The repository-wide ground rules in [`AGENTS.md`](../AGENTS.md) remain authoritative. In particular, engine changes must pass the ES-YAML hard gate described there; this document does not require unrelated conformance work for a docs-only or otherwise isolated change.

## Start with the change that will actually merge

Before reviewing code, establish its ancestry and scope:

1. Fetch the current upstream `main` and inspect the merge-base, commits unique to the branch, and the complete `main...HEAD` diff.
2. Identify prerequisite PRs and commits. Say whether the branch is independent, stacked, or temporarily contains duplicated prerequisite commits.
3. Read the relevant commit history before deriving a new design. Preserve intentional invariants and previous fixes.
4. Reconcile with current `main` before final validation. Usually that means rebasing or merging; if overlapping work makes waiting safer, document why, prove the current branch merges cleanly, and rely on the final merge-ref only for the interaction coverage it actually runs. Re-run interaction tests when another change touches the same state machine, lifecycle boundary, mapping, workflow, or hot path.
5. Inspect the final diff for unrelated files, generated artifacts, reverted upstream changes, weakened tests, and stale documentation.
6. Do not use a passing merge-ref to excuse an unexplained branch structure. The PR description must state merge order and known dependencies.

For stacked work, review both the isolated commit range and the effective diff against `main`. A correct patch can still be unsafe when composed with its prerequisite or with a recently merged change.

## Preserve the existing product contract

A fix must not turn a partial correctness problem into a wider availability problem. Before changing a guard, migration, optimization, or recovery path, enumerate the previously supported workflows and decide explicitly which remain supported.

At minimum, consider:

- first run, unchanged rerun, changed-input rerun, interrupted run, and restart;
- empty, partial, pending, committed, malformed, and legacy durable state;
- additions, replacements, removals, duplicates, and ownership changes;
- default configuration, optional features, degraded environments, and supported platforms;
- interactive output, `--json`, exit codes, HTTP contracts, and agent-readable fields;
- the top-level `xerj autoindex` and `xerj brain` workflows when shared code changes.

If behavior must become fail-closed, refuse only the unsafe case. Name what was detected, state whether remote or durable state changed, and give an executable recovery route. Test that the recovery route actually works; an error that merely says “retry” or recommends a now-rejected flag is not a recovery contract.

## Operational documentation and runnable recipes

Treat every shell, TOML, systemd, configuration, and copy-paste command in a recipe as a program, not illustrative prose. Execute the ordered success path and a deliberate negative control, such as a bad checksum, missing artifact, or disallowed egress. A negative path fails closed only when the recipe exits non-zero and no artifact is extracted, installed, published, or served. Record the observed exit status, the state at refusal, and the recovery command, and prove that recovery succeeds.

A runnable block that verifies an artifact must also be the block that acts on it. Do not hand off through a filesystem path between a verifying block and a privileged block.

Run each negative control in two additional compositions: one that discards the failing block's exit status, and one that appends the next documented block. In both compositions, require that no artifact is extracted, installed, published, or served and that no unsafe or privileged path is reached.

For every directory or path a recipe reads or writes, name the trust boundary and who can write there. Treat an untrusted staging tree as attacker-controlled: assume an attacker can pre-create any path the recipe will use, including a path whose name is derived from a published digest. Create scratch space outside that tree, exercise the negative control with attacker-precreated paths already present, and verify the refusal state.

Exercise the process lifecycle: startup, readiness/health, the first real operation, graceful stop, cleanup, port release, and restart from the same state. For persistent configuration or data, test fresh state, existing state, migration/reindex requirements, an unchanged rerun, and the documented recovery or rollback transition; distinguish what is preserved from what is discarded.

Give every count an explicit unit, such as files, pages, variants, link elements, requests, or routes. If a claim says “all X”, “only X”, or “no X”, define X as a concrete set and enumerate its members. List exclusions. State which feature, platform, transport, and fallback variants were tested. Separately list every unsupported variant. Verify every publication copy.

Document a concrete mitigation that is executable in the stated environment, such as a firewall rule paired with a negative egress probe, a source-rebuild command, or a service-hardening setting. Do not recommend a runtime switch or workaround that the product does not implement.

When a document is published through multiple paths, trace the publication topology from its source through generated pages, indexes, navigation, and agent-facing copies. For claims about an already-published release, reuse `scripts/verify-release.sh`; it does not validate an unpublished pull request or an offline recipe.

## Durable state is not invocation state

Treat a resume journal, sealed snapshot, mapping, catalog document, index, or generation marker as authority. Treat counters, temporary files, process IDs, clocks, caches, and in-memory collections as invocation-local unless explicitly persisted.

Review every field that is rewritten on a zero-work resume:

- Can it be reconstructed from durable committed records?
- Does an unchanged rerun preserve the prior value rather than overwrite it with zero or “now”?
- Is it written only after the corresponding publication is durable?
- Does failure leave the old authority intact?
- Can a pending state be mistaken for a committed state?
- Is an identifier unique under same-process, same-second, retry, and concurrent execution?

When the change introduces a new persistent field, specify its ownership, versioning, backward-compatible default, upgrade behavior, and removal plan. Do not infer durable corpus totals from work performed only in the current invocation.

When correcting one field in a replacement document or bulk write, audit every sibling field in that document. One durable value does not make invocation-local counters, notes, timestamps, or derived metadata durable; a zero-work resume can silently reset any of them.

## Legacy mappings and stored-data migrations

“Additive mapping” is a claim that must be tested against real prior state, not only a fresh index or a mock that always returns HTTP 200.

For any persistent schema change:

1. Identify whether the field already existed dynamically, under another type, or in older serialized records.
2. Exercise the upgrade against representative data from every materially distinct supported schema generation, including the oldest supported format.
3. Make the mock reproduce the engine’s actual conflict or parse response.
4. Do not swallow all mapping errors to tolerate one known conflict. Narrow the compatibility behavior to that field and response.
5. Keep unrelated upgrades mandatory so genuine failures still stop the operation.
6. Document changed field meaning even when the wire type stays compatible.

If migration cannot be automatic, provide an exact, tested operator procedure that names the affected indices, state directories, prefixes, or generations and explains what is preserved or lost.

## Failure atomicity and preflight ordering

Validate every locally knowable preflight condition before deleting, truncating, rotating, sealing, publishing, or mutating remote state. For failures discoverable only during remote I/O or publication, define the intent, commit, rollback, and retry boundaries and make recovery explicit. The test must compare state before and after the refusal or mid-operation failure, not just assert an error.

For destructive or generation-changing operations, cover both committed and pending authority. Prove that:

- journal bytes and sealed snapshots remain unchanged;
- existing remote documents remain readable;
- no partial new generation becomes authoritative;
- a normal resume or the documented isolated recovery succeeds afterward;
- the error identifies the actual failed precondition.

Test the ordering over the real transport boundary where possible. A unit test of a predicate does not prove that the predicate runs before a remote mutation.

## Optional optimizations must remain optional

An accelerator, cache, spool, replay artifact, or approximate fast path must not become a new correctness dependency unless the public contract explicitly changes.

Define the fallback before optimizing:

- If optional state is unavailable, corrupted, over budget, or unsupported on the platform, can the established path still produce the same result?
- Does a fallback classify the accelerator failure accurately instead of blaming source data or backend configuration?
- Are fallback and cleanup counters exact?
- Is the fallback bounded, observable, and covered by a test that reaches it?

Avoid unconditional work that benefits only the admitted fast path. Expensive verification, hashing, file reads, allocation, and warnings should be gated on an artifact or optimization actually being usable.

## Machine contracts must be exact

Agent-facing JSON, HTTP responses, CLI exit codes, identity endpoints, telemetry, and recovery objects are APIs.

For each field:

- derive it from the effective runtime behavior, not only the requested configuration;
- omit or mark unknown values that cannot be pinned honestly;
- bind identities to behavior-changing bytes, algorithms, dimensions, and fallbacks;
- keep error types, stdout/stderr routing, and exit codes stable and documented;
- avoid leaking paths, credentials, endpoints, model locations, or internal error details;
- use stable or deterministic identifiers only when equivalent inputs must compare equal;
- use collision-resistant or monotonic identifiers when uniqueness is required, and test same-process, same-timestamp, retry, and concurrent creation.

A test that pins a descriptive string does not prove the underlying algorithm is pinned. Use an independent golden probe or behavior fixture, then ensure the runtime identity incorporates that probe.

Derive an execution identity from the exact immutable bytes and effective configuration the runtime will load, and execute from that same snapshot. Hashing a mutable file and reopening it later leaves a time-of-check/time-of-use gap. Scope retained snapshots to the engine or execution lifetime and release them with that owner; do not turn identity safety into an unbounded process-global retention policy.

Define ambiguity and tie behavior for every durable-state or schema match. Never let hash-map iteration or incidental lexicographic ordering choose among equally valid candidates. Fail closed, ask for disambiguation, or use an explicitly approved product tie-break, and cover the equal-best case with a regression test.

## Tests must fail for the defect

For each important claim, identify at least one regression test and prove that a targeted mutation or source-hunk revert makes it fail for the intended reason.

Prefer this ladder:

1. a deterministic unit test for the local invariant;
2. a state-machine or integration test for transitions and persistence;
3. a real HTTP or CLI test for ordering, routing, error text, and recovery;
4. an end-to-end workflow test for the user-visible contract.

Do not weaken or invert a previously valid assertion merely to accommodate the new implementation. If an old test encoded intended behavior, changing it requires an explicit product decision and documentation.

### Keep tests deterministic and resource-independent

Tests must not silently depend on wall-clock resolution, available disk, descriptor limits, thread scheduling, CPU count, network availability, process order, or a specific build profile.

- Inject clocks, IDs, disk headroom, descriptor headroom, and failpoints.
- Gate profile-specific assertions with the matching configuration.
- Make unsupported-platform behavior explicit.
- Skip with a visible reason only when dependency injection is impractical.
- Assert the diagnostic or state transition, not merely a non-zero exit that an unrelated failure could also produce.

### Isolate process-global state

Counters, environment variables, singleton runtimes, failpoints, caches, and test-only delays shared by a test binary can contaminate parallel tests.

Use scoped guards that restore state on drop, serialize every caller that touches the same global, or replace the global with an injected per-test object. Resetting a counter inside one test is insufficient if another test can increment it concurrently. Run the focused suite repeatedly and under the same release/debug profile CI uses.

## Telemetry is a correctness surface

Every reported count must define its scope and increment at the event it names.

- “parser calls” increments only after a parser was successfully invoked.
- “live” and “peak” values change only after admission succeeds and are decremented on every exit path.
- “verified replay” requires a successful verification.
- invocation metrics must not be presented as durable dataset totals.
- final “current” resource gauges should return to their documented baseline.
- timestamps must distinguish invocation start from summary generation.

Add success, fallback, refusal, and zero-work-resume assertions for the telemetry block itself. Deleting an increment should fail a test. If exactness is impossible, rename the field to state the approximation.

## Feature-gated code needs feature-gated CI

If a meaningful code path is behind a Cargo feature, platform condition, optional backend, or build mode, at least one applicable CI job must compile it and run its focused tests. Also run strict Clippy for that feature combination.

Preserve the repository’s existing workflows while adding coverage. Inspect the full workflow after conflict resolution or maintainer follow-ups; do not accidentally replace unrelated jobs. Avoid downloading large external assets in the standard gate when byte fixtures or ignored real-model tests can validate the contract.

## Performance and resource claims

A performance PR must be correct before it is fast. Faster-but-wrong is a regression.

Record:

- exact control and candidate commits and build profiles;
- corpus/query manifest, configuration, hardware, concurrency, and cache state;
- repeated runs and the chosen summary statistic;
- wall time, throughput, peak memory, and correctness/quality gates relevant to the claim;
- raw repository-visible artifacts or a reproducible command;
- known trade-offs and workload boundaries.

Use matched builds and change one variable at a time. Do not compare an isolated embedding layer with end-to-end indexing, documents per second with requests per second, warm with cold, or a small controlled sample with the full corpus without labeling the distinction.

For memory work, distinguish logical retained bytes, allocator active/resident bytes, process RSS/high-water mark, mapped files, and transient concurrency. A lower logical counter is not proof of lower process memory. For CPU work, use profiling or phase attribution to show the changed path is material before optimizing it.

Public numbers belong in the PR only after the cited run is reproducible and quality-equivalent. State negative results and known gaps; do not turn an experiment into a product-wide claim.

## PR scope, descriptions, and follow-ups

Prefer the smallest independently correct and useful PR, not the smallest diff. Split work when each part has its own user-visible value, validation, and safe merge order. Keep it together when separating it would leave a knowingly incomplete or unusable state.

Before submission:

- explain the root cause, not only the symptom;
- describe current behavior, resulting behavior, and recovery;
- name dependencies and merge order;
- list tests actually run on the final head;
- disclose skipped gates, unsupported cases, memory or compatibility costs, and deferred work;
- update CHANGELOG and user/agent docs for user-visible behavior;
- remove references to inaccessible local paths or unverifiable evidence;
- check that title, body, comments, and commit message still describe the final code after review-driven rescoping.

Never cite `/workspace/...`, a home directory, a temporary directory, or another machine-local path as public PR evidence. Check the artifact into an appropriate repository location, provide a reproducible command, link an accessible CI artifact, or state the evidence boundary explicitly and narrow the claim.

When incorporating maintainer follow-ups, preserve their authorship and commit bodies. Do not silently rewrite or squash someone else’s work. State which upstream commits were adopted, re-run the relevant gates on the composed tree, and update the PR description. “Allow edits from maintainers” can simplify collaboration, but it does not replace reviewing the resulting diff.

## Pre-submission audit prompt

Copy this prompt into an agent review or use it as a human checklist:

```text
Review this contribution against current upstream main, not only its tip commit.

1. Report merge-base, unique commits, effective main...HEAD diff, prerequisites, duplicate ancestry, overlapping in-flight changes, and whether the final branch composes cleanly.
2. State the user-visible contract before and after. Exercise first run, unchanged rerun, changed input, interruption, restart, pending/committed state, and every documented recovery path that applies.
3. Trace each persistent or machine-readable field and every sibling in the same rewritten document to its authoritative source. Check every materially distinct legacy schema, zero-work resume, failure atomicity, stable-versus-unique identifier semantics, output routing, exit codes, and telemetry scope.
4. For optional optimizations, force admission failure, corruption, resource exhaustion, and unsupported-platform behavior; prove the established correctness path remains available.
5. Map every important claim to a test. Perform a targeted mutation or source-hunk revert and show the test fails for the intended reason. Include real HTTP/CLI and end-to-end coverage where ordering or recovery matters.
6. Audit tests for clocks, disk, file-descriptor limits, build profile, process-global state, scheduling, environment variables, external assets, and parallel execution.
7. Confirm every feature-gated path is compiled, tested, and linted in an applicable CI job without deleting or weakening existing workflow coverage. For identities over mutable assets, prove the identity and execution use the same immutable byte/config snapshot and that the snapshot is released with its owner.
8. Reproduce performance/resource claims with matched builds, fixed inputs, repeated runs, correctness gates, raw evidence, and explicit workload boundaries.
9. Inspect errors and help text for cause, state-change disclosure, exact recovery commands, related help, and agent-readable structure.
10. Exercise ambiguous and equal-best durable-state/schema matches; prove incidental iteration or lexical order cannot silently choose the winner. List findings by severity, every section judged not applicable with a reason, explicit known gaps, and everything not verified. Do not infer completion from green unrelated tests.
11. For every operational document or runnable recipe, execute the ordered success path and at least one negative control; require a non-zero exit with no artifact extracted, installed, published, or served; keep artifact verification and the action it authorizes in one runnable block with no filesystem handoff to a privileged block; rerun each negative control once with the failing block's exit status discarded and once with the next documented block appended, requiring that neither composition reaches an artifact or unsafe/privileged path; exercise lifecycle and recovery; identify path trust boundaries, attacker-precreated paths, and scratch space outside untrusted staging; enumerate completeness sets and exclusions; state which feature, platform, transport, and fallback variants were tested; separately list every unsupported variant; verify every publication copy and the documented mitigation.
```

## Evidence table

Include a table like this in the PR body or review record. Add or remove rows to match the change.

| Claim or invariant | Authoritative source | Test or reproduction | Mutation / negative control | Result on final head | Evidence location | Known gap |
|---|---|---|---|---|---|---|
| Example: refusal happens before mutation | journal, snapshots, remote read-back | real HTTP refusal and recovery test | disable preflight guard | Pass: mutation is detected before writes | repository path or CI job | concurrent refusal not exercised |
| Example: operational recipe fails closed at an untrusted staging boundary | recipe block boundaries, path ownership, publication topology | run the success path and confirm the verifying block also acts on the artifact | as the staging writer, pre-create a digest-derived destination; run the negative control once with the failing block's exit status discarded and once with the next documented block appended | Pass: neither composition extracts, installs, publishes, or serves an artifact or reaches an unsafe/privileged path; recovery succeeds | repository script or CI job | unsupported platforms are enumerated |
|  |  |  |  |  |  |  |

Evidence is useful only when another contributor can inspect or reproduce it. Prefer committed fixtures, scripts, CI jobs, and concise raw outputs over claims that depend on a private workstation path.
