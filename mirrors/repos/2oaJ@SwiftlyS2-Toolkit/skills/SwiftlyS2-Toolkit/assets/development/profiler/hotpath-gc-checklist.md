# SwiftlyS2 Hot Path / Performance / GC Checklist

Official docs sections:
- `Profiler`
- `Thread Safety`
- `Native Functions and Hooks`

Use this for: hook performance reviews, high-frequency loops, state synchronization, menu callbacks, scheduler periodic tasks, and code audits on main-thread critical paths.

## 1. Decide first whether this code is actually on a hot path

- [ ] Is it inside a high-frequency Hook, RuntimeLoop, bot-control path, or another high-refresh chain?
- [ ] Is it executed repeatedly per tick, per frame, or per player?
- [ ] Does it run on the main thread and directly affect the 64-tick frame budget?

## 2. Allocation and GC risk

- [ ] Does the hot path frequently allocate `new List<>`, `new Dictionary<>`, or `new[]`?
- [ ] Does it repeatedly call `ToList()`, `ToArray()`, `OrderBy()`, `Where()`, or `Select()` inside loops?
- [ ] Does it frequently create `string`, interpolated strings, or `string.Format` results inside loops?
- [ ] Does it create temporary DTOs, anonymous objects, or lambda closures on the hot path?
- [ ] Is there implicit boxing?

## 3. JSON / IO / heavy CPU work

- [ ] Is JSON avoided in Hooks, high-frequency loops, menu callbacks, and scheduler periodic callbacks?
- [ ] Are disk IO, network IO, database queries, compression, regex, and large sorts avoided on hot paths?
- [ ] Have main-thread sampling and background serialization / aggregation been separated?

## 4. Algorithms and complexity

- [ ] Does the hot path repeatedly scan all players or all records in full?
- [ ] Is `O(n)` / `O(n log n)` work incorrectly placed inside a per-player-per-tick path?
- [ ] Could it be changed into producer / consumer form, with the hot path only sampling and background logic aggregating?

## 5. Landing principles

- Ensure correctness before optimizing
- Find real hotspots before optimizing; do not over-micro-optimize low-frequency paths
- Reduce unnecessary allocations first, and only then consider `Span`, `stackalloc`, or more aggressive techniques
