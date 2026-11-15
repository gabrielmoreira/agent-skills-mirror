import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("./preferences.js", () => ({ enabledChannels: vi.fn() }));
vi.mock("./rate-limit.js", () => ({ allowPush: vi.fn() }));
vi.mock("./repository.js", () => ({ insertNotifications: vi.fn() }));
vi.mock("./queue.js", () => ({ queue: { enqueue: vi.fn() } }));

import { enabledChannels } from "./preferences.js";
import { queue } from "./queue.js";
import { allowPush } from "./rate-limit.js";
import { insertNotifications } from "./repository.js";
import { notify } from "./service.js";

const base = {
  userId: "user_1",
  kind: "mention" as const,
  title: "Ada mentioned you",
  body: "@you can you look at the invoice export?",
};

function fakeRows(channels: string[]) {
  return channels.map((channel, i) => ({ id: `n_${i}`, channel }));
}

describe("notify", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(allowPush).mockResolvedValue(true);
    vi.mocked(insertNotifications).mockImplementation(async (rows) =>
      fakeRows(rows.map((r) => r.channel as string)) as never,
    );
  });

  it("uses the kind's default channels when none are given", async () => {
    vi.mocked(enabledChannels).mockImplementation(async (_u, _k, wanted) => wanted);
    await notify(base);
    expect(enabledChannels).toHaveBeenCalledWith("user_1", "mention", ["EMAIL", "PUSH"]);
  });

  it("creates one row and one job per enabled channel", async () => {
    vi.mocked(enabledChannels).mockResolvedValue(["EMAIL", "PUSH"]);
    const ids = await notify(base);
    expect(ids).toEqual(["n_0", "n_1"]);
    expect(queue.enqueue).toHaveBeenCalledTimes(2);
    expect(queue.enqueue).toHaveBeenCalledWith({ notificationId: "n_1", channel: "PUSH", attempt: 0 });
  });

  it("drops push when the user is over the hourly limit", async () => {
    vi.mocked(enabledChannels).mockResolvedValue(["EMAIL", "PUSH"]);
    vi.mocked(allowPush).mockResolvedValue(false);
    await notify(base);
    const rows = vi.mocked(insertNotifications).mock.calls[0][0];
    expect(rows.map((r) => r.channel)).toEqual(["EMAIL"]);
  });

  it("does nothing when every channel is opted out", async () => {
    vi.mocked(enabledChannels).mockResolvedValue([]);
    expect(await notify(base)).toEqual([]);
    expect(insertNotifications).not.toHaveBeenCalled();
    expect(queue.enqueue).not.toHaveBeenCalled();
  });

  it("rejects an unknown kind", async () => {
    await expect(notify({ ...base, kind: "nope" as never })).rejects.toThrow();
  });
});
