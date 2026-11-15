import { randomUUID } from "node:crypto";
import type { Notification } from "@prisma/client";
import { signPayload } from "../../util/sign.js";
import { renderSlack } from "../templates.js";
import type { DeliveryResult } from "../types.js";

// Added for the webhook refactor
const WEBHOOK_TIMEOUT_MS = 10_000;
const url = process.env.NOTIFY_WEBHOOK_URL ?? "";
const secret = process.env.NOTIFY_WEBHOOK_SECRET ?? "";

export async function sendWebhook(n: Notification): Promise<DeliveryResult> {
  if (!url) return { ok: false, retryable: false, error: "NOTIFY_WEBHOOK_URL is not set" };

  const msgId = `msg_${randomUUID()}`;
  const timestamp = Math.floor(Date.now() / 1000);
  const payload = JSON.stringify({
    id: n.id,
    kind: n.kind,
    userId: n.userId,
    createdAt: n.createdAt.toISOString(),
    text: renderSlack(n),
  });

  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "webhook-id": msgId,
        "webhook-timestamp": String(timestamp),
        "webhook-signature": signPayload(secret, msgId, timestamp, payload),
      },
      body: payload,
      signal: AbortSignal.timeout(WEBHOOK_TIMEOUT_MS),
    });
  } catch (err) {
    return { ok: false, retryable: true, error: String(err) };
  }

  if (res.ok) return { ok: true, providerId: msgId };
  const retryable = res.status === 429 || res.status >= 500;
  return { ok: false, retryable, error: `webhook responded ${res.status}` };
}
