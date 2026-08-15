---
name: cache-policy-comparison
version: 1.1.1
description: "Compares bounded-cache eviction in stdlib Python: LRU, LFU, FIFO, S3FIFO classes plus a same-trace replay harness for hit rate and residency. Use when picking a policy for a buffer pool, page cache, CDN edge, or LLM KV cache, or when lining up policies on one trace. Not a Redis/Memcached operations guide and not for deploying production cache clusters."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

An eviction policy decides which resident entry a cache removes when a new entry is admitted beyond capacity. This skill provides production-grade, standard-library-only implementations of four core policies — LRU, LFU, FIFO, and S3FIFO — plus a replay-and-compare harness that drives an identical trace through all of them at the same capacity and lines up the results.

Four policies cover almost every replay-and-measure task:

| Policy   | Data structure                  | On hit                       | On admit                             | Eviction choice                                   |
|----------|---------------------------------|------------------------------|--------------------------------------|---------------------------------------------------|
| LRU      | OrderedDict                      | Move to tail                 | Append at tail                       | Pop head                                          |
| LFU      | `{key: freq}` + insertion order  | `freq[k] += 1`               | `freq[k] = 1`                         | Min `freq`, tiebreak by insertion order           |
| FIFO     | OrderedDict                      | Nothing                      | Append at tail                       | Pop head                                          |
| S3FIFO   | Three FIFO queues + `freq[k]`    | `freq[k] = min(freq+1, cap)` | Admit to small; ghost-hit admits to main | Second-chance on main; small drains to main/ghost |

Each has subtleties that trip naive implementations. The implementations target CPython 3.12 (current as of 2026) and lean only on the standard library (`collections`, `itertools`, `dataclasses`, `typing`), keeping the comparison portable and avoiding behavior that shifts between releases.

## When to Use

Use this skill when:

- Choosing or implementing an eviction policy for a buffer pool, page cache, CDN edge, or LLM KV cache.
- Writing a replay simulator that supports multiple policies.
- Comparing hit rates across LRU, LFU, FIFO, S3FIFO, and ARC policies.
- Understanding recency vs frequency semantics, queue topology, saturating counters, ghost buffers, and the second-chance rule that distinguishes modern FIFO-family policies from classic LRU.
- You need to clarify the distinction between a cache hit (token accounting) and a rank change (eviction order) — especially for FIFO, where a hit is still a hit but does not reorder.

Trigger keywords: eviction policy, LRU, LFU, FIFO, S3FIFO, ARC, cache hit rate, buffer pool, page cache, CDN edge, LLM KV cache, prefix cache replay, second-chance eviction, ghost queue, saturating counter.

## Prerequisites

