import { z } from "zod";
import { NOTIFICATION_KINDS, type NotificationKind } from "../generated/notification-kinds.js";

// Keep in sync with enum NotificationChannel in prisma/schema.prisma.
export const CHANNELS = ["EMAIL", "PUSH", "WEBHOOK"] as const;
export type Channel = (typeof CHANNELS)[number];

export const STATUSES = ["PENDING", "SENT", "FAILED"] as const;
export type Status = (typeof STATUSES)[number];

export type NotificationInput = {
  userId: string;
  kind: NotificationKind;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  channels?: Channel[];
};

export type NotificationView = {
  id: string;
  kind: NotificationKind;
  title: string;
  body: string;
  data: Record<string, unknown>;
  read: boolean;
  createdAt: string;
};

export type DeliveryJob = {
  notificationId: string;
  channel: Channel;
  attempt: number;
};

export type DeliveryResult =
  | { ok: true; providerId: string }
  | { ok: false; retryable: boolean; error: string };

export const notificationInputSchema = z.object({
  userId: z.string().min(1),
  kind: z.enum(NOTIFICATION_KINDS),
  title: z.string().min(1).max(140),
  body: z.string().min(1).max(4000),
  data: z.record(z.unknown()).optional(),
  channels: z.array(z.enum(CHANNELS)).nonempty().optional(),
});

export const listQuerySchema = z.object({
  unread: z.enum(["true", "false"]).optional(),
  cursor: z.string().optional(),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

export const preferenceUpdateSchema = z.array(
  z.object({
    kind: z.enum(NOTIFICATION_KINDS),
    channel: z.enum(CHANNELS),
    enabled: z.boolean(),
  }),
);
