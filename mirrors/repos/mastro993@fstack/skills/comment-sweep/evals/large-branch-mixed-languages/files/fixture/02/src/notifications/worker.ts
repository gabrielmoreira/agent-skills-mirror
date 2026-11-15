import type { DeliveryJob } from "./types.js";
import { deliver } from "./channels/index.js";
import { queue, redis } from "./queue.js";
import * as repo from "./repository.js";

const CLAIM_TIMEOUT_SECONDS = 5;
const PROMOTE_EVERY_MS = 1_000;
const SWEEP_EVERY_MS = 60_000;
const STALE_AFTER_MS = 30 * 60_000;

let running = true;

export async function handle(raw: string, job: DeliveryJob): Promise<void> {
  const notification = await repo.findNotification(job.notificationId);
  if (!notification || notification.status !== "PENDING") {
    await queue.ack(raw);
    return;
  }

  const attempts = await repo.bumpAttempts(notification.id);
  const result = await deliver(job.channel, notification);

  if (result.ok) {
    // Order matters: mark the row SENT before acking. Acking first and crashing in between
    // leaves the row PENDING with no job, and the stale sweeper delivers it a second time.
    await repo.markSent(notification.id, result.providerId);
    await queue.ack(raw);
    return;
  }

  if (result.retryable && (await queue.retry(raw, job)) === "retried") {
    console.warn(`notification ${notification.id} attempt ${attempts} failed, retrying: ${result.error}`);
    return;
  }
  if (!result.retryable) await queue.ack(raw);
  await repo.markFailed(notification.id, attempts);
  console.error(`notification ${notification.id} failed for good: ${result.error}`);
}

async function sweepStale(): Promise<void> {
  const stale = await repo.stalePending(new Date(Date.now() - STALE_AFTER_MS), 500);
  for (const row of stale) {
    await queue.enqueue({ notificationId: row.id, channel: row.channel, attempt: 0 });
  }
  if (stale.length > 0) console.warn(`re-enqueued ${stale.length} stale notifications`);
}

async function main(): Promise<void> {
  const recovered = await queue.requeueStuck();
  if (recovered > 0) console.warn(`recovered ${recovered} in-flight jobs from a previous run`);

  const promoter = setInterval(() => void queue.promoteDue(), PROMOTE_EVERY_MS);
  const sweeper = setInterval(() => void sweepStale(), SWEEP_EVERY_MS);

  process.on("SIGTERM", () => {
    running = false;
  });

  // Loop forever and process jobs
  while (running) {
    const claimed = await queue.claim(CLAIM_TIMEOUT_SECONDS);
    if (!claimed) continue;
    // console.log("job", claimed.job);
    try {
      await handle(claimed.raw, claimed.job);
    } catch (err) {
      console.error(`worker crashed on ${claimed.job.notificationId}`, err);
    }
  }

  clearInterval(promoter);
  clearInterval(sweeper);
  await redis.quit();
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
