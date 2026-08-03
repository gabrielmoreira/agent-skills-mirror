# Harness Home Guardrail

Harness Home is the framework-neutral, user-owned source of truth for portable identity, Memory, Skills, MCP descriptors, creative methods and references to durable Assets. Read this file before changing `src/lib/harness-home/**`, adding a Harness adapter, or wiring canonical data into a Runtime.

## 1. 词汇表

| 词汇 | 含义 |
|------|------|
| Canonical repository | User-owned file root containing `manifest.json` and referenced content. SQLite is never the only copy. |
| Manifest generation | Monotonic integer committed after all content files; readers use it as the visible transaction boundary. |
| HarnessAdapter | L0/L1 discovery/import/export/projection for an external Harness; it does not implement chat execution. |
| RuntimeAdapter | L2/L3 execution integration for session, stream, permission, artifact and interrupt. |
| Runtime overlay | Opaque Runtime-specific data preserved separately from canonical shared content. |
| SecretRef | Portable `secret://` identity. It never contains a resolved value. |
| Writer lease | Single-writer lock for one canonical realpath. |
| Prepared journal | Durable intent plus staged bytes used to resume a partial multi-file transaction. |
| Reference status | `pending`, `executable` or `rejected`; a stable canonical capability must be executable in CodePilot. |
| Runtime registration | Compile-time descriptor that owns wire ID, display metadata, packaged driver, exposure key and projection modes. It is not a dynamic JS plugin. |
| Definition descriptor | Canonical Skill/MCP metadata. Discovery makes it perceptible; only a Runtime-owned mounter may prove it executable. |

## 2. 不变量 / 契约表

| # | Contract |
|---|----------|
| 1 | Core contracts contain no external-framework home paths and no fixed Runtime record keys. Runtime/framework IDs are opaque strings validated by registries. |
| 2 | Unknown manifest fields and Runtime overlays round-trip without loss. Unknown executable behavior still fails closed. |
| 3 | `stable` canonical capability implies `referenceStatus=executable`. Draft/pending capability cannot enter stable Settings coverage or executable model context. |
| 4 | Manifest and canonical repository writes reject inline Secret material. Diagnostics/export contain only SecretRef and availability metadata. |
| 5 | A realpath has at most one writer. A second live/unverifiable instance becomes read-only or fails. Startup may reclaim the exact observed holder only when its opaque machine identity matches and the OS proves its PID is dead; another/unknown machine always fails closed. Manual takeover additionally requires explicit confirmation and the same-machine proof. |
| 6 | Multi-file write order is staging → fsynced prepared journal → content atomic rename → manifest atomic rename → fsynced committed journal. Manifest is always last. Journal discovery isolates each transaction directory; missing-journal remnants cannot hide valid siblings, and any recovery failure releases the writer lease. |
| 7 | `fs.watch` is a hint only. Open/focus/pre-write/explicit refresh must use generation and content hashes. External edits never become silent last-write-wins. |
| 8 | Existing path components may not be symlinks. Repository-relative refs may not be absolute, contain `..`, or target `.harness-home`. |
| 9 | Migration is dry-run first, copy-only, idempotent and conflict-aware. It does not delete or rewrite the external source. |
| 10 | New L0/L1 framework work defaults to its adapter directory, one registry entry and conformance fixtures. Context Compiler, Settings coverage and Artifact renderer are outside the allowed boundary. |
| 11 | Runtime overlays may override projection for the active Runtime but never overwrite the canonical base definition/state. |
| 12 | Creative Method and durable Taste Memory require evidence. A durable user preference requires explicit confirmation and remains revocable. |
| 13 | Runtime wire IDs, Settings labels, capability rows and packaged drivers derive from the explicit Runtime catalog. Unknown IDs fail closed; a missing packaged driver fails startup. |
| 14 | Canonical projection reads exactly one hash-consistent generation. Missing provenance, external edits, oversized context or Secret material abort projection before prompt assembly. |
| 15 | Canonical Skill/MCP definitions are catalogued as perception-only until a Runtime-specific mounter proves a real executable wire. Their bodies are not injected as fake tools. |
| 16 | Runtime switching is read-only with respect to canonical files. It may select a matching overlay but cannot rewrite the base manifest or external Harness source. |
| 17 | Canonical core files remain product/framework neutral. Product Runtime identities and integration imports belong only in adapter/runtime/product binding files; the recursive canonical boundary guard is a required test and pre-commit gate. |
| 18 | A read-only consistency check may cache hashes only behind stat identity (`dev/ino/size/mtimeNs/ctimeNs`) and a bounded generation cache. Any stat change, symlink, out-of-root path or journal mismatch forces revalidation/fail-closed; no cache may hide an external edit. |
| 19 | Invalid persisted Taste Memory is isolated per record and returned as metadata diagnostics; it cannot block valid Taste projection. Import validates Taste evidence before commit, while update/revoke of the same invalid identity fails closed until repaired. |
| 20 | Creative Method trigger/non-trigger phrases are bounded, non-empty after trim and free of control characters. Write, import and historical read all fail closed; an empty phrase can never activate or suppress every prompt. |

