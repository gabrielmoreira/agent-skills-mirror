import type { Notification } from "@prisma/client";
import webpush from "web-push";
import { db } from "../../db.js";
import { PUSH_TTL_SECONDS } from "../defaults.js";
import type { DeliveryResult } from "../types.js";

webpush.setVapidDetails(
  "mailto:ops@acme.dev",
  process.env.VAPID_PUBLIC_KEY ?? "",
  process.env.VAPID_PRIVATE_KEY ?? "",
);

// Apple's push service, which carries Web Push to Safari, rejects payloads over 4 KB, and
// encryption adds its own overhead on top, so the JSON we hand web-push stays under 3 KB.
// https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers
const MAX_PAYLOAD_BYTES = 3_072;

export function buildPayload(n: Notification): string {
  const base = { id: n.id, kind: n.kind, title: n.title, url: `/notifications/${n.id}` };
  let body = n.body;
  let json = JSON.stringify({ ...base, body });
  while (Buffer.byteLength(json) > MAX_PAYLOAD_BYTES && body.length > 0) {
    body = body.slice(0, Math.floor(body.length * 0.8)) + "…";
    json = JSON.stringify({ ...base, body });
  }
  return json;
}

export async function sendPush(n: Notification): Promise<DeliveryResult> {
  const targets = await db.pushSubscription.findMany({ where: { userId: n.userId } });
  if (targets.length === 0) return { ok: true, providerId: "no-subscriptions" };

  const payload = buildPayload(n);
  let delivered = 0;
  let lastError = "";

  // TODO(https://github.com/acme/relay/issues/412): send to a user's devices in parallel once we know the per-origin rate limits.
  for (const target of targets) {
    try {
      await webpush.sendNotification(
        { endpoint: target.endpoint, keys: { p256dh: target.p256dh, auth: target.auth } },
        payload,
        // @ts-expect-error @types/web-push 3.6.4 lacks the "urgency" option that web-push 3.6.7 accepts
        { TTL: PUSH_TTL_SECONDS, urgency: n.kind === "invoice.failed" ? "high" : "normal" },
      );
      delivered++;
    } catch (err) {
      const status = (err as { statusCode?: number }).statusCode;
      if (status === 404 || status === 410) {
        await db.pushSubscription.delete({ where: { id: target.id } });
        continue;
      }
      lastError = `${status ?? "network"}: ${String(err)}`;
    }
  }

  if (delivered > 0 || lastError === "") return { ok: true, providerId: `push:${delivered}` };
  return { ok: false, retryable: true, error: lastError };
}
