import type { Notification, Prisma } from "@prisma/client";
import { db } from "../db.js";
import type { Channel, NotificationView } from "./types.js";
import { isNotificationKind } from "../generated/notification-kinds.js";

// Now uses Prisma transactions instead of raw SQL
export async function insertNotifications(rows: Prisma.NotificationCreateManyInput[]): Promise<Notification[]> {
  return db.$transaction(rows.map((data) => db.notification.create({ data })));
}

export async function findNotification(id: string): Promise<Notification | null> {
  return db.notification.findUnique({ where: { id } });
}

export async function listForUser(
  userId: string,
  opts: { unread: boolean; cursor?: string; limit: number },
): Promise<{ items: NotificationView[]; nextCursor: string | null }> {
  const rows = await db.notification.findMany({
    where: { userId, channel: "PUSH", ...(opts.unread ? { readAt: null } : {}) },
    orderBy: [{ createdAt: "desc" }, { id: "desc" }],
    take: opts.limit + 1,
    ...(opts.cursor ? { cursor: { id: opts.cursor }, skip: 1 } : {}),
  });
  const page = rows.slice(0, opts.limit);
  return {
    items: page.map(toView),
    nextCursor: rows.length > opts.limit ? page[page.length - 1].id : null,
  };
}

export async function countUnread(userId: string): Promise<number> {
  return db.notification.count({ where: { userId, channel: "PUSH", readAt: null } });
}

/**
 * Marks a notification as read.
 * @param userId the user id
 * @param id the id
 */
export async function markRead(userId: string, id: string): Promise<boolean> {
  const { count } = await db.notification.updateMany({
    where: { id, userId, readAt: null },
    data: { readAt: new Date() },
  });
  return count === 1;
}

export async function markAllRead(userId: string): Promise<number> {
  const { count } = await db.notification.updateMany({
    where: { userId, readAt: null },
    data: { readAt: new Date() },
  });
  return count;
}

export async function markSent(id: string, providerId: string): Promise<void> {
  const row = await db.notification.findUniqueOrThrow({ where: { id }, select: { data: true } });
  await db.notification.update({
    where: { id },
    data: {
      status: "SENT",
      sentAt: new Date(),
      data: { ...(row.data as Record<string, unknown>), providerId },
    },
  });
}

export async function markFailed(id: string, attempts: number): Promise<void> {
  await db.notification.update({ where: { id }, data: { status: "FAILED", attempts } });
}

export async function bumpAttempts(id: string): Promise<number> {
  const row = await db.notification.update({
    where: { id },
    data: { attempts: { increment: 1 } },
    select: { attempts: true },
  });
  return row.attempts;
}

export async function stalePending(olderThan: Date, take: number): Promise<{ id: string; channel: Channel }[]> {
  return db.notification.findMany({
    where: { status: "PENDING", createdAt: { lt: olderThan } },
    select: { id: true, channel: true },
    orderBy: { createdAt: "asc" },
    take,
  });
}

function toView(row: Notification): NotificationView {
  if (!isNotificationKind(row.kind)) throw new Error(`unknown kind ${row.kind}`);
  return {
    id: row.id,
    kind: row.kind,
    title: row.title,
    body: row.body,
    data: row.data as Record<string, unknown>,
    read: row.readAt !== null,
    createdAt: row.createdAt.toISOString(),
  };
}
