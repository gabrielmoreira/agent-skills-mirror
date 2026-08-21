---
name: workload-balancing
version: 1.1.1
description: "Partitions Python work across ProcessPoolExecutor, asyncio semaphores, work-stealing deques, and LPT weighted bins to cut stragglers and load imbalance. Use for even chunking, dynamic pull queues, or speculative backup tasks on CPU- or I/O-bound pools. Not for single-threaded jobs, hard real-time timing, or Temporal/n8n durable workflows (workflow-automation)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# Workload Balancing Skill

Distribute work efficiently across parallel workers to maximize throughput and minimize completion time. Covers static/dynamic partitioning, work stealing, weighted bin packing, and adaptive load balancing strategies for CPU-bound and I/O-bound workloads.

## When to Use

- Balancing work distribution across parallel workers, processes, or nodes
- Improving parallel execution efficiency and throughput
- Reducing straggler tasks that delay overall completion
- Implementing load balancing strategies (static, dynamic, work stealing)
- Optimizing task scheduling for uniform or variable workloads
- Handling resource constraints (memory-bound, heterogeneous workers, network costs)

## Do Not Use

- Single-threaded or sequential workloads with no parallelism
- Workloads where task overhead exceeds balancing benefits
- Real-time systems with strict deterministic timing requirements
- When tasks have complex interdependencies that prevent parallel execution
- Scenarios where partitioning cost exceeds task execution cost
- **Warning:** Avoid using `multiprocessing.Queue` for extremely high-throughput small tasks due to serialization overhead; use `multiprocessing.shared_memory` or `Ray` for large-scale data.
- **Warning:** Avoid global locks in dynamic scheduling to prevent the "convoy effect" where the scheduler becomes the bottleneck.

## Prerequisites

- Python 3.8+ with `concurrent.futures`, `asyncio`, and `multiprocessing` available in the standard library
- `numpy` installed for array-based static chunking (`pip install numpy`)
- `aiohttp` installed for async I/O semaphore balancing (`pip install aiohttp`)
- On Windows hosts (PowerShell), ensure `if __name__ == "__main__":` guard is present before any `ProcessPoolExecutor` usage — Windows uses spawn-based multiprocessing which re-imports the module
- For large-scale distributed workloads, consider `Ray` (`pip install ray`) as an alternative to `multiprocessing`

## Procedure

### Step 1: Characterize the Workload

Before selecting a strategy, determine:

1. **Task time uniformity** — Are task durations roughly equal or highly variable?
2. **Task count** — Is the total number of tasks known upfront or streaming?
3. **Task size/cost** — Can you estimate per-task cost (bytes, compute units)?
4. **Resource constraints** — Are workers memory-bound, heterogeneous, or network-limited?
5. **Interdependencies** — Can tasks run independently or do they require ordering?

### Step 2: Select Strategy via Decision Tree

```
What's the workload characteristic?

Uniform task times:
├── Known count → Static partitioning (equal chunks)
├── Streaming input → Round-robin distribution
└── Large items → Size-aware partitioning

Variable task times:
├── Predictable variance → Weighted distribution
├── Unpredictable → Dynamic scheduling / work stealing
└── Long-tail distribution → Work stealing + time limits

Resource constraints:
├── Memory-bound workers → Memory-aware assignment
├── Heterogeneous workers → Capability-based routing
└── Network costs → Locality-aware placement
```

### Step 3: Implement the Selected Strategy

#### Strategy 1: Static Chunking (Uniform Workloads)

Best for predictable, similar-sized tasks. Uses `ProcessPoolExecutor` for CPU-bound tasks.

```python
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def process_chunk(chunk):
    return [item * 2 for item in chunk]

def static_balanced_process(items, num_workers=4):
    """Divide work into equal chunks upfront."""
    chunks = np.array_split(items, num_workers)

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_chunk, chunks))

    return [item for chunk_result in results for item in chunk_result]
```

**Windows note:** Always wrap the call in `if __name__ == "__main__":` to avoid spawn-related re-import issues.

#### Strategy 2: Dynamic Task Queue (Variable Workloads)

Best for unpredictable task durations. Workers pull tasks dynamically as they complete.

```python
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from typing import List, Any

def process_item(item):
    return item * 2

def dynamic_balanced_process(items: List[Any], num_workers=4):
    """Workers pull tasks dynamically as they complete."""
    results = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_item, item): item
                   for item in items[:num_workers]}
        pending = list(items[num_workers:])

        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)

            for future in done:
                results.append(future.result())
                del futures[future]

                if pending:
                    next_item = pending.pop(0)
                    futures[executor.submit(process_item, next_item)] = next_item

    return results
```

#### Strategy 3: Work Stealing (Long-Tail Tasks)

Best for when some tasks take much longer than others. Idle workers "steal" from the end of other workers' queues.

```python
import asyncio
from collections import deque
from typing import Optional, Callable, Any

class WorkStealingPool:
    def __init__(self, num_workers: int):
        self.queues = [deque() for _ in range(num_workers)]
        self.num_workers = num_workers

    def distribute(self, items: list):
        """Initial round-robin distribution."""
        for i, item in enumerate(items):
            self.queues[i % self.num_workers].append(item)

    async def worker(self, worker_id: int, process_fn: Callable):
        """Process own queue, steal from others when empty."""
        while True:
            if self.queues[worker_id]:
                item = self.queues[worker_id].pop()
            else:
                item = self._steal_work(worker_id)
                if item is None:
                    break

            await process_fn(item)

    def _steal_work(self, worker_id: int) -> Optional[Any]:
        """Steal from the queue with most items."""
        busiest = max(range(self.num_workers),
                      key=lambda i: len(self.queues[i]) if i != worker_id else 0)
        if self.queues[busiest]:
            return self.queues[busiest].popleft()
        return None
```

