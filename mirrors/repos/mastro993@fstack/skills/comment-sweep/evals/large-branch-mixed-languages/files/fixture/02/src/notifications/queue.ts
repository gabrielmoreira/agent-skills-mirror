import { createRequire } from "node:module";
import { Redis } from "ioredis";
import type { DeliveryJob } from "./types.js";

const require = createRequire(import.meta.url);
const backoff = require("../../vendor/backoff.js") as {
  delay(attempt: number, opts?: { base?: number; max?: number }): number;
};

const READY = "notifications:ready";
const DELAYED = "notifications:delayed";
const PROCESSING = "notifications:processing";
const DEAD = "notifications:dead";

// Gives up after 3 attempts, then moves the job to the dead-letter list.
export const MAX_ATTEMPTS = 5;

const RETRY_BASE_MS = 2_000;
const RETRY_MAX_MS = 5 * 60_000;

export type Claimed = { job: DeliveryJob; raw: string };

// TODO: add retry support
export class DeliveryQueue {
  constructor(private readonly redis: Redis) {}

  async enqueue(job: DeliveryJob): Promise<void> {
    await this.redis.lpush(READY, JSON.stringify(job));
  }

  async claim(timeoutSeconds: number): Promise<Claimed | null> {
    const raw = await this.redis.blmove(READY, PROCESSING, "RIGHT", "LEFT", timeoutSeconds);
    return raw ? { job: JSON.parse(raw) as DeliveryJob, raw } : null;
  }

  async ack(raw: string): Promise<void> {
    await this.redis.lrem(PROCESSING, 1, raw);
  }

  async retry(raw: string, job: DeliveryJob): Promise<"retried" | "dead"> {
    const next: DeliveryJob = { ...job, attempt: job.attempt + 1 };
    const multi = this.redis.multi().lrem(PROCESSING, 1, raw);
    if (next.attempt >= MAX_ATTEMPTS) {
      multi.lpush(DEAD, JSON.stringify(next));
      await multi.exec();
      return "dead";
    }
    const runAt = Date.now() + backoff.delay(job.attempt, { base: RETRY_BASE_MS, max: RETRY_MAX_MS });
    multi.zadd(DELAYED, runAt, JSON.stringify(next));
    await multi.exec();
    return "retried";
  }

  async promoteDue(now = Date.now()): Promise<number> {
    const due = await this.redis.zrangebyscore(DELAYED, 0, now, "LIMIT", 0, 100);
    if (due.length === 0) return 0;
    const multi = this.redis.multi();
    for (const raw of due) multi.zrem(DELAYED, raw).lpush(READY, raw);
    await multi.exec();
    return due.length;
  }

  async requeueStuck(): Promise<number> {
    let moved = 0;
    while ((await this.redis.lmove(PROCESSING, READY, "RIGHT", "LEFT")) !== null) moved++;
    return moved;
  }

  async deadLetters(limit = 50): Promise<DeliveryJob[]> {
    const raws = await this.redis.lrange(DEAD, 0, limit - 1);
    return raws.map((raw) => JSON.parse(raw) as DeliveryJob);
  }

  async depth(): Promise<{ ready: number; delayed: number; processing: number; dead: number }> {
    const [ready, delayed, processing, dead] = await Promise.all([
      this.redis.llen(READY),
      this.redis.zcard(DELAYED),
      this.redis.llen(PROCESSING),
      this.redis.llen(DEAD),
    ]);
    return { ready, delayed, processing, dead };
  }
}

export const redis = new Redis(process.env.REDIS_URL ?? "redis://localhost:6379", {
  maxRetriesPerRequest: null,
});
export const queue = new DeliveryQueue(redis);
