import type { NotificationKind } from "../generated/notification-kinds.js";
import { NOTIFICATION_KINDS } from "../generated/notification-kinds.js";
import { db } from "../db.js";
import { defaultEnabled } from "./defaults.js";
import { CHANNELS, type Channel } from "./types.js";

export type PreferenceRow = { kind: NotificationKind; channel: Channel; enabled: boolean };

// Get the preferences for the user
export async function getPreferences(userId: string): Promise<PreferenceRow[]> {
  const stored = await db.notificationPreference.findMany({ where: { userId } });
  const byKey = new Map(stored.map((p) => [`${p.kind}:${p.channel}`, p.enabled]));
  const rows: PreferenceRow[] = [];
  for (const kind of NOTIFICATION_KINDS) {
    for (const channel of CHANNELS) {
      rows.push({ kind, channel, enabled: byKey.get(`${kind}:${channel}`) ?? defaultEnabled(kind, channel) });
    }
  }
  return rows;
}

export async function enabledChannels(userId: string, kind: NotificationKind, wanted: Channel[]): Promise<Channel[]> {
  const prefs = await getPreferences(userId);
  return wanted.filter((channel) => prefs.some((p) => p.kind === kind && p.channel === channel && p.enabled));
}

export async function savePreferences(userId: string, rows: PreferenceRow[]): Promise<void> {
  await db.$transaction(
    rows.map((row) =>
      db.notificationPreference.upsert({
        where: { userId_kind_channel: { userId, kind: row.kind, channel: row.channel } },
        create: { userId, ...row },
        update: { enabled: row.enabled },
      }),
    ),
  );
}

export async function unsubscribeAll(userId: string, channel: Channel): Promise<void> {
  await savePreferences(
    userId,
    NOTIFICATION_KINDS.map((kind) => ({ kind, channel, enabled: false })),
  );
}
