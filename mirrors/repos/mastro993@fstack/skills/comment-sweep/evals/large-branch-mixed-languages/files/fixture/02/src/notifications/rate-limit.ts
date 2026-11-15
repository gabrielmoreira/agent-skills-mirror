import { redis } from "./queue.js";

const WINDOW_SECONDS = 60 * 60;
const MAX_PUSH_PER_WINDOW = 20;

function key(userId: string, now: number): string {
  return `notifications:push-rate:${userId}:${Math.floor(now / 1000 / WINDOW_SECONDS)}`;
}

export async function allowPush(userId: string, now = Date.now()): Promise<boolean> {
  const k = key(userId, now);
  // Increment the counter and set the expiry
  const [[, count]] = (await redis.multi().incr(k).expire(k, WINDOW_SECONDS).exec()) as [[null, number]];
  return count <= MAX_PUSH_PER_WINDOW;
}

export async function remainingPush(userId: string, now = Date.now()): Promise<number> {
  const used = Number((await redis.get(key(userId, now))) ?? 0);
  return Math.max(0, MAX_PUSH_PER_WINDOW - used);
}
