/*
 * Copyright (c) 2022 Svix Inc.
 * SPDX-License-Identifier: MIT
 *
 * Adapted from https://github.com/svix/svix-webhooks/blob/main/javascript/src/webhook.ts
 */
import { createHmac, timingSafeEqual } from "node:crypto";

export class WebhookVerificationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WebhookVerificationError";
  }
}

const TOLERANCE_SECONDS = 5 * 60;
const PREFIX = "whsec_";

function keyFrom(secret: string): Buffer {
  return Buffer.from(secret.startsWith(PREFIX) ? secret.slice(PREFIX.length) : secret, "base64");
}

export function signPayload(secret: string, msgId: string, timestamp: number, payload: string): string {
  const mac = createHmac("sha256", keyFrom(secret)).update(`${msgId}.${timestamp}.${payload}`).digest("base64");
  return `v1,${mac}`;
}

export function verifyPayload(
  secret: string,
  headers: { id: string; timestamp: string; signature: string },
  payload: string,
  now = Math.floor(Date.now() / 1000),
): void {
  const timestamp = Number(headers.timestamp);
  if (!Number.isInteger(timestamp)) throw new WebhookVerificationError("Invalid timestamp");
  if (now - timestamp > TOLERANCE_SECONDS) throw new WebhookVerificationError("Message timestamp too old");
  if (timestamp > now + TOLERANCE_SECONDS) throw new WebhookVerificationError("Message timestamp too new");

  const expected = Buffer.from(signPayload(secret, headers.id, timestamp, payload).split(",")[1]);
  for (const versioned of headers.signature.split(" ")) {
    const [version, signature] = versioned.split(",");
    if (version !== "v1" || !signature) continue;
    const given = Buffer.from(signature);
    if (given.length === expected.length && timingSafeEqual(given, expected)) return;
  }
  throw new WebhookVerificationError("No matching signature found");
}
