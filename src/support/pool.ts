/**
 * support/pool.ts — Bounded-concurrency job processor.
 *
 * Runs a handler for each job in the input array, keeping at most
 * `concurrency` handlers in flight at any time.  Slot indices are stable
 * for the lifetime of the pool so callers can associate display state
 * (e.g. a dashboard row) with a specific worker lane.
 *
 * JavaScript is single-threaded: the `index` read-and-increment is
 * synchronous before any await, so there is no data race on the counter.
 */
export async function processJobs<T>(
  jobs: T[],
  handler: (job: T, slot: number) => Promise<void>,
  opts: { concurrency: number },
): Promise<void> {
  if (jobs.length === 0) return;

  let index = 0;

  async function worker(slot: number): Promise<void> {
    for (;;) {
      const i = index++;
      if (i >= jobs.length) return;
      await handler(jobs[i], slot);
    }
  }

  await Promise.all(
    Array.from(
      { length: Math.min(opts.concurrency, jobs.length) },
      (_, slot) => worker(slot),
    ),
  );
}
