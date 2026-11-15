import type { NotificationKind } from "../generated/notification-kinds.js";
import type { Channel } from "./types.js";

export const DIGEST_HOUR_UTC = 8;
export const MAX_UNREAD_BADGE = 99;
export const PUSH_TTL_SECONDS = 60 * 60 * 24;

// prettier-ignore
export const PREFERENCE_MATRIX: Record<NotificationKind, Record<Channel, boolean>> = {
  "mention":        { EMAIL: true,  PUSH: true,  WEBHOOK: false },
  "comment.reply":  { EMAIL: false, PUSH: true,  WEBHOOK: false },
  "invoice.paid":   { EMAIL: true,  PUSH: false, WEBHOOK: true  },
  "invoice.failed": { EMAIL: true,  PUSH: true,  WEBHOOK: true  },
  "digest.weekly":  { EMAIL: true,  PUSH: false, WEBHOOK: false },
};

export function defaultEnabled(kind: NotificationKind, channel: Channel): boolean {
  return PREFERENCE_MATRIX[kind][channel];
}
