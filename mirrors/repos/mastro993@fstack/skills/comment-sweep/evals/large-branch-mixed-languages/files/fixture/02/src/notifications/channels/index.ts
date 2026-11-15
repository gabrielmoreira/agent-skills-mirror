import type { Notification } from "@prisma/client";
import type { Channel, DeliveryResult } from "../types.js";
import { sendEmail } from "./email.js";
import { sendPush } from "./push.js";
import { sendWebhook } from "./webhook.js";

const senders: Record<Channel, (n: Notification) => Promise<DeliveryResult>> = {
  EMAIL: sendEmail,
  PUSH: sendPush,
  WEBHOOK: sendWebhook,
};

export function deliver(channel: Channel, notification: Notification): Promise<DeliveryResult> {
  return senders[channel](notification);
}