#### Strategy 4: Weighted Distribution (Bin Packing)

Best for when task costs are known or estimable. Uses a "Largest Processing Time first" (LPT) heuristic to minimize makespan.

```python
from typing import List, Tuple, Any

def weighted_partition(items: List[Any], weights: List[float], num_workers: int):
    """Partition items to balance total weight per worker using LPT algorithm."""
    sorted_items = sorted(zip(items, weights), key=lambda x: -x[1])

    worker_loads = [0.0] * num_workers
    worker_items = [[] for _ in range(num_workers)]

    for item, weight in sorted_items:
        min_worker = min(range(num_workers), key=lambda i: worker_loads[i])
        worker_items[min_worker].append(item)
        worker_loads[min_worker] += weight

    return worker_items
```

#### Strategy 5: Async Semaphore Balancing (I/O Workloads)

Best for limiting concurrent I/O operations to prevent socket exhaustion or API rate limiting.

```python
import asyncio
import aiohttp

async def semaphore_balanced_fetch(urls: list, max_concurrent=10):
    """Limit concurrent operations while processing queue."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_fetch(session, url):
        async with semaphore:
            async with session.get(url) as response:
                return await response.text()

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Step 4: Handle Stragglers

Techniques to mitigate slow workers:

```python
# 1. Timeout with fallback
from concurrent.futures import TimeoutError

try:
    result = future.result(timeout=30)
except TimeoutError:
    result = fallback_value

# 2. Speculative execution (Backup Tasks)
async def speculative_execute(task, timeout=10):
    primary = asyncio.create_task(execute(task))
    try:
        return await asyncio.wait_for(primary, timeout)
    except asyncio.TimeoutError:
        backup = asyncio.create_task(execute(task))
        done, pending = await asyncio.wait(
            [primary, backup], return_when=asyncio.FIRST_COMPLETED
        )
        for p in pending:
            p.cancel()
        return done.pop().result()

# 3. Dynamic rebalancing
def rebalance_on_straggler(futures, threshold_ratio=2.0):
    """Redistribute work if one worker falls behind."""
    avg_completion = statistics.mean(completion_times)
    for future, worker_id in futures.items():
        if future.running() and elapsed(future) > threshold_ratio * avg_completion:
            remaining_work = cancel_and_get_remaining(future)
            redistribute(remaining_work, fast_workers)
```

### Step 5: Monitor and Adapt

Track these metrics during execution:

| Metric | Calculation | Target | Significance |
|--------|-------------|--------|---------------|
| Load imbalance | `max(load) / avg(load)` | < 1.2 | High value indicates poor distribution |
| Straggler ratio | `max(time) / median(time)` | < 2.0 | High value indicates "long tail" issues |
| Worker utilization | `busy_time / total_time` | > 90% | Low value indicates overhead or starvation |
| Queue depth variance | `std(queue_lengths)` | Low | High variance suggests need for work stealing |

### Partitioning Strategies Reference

| Strategy | Best For | Implementation | Complexity |
|----------|----------|----------------|------------|
| Equal chunks | Uniform tasks | `np.array_split(items, n)` | O(1) |
| Round-robin | Streaming | `items[i::n_workers]` | O(1) |
| Size-weighted | Known sizes | LPT Bin Packing | O(N log N) |
| Hash-based | Consistent routing | `hash(key) % n_workers` | O(1) |
| Range-based | Sorted/ordered data | Contiguous ranges | O(1) |

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Starvation | Large tasks block queue | Break into subtasks or use priority queues |
| Thundering herd | All workers wake at once | Add random jitter to retry/wake intervals |
| Hot spots | Uneven key distribution | Use consistent hashing or salt keys |
| Convoy effect | Workers wait on same resource | Use fine-grained locking or lock-free structures |
| Over-partitioning | Too many small tasks | Batch small items into larger chunks |
| Serialization overhead | `multiprocessing.Queue` for tiny tasks | Use `multiprocessing.shared_memory` or `Ray` |
| Windows spawn crash | Missing `__main__` guard | Wrap entry point in `if __name__ == "__main__":` |
| Scheduler bottleneck | Global lock in dynamic scheduling | Use decentralized work stealing or lock-free queues |

## Verification

Before finalizing balanced code, verify each item:

1. **Work distribution is roughly even** — measure completion times per worker:
   ```python
   import time
   start = time.perf_counter()
   # ... run workload ...
   elapsed = time.perf_counter() - start
   print(f"Total elapsed: {elapsed:.2f}s")
   ```
   Check that per-worker time variance is low (load imbalance < 1.2).

2. **No starvation** — confirm all workers stay busy until the end by logging worker activity timestamps.

3. **Stragglers are handled** — verify timeout/retry/speculative logic is implemented and tested under skewed load.

4. **Overhead is acceptable** — measure partitioning cost separately and confirm it is much less than task execution cost.

5. **Results are complete and correct** — assert no lost tasks during stealing/rebalancing:
   ```python
   assert len(results) == len(items), f"Lost tasks: {len(items) - len(results)}"
   ```

6. **Resource utilization is high** — monitor CPU/memory usage across workers; target > 90% busy time.

7. **Run the test suite** — verify balancing behavior under skewed load distributions:
   ```powershell
   python -m pytest tests/test_workload_balancing.py -v
   ```

## Related Skills

- parallel-processing
- async-programming
- performance-optimization
- distributed-systems
- task-scheduling
