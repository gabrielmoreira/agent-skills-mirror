# runtime/pool

The client for pooled inline execution. The pool itself (warm interpreter
children, the job protocol, backpressure, idle reaping, recycle-after-N) lives
in the `tinyruntime` module, where one implementation serves every language.

What is here is two decisions this core still owns.

## 1. Whether a language pools at all

| Language | Default | Why |
| --- | --- | --- |
| `node` | **on** | Each job runs in its own `worker_thread`: a fresh module graph and fresh globals per job, so reuse is safe. |
| `python` | **off** | Jobs share one interpreter. CPython has no worker-thread equivalent and no safe way to kill a running thread, so reuse leaks `sys.modules`, `os.environ`, logging handlers, and threads across unrelated runs. Opt in with `[runtime_pool.python] enabled = true`. |

`[runtime_pool] enabled = false` is the master switch and reverts every caller to
its legacy per-call spawn, with no behavioural change. Pooling is an optimisation
seam, not a dependency.

## 2. What a failure means for the caller

This is the subtle part, and the reason `PoolRunError` has three variants rather
than being one error type. Each drives different caller behaviour:

| Variant | The job… | The caller must… |
| --- | --- | --- |
| `PreDispatch` | provably never reached a worker | fall back to a per-call spawn (safe, because nothing ran) |
| `PostDispatch` | reached a worker and **may have executed** | **not** retry, or it risks running someone's code twice |
| `Saturated` | was shed because the pool was full | **not** spawn: that reintroduces exactly the resident memory the pool caps, so report busy or retry later |

`classify` maps the module's failures onto these. The default is `PreDispatch`,
and the asymmetry is deliberate: mistakenly treating a job as un-run costs one
extra fallback spawn, while mistakenly treating a run job as un-run duplicates
its side effects. Only the two signals the module states explicitly, capacity
and post-dispatch, move a failure out of the default.

## Key files

| File | Role |
| --- | --- |
| [`mod.rs`](./mod.rs) | `PoolRunError`, the shared `run_inline` dispatch, and `classify`. |
| [`node.rs`](./node.rs) / [`python.rs`](./python.rs) | Per-language `enabled()` and `run_inline()`; they differ only in which language they name. |
| [`types.rs`](./types.rs) | `PoolExecOutcome` (with `queue_wait` kept apart from `elapsed`), `PoolLang`, `PoolSettings`. |

## Why it exists

At the target deployment density (100-1000 live agents on a 2 GB, 2 vCPU box),
a fresh interpreter child per run is the biggest memory cost: one JS skill
step spawns a `node` child at roughly 72-75 MB RSS. A small, bounded pool of
warm workers turns "K concurrent skill runs, K interpreters" into "K
concurrent skill runs, about one pooled worker", at the cost of queueing work
beyond the pool size. This is one piece of the density work described in
[performance.md](../../../../../gitbooks/developing/performance.md).

## Defaults (`[runtime_pool]`, `config/schema/runtime_pool.rs`)

| Setting | Default | Meaning |
| --- | --- | --- |
| `max_workers` | 2 | concurrently resident workers per language; clamped to at least 1 |
| `idle_ttl_secs` | 60 | reap a worker idle this long; `0` disables idle reaping |
| `recycle_after_jobs` | 100 | retire a worker after this many jobs; `0` disables recycling |
| `max_queue_depth` | 256 | jobs allowed to queue before new submissions are rejected; clamped to at least 1 |

Node pools by default (`worker_thread` isolation makes reuse safe); Python
does not (CPython has no safe way to kill a running thread, so reuse can leak
state across jobs). Set `enabled` explicitly per language to override.

## Notes

- **`queue_wait` is reported separately from `elapsed` on purpose.** A host that
  cannot tell a slow job from a busy pool will tune the wrong knob.
- **A worker is still a child of this process.** A TinyBus module is a `cdylib`
  loaded in-process, so the resident cost and the process-tree shape the
  `library-profile skill-run` gate asserts on are unchanged by the move.

## Further reading

- [Parent module (`runtime`)](../README.md)
- [tinyruntime submodule](../../../../../vendor/tinyruntime/README.md)
- [System and utilities tools](../../../../../gitbooks/features/native-tools/system-and-utilities.md)
- [Loadable modules](../../../../../gitbooks/developing/loadable-modules.md)