## 3. 关键文件 + 责任

| File | Responsibility |
|------|----------------|
| `src/lib/harness-home/contracts.ts` | Portable schema, scope, provenance, capability, Method and Taste evidence shapes |
| `manifest.ts` | Known-field validation, unknown-field preservation and manifest Secret gate |
| `scope.ts` | Built-in → user → assistant → project → matching Runtime overlay order |
| `validation.ts` | Secret scan, Full Reference rule and evidence validation |
| `repository/file-repository.ts` | Repository identity, generation check, consistency diagnostics and commit orchestration |
| `repository/writer-lease.ts` | Single-writer ownership and explicit dead-holder takeover |
| `repository/transaction.ts` | Prepared/committed/orphaned journal and crash recovery |
| `migration.ts` | Dry-run/apply, idempotency and same-name/different-content conflicts |
| `secret-store.ts` | Value-free metadata plus explicit resolve/mutate facade |
| `codepilot-secret-store.ts` | Compatibility resolver over v0.62 Settings/Provider/env/external-owned stores |
| `registry.ts` | Open descriptor registries for Harness and Runtime adapters |
| `src/lib/runtime/runtime-catalog.ts` | Built-in Runtime registration, display/driver/exposure metadata and packaged-driver gate |
| `runtime/descriptor.ts` | Descriptor-derived capability declarations and CodePilot Full Reference assertion |
| `runtime/repository-projection.ts` | Consistent canonical generation → Runtime projection and prompt fragment |
| `runtime/definitions.ts` | Canonical-first Skill/MCP create/update with expected-hash conflict protection |
| `runtime/configured.ts` | Read-only configured-root resolution and value-free Secret diagnostics |
| `src/app/api/harness-home/**` | Metadata-only diagnostics, configure/unconfigure and canonical definition write boundary |
| `src/lib/harness/runtime-adapter.ts` | Injects a validated canonical projection into all three Runtime facades |

## 4. 改动检查表

- [ ] Contract change preserves unknown fields and overlays.
- [ ] New field has a portable meaning and does not expose a local absolute path or Secret.
- [ ] Repository write verifies current manifest hash/generation and every referenced content hash.
- [ ] New transaction path keeps manifest last and recovery idempotent.
- [ ] New credential namespace declares resolve, mutation, reauthorization and cleanup semantics.
- [ ] New L0/L1 adapter passes the shared conformance suite and does not modify forbidden touchpoints.
- [ ] Canonical files pass `npm run test:harness-boundary`; product/framework identity remains in the declared integration layer.
- [ ] New Runtime descriptor keeps unsupported capabilities explicit and passes permission/event conformance.
- [ ] New Runtime registration includes a real packaged driver and keeps DB/HTTP wire validation fail-closed.
- [ ] Canonical projection includes source provenance and does not expose Memory/identity bodies through diagnostics.
- [ ] Skill/MCP discovery remains perception-only until a conformance-tested mounter is passed explicitly.
- [ ] New Asset kind is producer-backed and is registered in Program B, not added as a speculative enum here.
- [ ] New Taste/Method persistence includes evidence, scope and revoke behavior.
- [ ] Taste readers isolate legacy/import poison per record and keep a visible diagnostic breadcrumb.
- [ ] Lease recovery proves the holder is on the same machine before probing its PID; portable roots never infer cross-machine death from a local PID miss.
- [ ] Method activation phrases pass the same non-empty/length/control-character validation on write, import and historical read.
- [ ] Tests use isolated temporary roots; never point at a real user Harness root.

## 5. 常见坑

- Treating a successful `fs.watch` event as proof that an index is current.
- Deleting a lock by age or local PID miss alone. A slow, suspended or cross-machine process may still be the writer; automatic recovery requires an exact same-machine holder whose PID is provably dead.
- Writing the manifest before content and exposing a mixed generation after a crash.
- Resolving a SecretRef for diagnostics and accidentally serializing the returned value.
- Parsing only known Runtime overlays and dropping fields from an uninstalled adapter.
- Calling an L0/L1 scanner a Runtime integration, then branching in Context Compiler and Settings.
- Adding a new product/framework word to a portable provenance value, MIME type, secret namespace or canonical import.
- Rehashing every Harness file on every read-only turn, or caching by pathname/mtime alone and missing an external edit.
- Treating a canonical Skill/MCP file as mounted because it was successfully read.
- Returning canonical section bodies or resolved Secret values from diagnostics.
- Adding a selectable Runtime descriptor without registering its packaged driver.
- Treating a selected image or one-off edit as a permanent user preference.
- Adding `component`, `document` or `html_bundle` before a real materializer/validator/consumer exists.

