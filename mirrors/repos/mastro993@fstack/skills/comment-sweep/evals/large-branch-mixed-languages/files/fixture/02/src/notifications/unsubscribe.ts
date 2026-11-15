import { createHmac, timingSafeEqual } from "node:crypto";
import { Router } from "express";
import { CHANNELS, type Channel } from "./types.js";
import { unsubscribeAll } from "./preferences.js";

const secret = process.env.UNSUBSCRIBE_SECRET ?? "";
const appUrl = process.env.APP_URL ?? "https://relay.acme.dev";

function sign(userId: string, channel: Channel): string {
  return createHmac("sha256", secret).update(`${userId}:${channel}`).digest("base64url");
}

export function unsubscribeUrl(userId: string, channel: Channel): string {
  const token = Buffer.from(`${userId}:${channel}:${sign(userId, channel)}`).toString("base64url");
  return `${appUrl}/unsubscribe?token=${token}`;
}

export function readToken(token: string): { userId: string; channel: Channel } | null {
  const [userId, channel, mac] = Buffer.from(token, "base64url").toString().split(":");
  if (!userId || !mac || !CHANNELS.includes(channel as Channel)) return null;
  const expected = Buffer.from(sign(userId, channel as Channel));
  const given = Buffer.from(mac);
  if (expected.length !== given.length || !timingSafeEqual(expected, given)) return null;
  return { userId, channel: channel as Channel };
}

export const unsubscribeRouter = Router();

unsubscribeRouter.get("/", (_req, res) => {
  res.sendFile("unsubscribe.html", { root: "web/public" });
});

unsubscribeRouter.post("/", async (req, res) => {
  const token = String(req.query.token ?? req.body?.token ?? "");
  const parsed = readToken(token);
  if (!parsed) return res.status(400).json({ error: "invalid token" });
  await unsubscribeAll(parsed.userId, parsed.channel);
  res.status(200).json({ ok: true, channel: parsed.channel });
});