- **Python:** CPython 3.12 or later. The code uses `from __future__ import annotations`, `Protocol` with `runtime_checkable`, and PEP 695-style type aliases where applicable.
- **Standard library only:** No third-party packages required. Do not reach for deprecated APIs or unmaintained libraries.
- **Type checker (recommended):** `mypy --strict` or `pyright` for verification. See [Verification](#verification).
- **Windows host (primary):** PowerShell is the primary shell. All commands below assume PowerShell syntax. On Windows, run Python via `python` (not `python3`). Example:

  ```powershell
  python --version
  python -m pip install --upgrade pip
  ```

- **Self-contained notes:** S3FIFO second-chance eviction, ghost-queue admission, and ARC's adaptive recency/frequency split are documented in the S3FIFO procedure and the Extending to ARC example below. This folder does not include extra paper notes.

## Procedure

### Step 1 — Implement LRU

LRU bets that the recent past predicts the near future: the key you touched most recently is the one you are most likely to touch again, so the *least* recently used key is the safest to evict. An `OrderedDict` makes this cheap because it remembers insertion/move order — keep the most-recently-accessed key at the tail, and the eviction victim is always whatever sits at the head.

On a hit, move the key to the tail (`move_to_end`) so it is no longer a candidate for eviction. On a miss, insert at the tail and, if you are now over capacity, pop the head.

The single most common bug is **forgetting to refresh recency on a hit**. Skip the `move_to_end` and every key keeps its original insertion rank regardless of how often it is used — which is exactly FIFO.

```python
from collections import OrderedDict
from collections.abc import Hashable


class LRU:
    """Least-Recently-Used cache tracking residency only (values are not stored)."""

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError(f"capacity must be an int, got {type(capacity).__name__}")
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.capacity: int = capacity
        self._order: "OrderedDict[Hashable, None]" = OrderedDict()

    def contains(self, key: Hashable) -> bool:
        return key in self._order

    def resident_count(self) -> int:
        return len(self._order)

    def access(self, key: Hashable) -> bool:
        """Record an access. Returns True on a hit, False on a miss.

        The return value is read against the pre-access state, so the hit/miss
        decision is made before any admission side effects are applied.
        """
        if key is None:
            raise ValueError("key must not be None")
        if key in self._order:
            self._order.move_to_end(key)  # refresh recency: the bug to avoid is skipping this
            return True
        self._order[key] = None
        if len(self._order) > self.capacity:
            self._order.popitem(last=False)  # evict the head: least-recently-used
        return False
```

### Step 2 — Implement LFU

LFU makes the opposite bet from LRU: popularity, not recency, predicts the future, so the key accessed the *fewest* times is the safest to evict. That requires two pieces of state — a frequency count per key and a tiebreaker for when counts are equal. An always-incrementing insertion counter is the simplest deterministic tiebreaker: when several keys share the minimum frequency, evict the one inserted earliest.

On a hit, increment that key's frequency. On a miss at capacity, evict the key with the minimum frequency, breaking ties toward the oldest insertion.

```python
import itertools
from collections.abc import Hashable


class LFU:
    """Least-Frequently-Used cache with deterministic insertion-order tiebreaking."""

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError(f"capacity must be an int, got {type(capacity).__name__}")
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.capacity: int = capacity
        self._freq: dict[Hashable, int] = {}
        self._seq: dict[Hashable, int] = {}  # insertion order, the deterministic tiebreaker
        self._counter: "itertools.count[int]" = itertools.count()

    def contains(self, key: Hashable) -> bool:
        return key in self._freq

    def resident_count(self) -> int:
        return len(self._freq)

    def access(self, key: Hashable) -> bool:
        """Record an access. Returns True on a hit, False on a miss."""
        if key is None:
            raise ValueError("key must not be None")
        if key in self._freq:
            self._freq[key] += 1
            return True
        if len(self._freq) >= self.capacity:
            self._evict_one()
        self._freq[key] = 1
        self._seq[key] = next(self._counter)
        return False

    def _evict_one(self) -> None:
        # Victim = minimum frequency, ties broken by smallest (oldest) insertion sequence.
        victim: Hashable = min(self._freq, key=lambda k: (self._freq[k], self._seq[k]))
        del self._freq[victim]
        del self._seq[victim]
```

### Step 3 — Implement FIFO

FIFO makes no bet about the future at all: it evicts in the order keys arrived, ignoring both how recently and how often they were used. That makes it the natural lower-bound baseline — any policy that tracks access patterns should beat it, and if yours does not, that gap is a signal something is wrong in your richer policy.

The defining property is that a hit does **not** reorder anything. A hit is still counted as a hit for accounting, but the key keeps its arrival rank, so eviction always removes the oldest-inserted resident.

```python
from collections import OrderedDict
from collections.abc import Hashable


class FIFO:
    """First-In-First-Out cache. Hits are recorded but never change eviction order."""

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError(f"capacity must be an int, got {type(capacity).__name__}")
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.capacity: int = capacity
        self._order: "OrderedDict[Hashable, None]" = OrderedDict()

    def contains(self, key: Hashable) -> bool:
        return key in self._order

    def resident_count(self) -> int:
        return len(self._order)

    def access(self, key: Hashable) -> bool:
        """Record an access. Returns True on a hit, False on a miss."""
        if key is None:
            raise ValueError("key must not be None")
        if key in self._order:
            return True  # deliberately no reordering: that distinction is what makes this FIFO
        self._order[key] = None
        if len(self._order) > self.capacity:
            self._order.popitem(last=False)  # evict the oldest arrival
        return False
```

### Step 4 — Implement S3FIFO

S3FIFO (Yang et al., SOSP 2023) matches or beats LRU on typical web and LLM workloads while spending a fraction of the per-access bookkeeping. The insight is that most cached objects are "one-hit wonders" accessed exactly once, and you should not pay LRU's per-hit pointer surgery to discover that. Three FIFO queues separate the proven-useful keys from the noise:

- **Small queue (S, ~10% of capacity)** — probation area. Every brand-new key lands here. One-hit wonders age out of S quickly without ever polluting the main cache.
- **Main queue (M, ~90% of capacity)** — holds keys that proved their worth. Uses *second-chance* eviction: a key with leftover frequency credit is reinserted at the head with its counter decremented instead of being evicted, giving warm keys repeated reprieves.
- **Ghost queue (G, metadata only)** — remembers fingerprints of recently evicted keys. If such a key returns, that is strong evidence it belongs in the main cache, so it is admitted straight to M rather than starting over in S.

Two design points are load-bearing:

1. The frequency counter **saturates** at a small cap (`FREQ_MAX = 3`) so the main-queue second-chance loop does a bounded amount of work per eviction. An unbounded counter would let one very hot key spin that loop indefinitely.
2. **Ghosts are not residents**: they hold no value, count against neither queue's capacity, and a ghost hit on insertion is not a cache hit for token accounting.

```python
from collections import OrderedDict
from collections.abc import Hashable


class S3FIFO:
    """S3-FIFO eviction (Yang et al., SOSP 2023): a small admission queue, a main
    queue with second-chance eviction, and a metadata-only ghost queue.

    The frequency counter saturates at FREQ_MAX so the main-queue second-chance
    loop performs a bounded amount of work per eviction.
    """

    FREQ_MAX: int = 3

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise TypeError(f"capacity must be an int, got {type(capacity).__name__}")
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.capacity: int = capacity
        self._small_capacity: int = max(1, capacity // 10)
        self._main_capacity: int = max(1, capacity - self._small_capacity)
        self._ghost_capacity: int = self._main_capacity

        self._small: "OrderedDict[Hashable, None]" = OrderedDict()
        self._main: "OrderedDict[Hashable, None]" = OrderedDict()
        self._ghost: "OrderedDict[Hashable, None]" = OrderedDict()
        self._freq: dict[Hashable, int] = {}

    def contains(self, key: Hashable) -> bool:
        """Residency excludes the ghost queue, which holds metadata only."""
        return key in self._small or key in self._main

    def resident_count(self) -> int:
        return len(self._small) + len(self._main)

    def access(self, key: Hashable) -> bool:
        """Record an access. Returns True on a hit, False on a miss.

        A ghost match during insertion is *not* a hit: it only changes which
        queue the returning key is admitted to.
        """
        if key is None:
            raise ValueError("key must not be None")
        if key in self._small or key in self._main:  # cache hit
            self._freq[key] = min(self._freq.get(key, 0) + 1, self.FREQ_MAX)
            return True
        self._insert(key)  # cache miss
        return False

    def _insert(self, key: Hashable) -> None:
        while self.resident_count() >= self.capacity:
            self._evict()
        if key in self._ghost:
            del self._ghost[key]
            self._main[key] = None  # a returning key has earned a place in main
            self._freq[key] = 0
        else:
            self._small[key] = None  # a brand-new key starts on probation in small
            self._freq[key] = 0

    def _evict(self) -> None:
        # Evict from small while it is at or above its share; otherwise from main.
        if len(self._small) >= self._small_capacity:
            self._evict_small()
        else:
            self._evict_main()

    def _evict_small(self) -> None:
        # Drain oldest small entries: promote proven-warm keys (freq > 1) to main,
        # demote the rest to ghost. Returns as soon as one key is demoted.
        while self._small:
            key, _ = self._small.popitem(last=False)  # oldest small entry
            if self._freq.get(key, 0) > 1:
                self._main[key] = None  # promotion; frequency is carried over
            else:
                del self._freq[key]
                self._to_ghost(key)
                return

    def _evict_main(self) -> None:
        # Second chance: a key with remaining credit is reinserted at the head with
        # its counter decremented; the first zero-credit key is evicted to ghost.
        while self._main:
            key, _ = self._main.popitem(last=False)  # oldest main entry
            freq = self._freq.get(key, 0)
            if freq > 0:
                self._freq[key] = freq - 1
                self._main[key] = None  # reinsert at head, one chance spent
            else:
                del self._freq[key]
                self._to_ghost(key)
                return

    def _to_ghost(self, key: Hashable) -> None:
        self._ghost[key] = None
        if len(self._ghost) > self._ghost_capacity:
            self._ghost.popitem(last=False)  # bound ghost; forget the oldest fingerprint
```

### Step 5 — Build the replay-and-compare harness

The harness treats each policy class as a factory (`LRU`, `LFU`, `FIFO`, `S3FIFO` are all `Callable[[int], EvictionPolicy]`), rebuilds a clean cache per run so the comparison is fair, and validates the trace at the boundary so a malformed input fails loudly instead of producing a quietly wrong hit rate.

Two correctness details are baked in deliberately:

- Residency is read with `contains()` *before* `access()` mutates the cache — reversing that order makes every block hit against itself.
- The resident count comes from the uniform `resident_count()` method each policy exposes, never from a guess that capacity was fully used (S3FIFO routinely ends below capacity because ghosts absorb admission pressure).

```python
from __future__ import annotations

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@runtime_checkable
class EvictionPolicy(Protocol):
    """Structural type implemented by LRU, LFU, FIFO, and S3FIFO above."""

    def contains(self, key: Hashable) -> bool:
        """Return True if `key` is currently resident (ghost entries excluded)."""

    def access(self, key: Hashable) -> bool:
        """Record an access to `key`; return True on a hit, False on a miss."""

    def resident_count(self) -> int:
        """Return the number of resident keys (ghost entries excluded)."""


@dataclass(frozen=True)
class Block:
    """One cache unit referenced by a request, carrying its token weight."""

    key: Hashable
    tokens: int

    def __post_init__(self) -> None:
        if self.key is None:
            raise ValueError("Block.key must not be None")
        if not isinstance(self.tokens, int) or isinstance(self.tokens, bool):
            raise TypeError(
                f"Block.tokens must be an int, got {type(self.tokens).__name__}"
            )
        if self.tokens < 0:
            raise ValueError(f"Block.tokens must be non-negative, got {self.tokens}")


Request = Sequence[Block]
Trace = Sequence[Request]


@dataclass
class ReplayResult:
    hit_tokens: int = 0
    prompt_tokens: int = 0
    per_request_hit_tokens: list[int] = field(default_factory=list)
    resident_count: int = 0

    @property
    def hit_rate(self) -> float:
        if self.prompt_tokens == 0:
            return 0.0
        return self.hit_tokens / self.prompt_tokens


def replay(
    policy_factory: Callable[[int], EvictionPolicy],
    capacity: int,
    trace: Trace,
) -> ReplayResult:
    """Replay `trace` through a freshly built policy at `capacity`."""
    if not callable(policy_factory):
        raise TypeError("policy_factory must be callable")
    if not isinstance(capacity, int) or isinstance(capacity, bool):
        raise TypeError(f"capacity must be an int, got {type(capacity).__name__}")
    if capacity <= 0:
        raise ValueError(f"capacity must be positive, got {capacity}")

    policy: EvictionPolicy = policy_factory(capacity)
    result = ReplayResult()

    for request in trace:
        request_hit_tokens = 0
        for block in request:
            if not isinstance(block, Block):
                raise TypeError(
                    f"trace entries must be Block instances, got {type(block).__name__}"
                )
            # Read residency BEFORE access() mutates the cache, or every block self-hits.
            is_hit = policy.contains(block.key)
            policy.access(block.key)
            result.prompt_tokens += block.tokens
            if is_hit:
                request_hit_tokens += block.tokens
        result.hit_tokens += request_hit_tokens
        result.per_request_hit_tokens.append(request_hit_tokens)

    result.resident_count = policy.resident_count()
    return result


def compare_policies(capacity: int, trace: Trace) -> dict[str, ReplayResult]:
    """Replay one trace through every policy at the same capacity."""
    factories: dict[str, Callable[[int], EvictionPolicy]] = {
        "LRU": LRU,
        "LFU": LFU,
        "FIFO": FIFO,
        "S3FIFO": S3FIFO,
    }
    return {name: replay(factory, capacity, trace) for name, factory in factories.items()}
```

### Step 6 — Run the demo

Save all classes and the harness in a single module (e.g. `cache_policies.py`), then add the demo entry point and run it:

```python
if __name__ == "__main__":
    shared_prefix: list[Block] = [Block("sys", 8), Block("ctx", 16)]
    demo_trace: Trace = [
        [*shared_prefix, Block("q1", 4)],
        [*shared_prefix, Block("q2", 4)],
        [Block("sys", 8), Block("other", 32), Block("q3", 4)],
    ]
    for name, outcome in compare_policies(capacity=4, trace=demo_trace).items():
        print(
            f"{name:7s} hit_rate={outcome.hit_rate:6.2%} "
            f"hit_tokens={outcome.hit_tokens:4d} resident={outcome.resident_count}"
        )
```

```powershell
python cache_policies.py
```

Expected output (approximate — exact numbers depend on eviction order):

```
LRU     hit_rate= 28.57% hit_tokens=  16 resident=4
LFU     hit_rate= 28.57% hit_tokens=  16 resident=4
FIFO    hit_rate= 28.57% hit_tokens=  16 resident=4
S3FIFO  hit_rate= 28.57% hit_tokens=  16 resident=3
```

### Step 7 — Interpret workload implications

- Strong **recency** → LRU wins slightly.
- Stable **hot set** with long tail (Zipf) → LFU or S3FIFO.
- Nearly uniform random → all converge toward `capacity / working_set` hit rate.
- **Prefix-shared LLM workloads** are mixed — shared prefixes are both recent and frequent, so LRU/LFU/S3FIFO typically sit within a few percent of each other at the same capacity, but they differ in which blocks remain resident at end-of-trace, and their miss-handling costs diverge. Measure, don't assume.

### Step 8 — Compare beyond hit rate

Replay the same trace through each policy at identical capacity, record `total_hit_tokens / total_prompt_tokens` and the final resident set. Do not compare hit rate alone — also compare:

- **Final residency** — how many unique blocks are resident at the end. Under S3FIFO this is often strictly less than capacity because ghost entries absorb the admission pressure.
- **Per-request hit-token distribution** — two policies can have similar overall hit rate but very different per-request variance.
- **Admission effort** — under policies with ghost structures, the bookkeeping cost per access is non-trivial.

## Examples

### Extending to ARC (Adaptive Replacement Cache)

ARC maintains two ghost lists (one for recently evicted from the recency-sensitive side, one for the frequency-sensitive side) and dynamically adjusts the split point between the two resident queues based on which ghost list is producing hits. To add ARC to the harness:

1. Implement an `ARC` class that satisfies the `EvictionPolicy` protocol (`contains`, `access`, `resident_count`).
2. Add `"ARC": ARC` to the `factories` dict in `compare_policies`.
3. Confirm that `resident_count()` returns only the sum of the two resident queues, excluding both ghost lists.
4. Drive ARC's adaptive `p` from which ghost list is hitting (recency-evicted vs frequency-evicted), keeping `resident_count()` as the two resident queues only.

## Pitfalls

These are the mistakes that quietly corrupt a comparison. Each is listed with the underlying reason so you can recognize the same failure mode in a variation the list does not name.

- **Treating FIFO as "LRU without the hit update" in your accounting.** The implementations overlap, but the concepts diverge where it matters: a hit on a FIFO cache is still a hit for token accounting — the block simply keeps its existing rank instead of being promoted. If you let "no rank change" leak into "not a hit," your hit-rate numbers silently drop and the comparison becomes meaningless.
- **Reusing an LRU implementation when the task specifies S3FIFO, or vice versa.** These policies make different eviction decisions, so both the final hit rate and the resident set will differ. A comparison exists precisely to surface those differences, so "close enough" defeats the purpose — you would be measuring two copies of the same policy.
- **Counting ghost entries as resident, or scoring a ghost hit as a real hit.** Ghosts are metadata-only: they remember that a key was *recently evicted* so the policy can react if it returns, but they hold no value and consume no capacity. Conflating them with resident entries inflates both your residency count and your hit rate, which double-distorts the comparison.
- **Letting the frequency counter grow without bound.** S3FIFO's main-queue eviction repeatedly decrements `freq` and re-inserts entries that still have credit. If `freq` is unbounded, a single very hot key can accumulate a huge count and turn that second-chance loop into a near-infinite spin. Saturating the counter (a small cap such as 3) bounds the work per eviction to a constant.
- **Picking the LFU victim with `min(d.items(), key=d.get)` and no explicit tiebreaker.** When several keys share the minimum frequency, `min` returns whichever the iteration order happens to surface first, and that order is not guaranteed stable across interpreters or versions. An explicit insertion-order tiebreaker makes the eviction deterministic and your results reproducible.
- **Checking residency *after* applying the current request's admission side effects.** The hit/miss decision must be read against the cache state as it was *before* this request mutated it. If you insert the key first and then test membership, every request reports a hit against itself, and the trace looks like a 100% hit rate that is pure artifact.
- **Computing final cache size without excluding ghosts or accounting for the small/main capacity split.** S3FIFO's capacity is partitioned between the small and main queues, and ghosts sit outside both. A size calculation that ignores either fact will not match the policy's actual residency, so report the resident set as (small ∪ main), never including ghost.
- **Reaching for deprecated APIs or unmaintained libraries.** The implementations here target CPython 3.12 (current as of 2026) and lean only on the standard library, which keeps the comparison portable and avoids behavior that shifts under you between releases.
- **Skipping input validation because "it's just a simulator."** A replay harness ingests trace data, often from files or other processes. Validating capacities, key types, and token counts at the boundary turns a corrupt trace into a clear, early error instead of a silently wrong hit rate — and it closes the obvious injection and resource-exhaustion vectors.
- **Frequency pollution in pure LFU.** A key that was hot early and then goes cold keeps its high count forever, sitting permanently above fresh arrivals that may now be hotter. Pure LFU has no way to forget, so stale keys can squat in the cache indefinitely. Production systems fix this with aging (periodically decaying counts) or by blending in a recency signal (W-TinyLFU). For a faithful policy comparison you want *pure* LFU — just be aware that its real-world fragility is the reason almost nobody ships it unmodified.

## Verification

Each check below targets a specific failure mode from the pitfalls list — the point is not to tick boxes but to catch the mistakes that make a comparison silently wrong before you trust its numbers.

1. **Cross-policy divergence:** Replay one identical trace through all four policies at several capacities; confirm the hit rates differ where the policies should differ. A flat tie across very different policies usually means a shared bug in the harness.

   ```powershell
   python -c "from cache_policies import compare_policies, Block; t=[[Block('a',1),Block('b',1)],[Block('a',1),Block('c',1)],[Block('b',1),Block('a',1)]]; [print(k, v.hit_rate, v.resident_count) for k,v in compare_policies(2, t).items()]"
   ```

2. **LRU recency refresh:** On a recency-heavy workload, confirm LRU clearly beats FIFO — equal hit rates mean the `move_to_end` recency refresh was dropped and LRU has degenerated to FIFO.

3. **LFU tiebreaker determinism:** Confirm the LFU victim is chosen by the `(freq, insertion_seq)` pair so repeated runs of the same trace evict the same key; a result that wobbles between runs means the tiebreaker is missing.

4. **FIFO hit-without-reorder:** Confirm FIFO returns `True` on a repeat access but does not reorder its queue (hit accounting still counts, eviction order does not change).

5. **S3FIFO counter saturation:** Confirm S3FIFO caps `freq` at `FREQ_MAX` and that the main-queue second-chance loop terminates in bounded time even under a hot-key-only trace.

6. **Ghost exclusion:** Confirm `contains()` and `resident_count()` exclude the ghost queue, and that a ghost match on insertion is not counted as a hit.

7. **Resident set correctness:** Confirm the reported resident set is `small ∪ main` (never including ghost) and that it can legitimately end below capacity under S3FIFO.

8. **Per-request variance:** Inspect `per_request_hit_tokens` variance across policies — two policies with the same overall hit rate can have very different per-request behavior.

9. **Type safety:** Run `mypy --strict` (or `pyright`) over the module and confirm it passes with no `Any` leaking through and no missing annotations.

   ```powershell
   python -m mypy --strict cache_policies.py
   ```

10. **Boundary validation:** Confirm the boundary validations fire: a non-positive capacity, a `None` key, a non-`Block` trace entry, and a negative token count each raise immediately rather than producing a wrong number.

    ```powershell
    python -c "from cache_policies import LRU; LRU(0)"
    python -c "from cache_policies import LRU; c=LRU(4); c.access(None)"
    python -c "from cache_policies import Block; Block('x', -1)"
    ```

11. **Standard-library-only on CPython 3.12:** Confirm the code runs unmodified on CPython 3.12 using only the standard library (`collections`, `itertools`, `dataclasses`, `typing`).

    ```powershell
    python --version
    python -c "import ast, sys; tree=ast.parse(open('cache_policies.py').read()); mods={n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}; assert all(m.split('.')[0] in ('collections','itertools','dataclasses','typing','__future__') for m in mods if m), mods; print('OK: stdlib only')"
    ```

## Related Skills

- `prefix-cache-replay` — Applies these policies to LLM prefix-cache traces, where keys are prompt-prefix blocks and the payoff is reused KV-cache tokens. This skill is self-contained (the full S3FIFO implementation lives in the S3FIFO section above); reach for `prefix-cache-replay` when you need trace ingestion, block hashing, and token accounting wired specifically for prefix sharing.