## 6. 测试覆盖

| Contract | Test |
|----------|------|
| Neutral contract, unknown overlay, scope, Full Reference, SecretRef, Taste evidence | `src/__tests__/unit/harness-home-contract.test.ts` |
| Single writer/read-only fallback/explicit takeover | `src/__tests__/unit/harness-home-repository.test.ts` |
| Dry-run/idempotency/conflict/full portable refs | `harness-home-repository.test.ts` |
| Crash recovery/manifest-last/external edit | `harness-home-repository.test.ts` |
| Symlink boundary and inline Secret rejection | `harness-home-repository.test.ts` |
| SecretStore value-free diagnostics/read-only namespaces | `harness-home-repository.test.ts` |
| Per-adapter L0/L1 behavior | `harness-home-adapter-conformance.test.ts` |
| Runtime registry/wire/packaged driver/Full Reference | `harness-home-runtime-conformance.test.ts` |
| Canonical projection, cross-Runtime read-only injection, stale generation and Secret metadata | `harness-home-runtime-conformance.test.ts` |
| Canonical Skill/MCP create/idempotency/hash conflict/Secret rejection | `harness-home-runtime-conformance.test.ts` |
| Recursive canonical neutrality, nested violation detection and pre-commit wiring | `harness-home-boundary-guard.test.ts` + `npm run test:harness-boundary` |
| Streaming hash, unchanged generation cache hit and external-edit invalidation | `harness-home-repository.test.ts` |
| Fsynced journal, missing-journal sibling isolation and recovery lease release | `harness-home-repository.test.ts` |
| Taste import validation and persisted poison isolation | `harness-home-repository.test.ts` + `harness-home-design-method.test.ts` |
| Same-machine dead lease recovery and cross-machine fail-closed | `harness-home-repository.test.ts` |
| Method trigger/non-trigger write and historical-read validation | `harness-home-design-method.test.ts` |

Required local verification for core/repository changes:

```bash
npm run typecheck
npm run test:harness-boundary
npx eslint src/lib/harness-home src/__tests__/unit/harness-home-*.test.ts
CODEX_DISABLED=1 npx tsx --test --import ./src/__tests__/db-isolation.setup.ts src/__tests__/unit/harness-home-*.test.ts
```

Run full `npm run test` before closing a phase or changing existing Runtime/DB/MCP behavior.

## 7. 设计决策日志

- 2026-07-30 — Harness Home is a domain aggregate, not a required page. UI entry remains a separate product decision.
- 2026-07-30 — User files are canonical; SQLite may index but cannot become the only copy of identity, Memory, Skill or Method.
- 2026-07-30 — Full Reference permits draft/pending catalog entries, while stable capabilities must be executable in CodePilot.
- 2026-07-30 — The write model uses a single writer, same-root staging, durable journal, manifest-last commit, hash reconciliation and explicit dead-holder takeover.
- 2026-07-30 — The initial SecretStore is a compatibility facade over existing v0.62 stores. No silent credential migration or external auth-file read is allowed.
- 2026-07-30 — L0/L1 Harness adapters are separated from L2/L3 Runtime adapters to keep new framework integration bounded.
- 2026-07-30 — Runtime IDs and user-facing metadata derive from one compile-time catalog. The legacy three wire values remain compatible; arbitrary third-party JS loading remains out of scope.
- 2026-07-30 — Canonical identity/rules/Memory/Method context is projected into all three Runtime facades from one consistent generation. Skill/MCP bodies remain perception-only until an executable mounter exists.
- 2026-07-30 — Harness Home Skill/MCP creation writes the canonical repository first. Replacing different bytes requires the caller's expected content hash; external export remains a separate adapter action.
- 2026-07-30 — Harness Home diagnostics are a code/API surface, not a new page. They return root, provenance, conflicts, capability gaps and Secret availability metadata, never canonical content or resolved values.
- 2026-07-31 — Claude review exposed product identity in canonical defaults and the lack of an enforcing recursive boundary. Portable provenance/MIME/secret namespaces are now neutral; `test:harness-boundary` scans nested canonical files and runs in the code pre-commit tier.
- 2026-07-31 — Repository consistency now uses streaming hashes plus a 32-generation stat-backed cache. This removes full-file hashing from unchanged read-only turns while preserving external-edit, symlink and journal fail-closed behavior.
- 2026-07-31 — Journal replacement is file-fsynced and directory-synced where the platform supports it; recovery handles transaction directories independently and releases the lease on every failed open. Taste Memory import validates evidence, while read/projection isolates invalid persisted records with diagnostics instead of poisoning the whole collection.
- 2026-07-31 — Writer leases persist only an opaque hashed machine identity. Dead-holder recovery is limited to the same identity before the local PID probe; legacy leases without identity and synced locks from another machine remain conflicts. Creative Method activation phrases now use one fail-closed validator across write/import/read.
