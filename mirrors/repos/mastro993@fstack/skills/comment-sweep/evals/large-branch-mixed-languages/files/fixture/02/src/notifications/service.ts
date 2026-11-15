// Import dependencies
import { DEFAULT_CHANNELS } from "../generated/notification-kinds.js";
import { enabledChannels } from "./preferences.js";
import { queue } from "./queue.js";
import { allowPush } from "./rate-limit.js";
import { insertNotifications } from "./repository.js";
import { notificationInputSchema, type Channel, type NotificationInput } from "./types.js";

/**
 * Creates a notification.
 * @param input the input
 * @returns the ids
 */
export async function notify(input: NotificationInput): Promise<string[]> {
  const parsed = notificationInputSchema.parse(input);
  const wanted: Channel[] = parsed.channels ?? [...DEFAULT_CHANNELS[parsed.kind]];

  // Check if the user has opted out
  let channels = await enabledChannels(parsed.userId, parsed.kind, wanted);
  if (channels.includes("PUSH") && !(await allowPush(parsed.userId))) {
    channels = channels.filter((c) => c !== "PUSH");
  }
  if (channels.length === 0) return [];

  const rows = await insertNotifications(
    channels.map((channel) => ({
      userId: parsed.userId,
      kind: parsed.kind,
      channel,
      title: parsed.title,
      body: parsed.body,
      data: (parsed.data ?? {}) as object,
    })),
  );

  // await audit.log("notification.created", rows.map((r) => r.id));
  for (const row of rows) {
    await queue.enqueue({ notificationId: row.id, channel: row.channel, attempt: 0 });
  }
  return rows.map((r) => r.id);
}

export async function notifyMany(inputs: NotificationInput[]): Promise<string[]> {
  const ids: string[] = [];
  for (const input of inputs) ids.push(...(await notify(input)));
  return ids;
}

export async function sendTest(userId: string): Promise<string[]> {
  return notify({
    userId,
    kind: "mention",
    title: "Test notification",
    body: "If you can read this, notifications reach you.",
    channels: ["EMAIL", "PUSH"],
  });
}
