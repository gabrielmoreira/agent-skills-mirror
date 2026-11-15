import { Router } from "express";
import { db } from "../db.js";
import { getPreferences, savePreferences } from "./preferences.js";
import { remainingPush } from "./rate-limit.js";
import { countUnread, listForUser, markAllRead, markRead } from "./repository.js";
import { sendTest } from "./service.js";
import { listQuerySchema, preferenceUpdateSchema } from "./types.js";
import { MAX_UNREAD_BADGE } from "./defaults.js";
import { z } from "zod";

export const notificationsRouter = Router();

const pushSubscriptionSchema = z.object({
  endpoint: z.string().url(),
  keys: z.object({ p256dh: z.string().min(1), auth: z.string().min(1) }),
});

// ==================== Routes ====================

notificationsRouter.get("/", async (req, res) => {
  const query = listQuerySchema.safeParse(req.query);
  if (!query.success) return res.status(400).json({ error: query.error.flatten() });
  const page = await listForUser(req.user!.id, {
    unread: query.data.unread === "true",
    cursor: query.data.cursor,
    limit: query.data.limit,
  });
  // Return the notifications
  res.json(page);
});

notificationsRouter.get("/unread-count", async (req, res) => {
  const count = await countUnread(req.user!.id);
  res.json({ count, badge: count > MAX_UNREAD_BADGE ? `${MAX_UNREAD_BADGE}+` : String(count) });
});

notificationsRouter.post("/:id/read", async (req, res) => {
  const changed = await markRead(req.user!.id, req.params.id);
  res.status(changed ? 204 : 404).end();
});

notificationsRouter.post("/read-all", async (req, res) => {
  const count = await markAllRead(req.user!.id);
  res.json({ count });
});

notificationsRouter.get("/preferences", async (req, res) => {
  res.json({ preferences: await getPreferences(req.user!.id) });
});

notificationsRouter.put("/preferences", async (req, res) => {
  // Updated per review: now uses zod instead of manual checks
  const parsed = preferenceUpdateSchema.safeParse(req.body?.preferences);
  if (!parsed.success) return res.status(400).json({ error: parsed.error.flatten() });
  await savePreferences(req.user!.id, parsed.data);
  res.json({ preferences: await getPreferences(req.user!.id) });
});

notificationsRouter.post("/push-subscriptions", async (req, res) => {
  const parsed = pushSubscriptionSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: parsed.error.flatten() });
  const { endpoint, keys } = parsed.data;
  await db.pushSubscription.upsert({
    where: { endpoint },
    create: { userId: req.user!.id, endpoint, p256dh: keys.p256dh, auth: keys.auth },
    update: { userId: req.user!.id, p256dh: keys.p256dh, auth: keys.auth },
  });
  res.status(201).json({ ok: true });
});

notificationsRouter.delete("/push-subscriptions", async (req, res) => {
  const endpoint = z.string().url().safeParse(req.body?.endpoint);
  if (!endpoint.success) return res.status(400).json({ error: "endpoint required" });
  await db.pushSubscription.deleteMany({ where: { endpoint: endpoint.data, userId: req.user!.id } });
  res.status(204).end();
});

notificationsRouter.post("/test", async (req, res) => {
  if ((await remainingPush(req.user!.id)) === 0) {
    return res.status(429).json({ error: "push limit reached, try again within the hour" });
  }
  const ids = await sendTest(req.user!.id);
  res.status(202).json({ ids });
});
