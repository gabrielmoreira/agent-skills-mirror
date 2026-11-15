import { useCallback, useEffect, useRef, useState } from "react";

export type NotificationItem = {
  id: string;
  kind: string;
  title: string;
  body: string;
  read: boolean;
  createdAt: string;
};

type Page = { items: NotificationItem[]; nextCursor: string | null };

const POLL_MS = 30_000;

/**
 * Hook that returns notifications.
 * @param unreadOnly whether to only return unread
 * @returns the notifications
 */
export function useNotifications(unreadOnly: boolean) {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);
  const aborter = useRef<AbortController | null>(null);

  const refreshCount = useCallback(async () => {
    const res = await fetch("/api/notifications/unread-count");
    if (res.ok) setUnread((await res.json()).count);
  }, []);

  const load = useCallback(
    async (after: string | null) => {
      aborter.current?.abort();
      const controller = new AbortController();
      aborter.current = controller;
      setLoading(true);
      const params = new URLSearchParams({ unread: String(unreadOnly), limit: "20" });
      if (after) params.set("cursor", after);
      try {
        const res = await fetch(`/api/notifications?${params}`, { signal: controller.signal });
        const page: Page = await res.json();
        setItems((prev) => (after ? [...prev, ...page.items] : page.items));
        setCursor(page.nextCursor);
      } finally {
        if (aborter.current === controller) setLoading(false);
      }
    },
    [unreadOnly],
  );

  const markRead = useCallback(async (id: string) => {
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
    setUnread((n) => Math.max(0, n - 1));
    await fetch(`/api/notifications/${id}/read`, { method: "POST" });
  }, []);

  const markAllRead = useCallback(async () => {
    setItems((prev) => prev.map((n) => ({ ...n, read: true })));
    setUnread(0);
    await fetch("/api/notifications/read-all", { method: "POST" });
  }, []);

  useEffect(() => {
    void refreshCount();
    const timer = setInterval(() => void refreshCount(), POLL_MS);
    return () => clearInterval(timer);
  }, [refreshCount]);

  return {
    items,
    unread,
    loading,
    hasMore: cursor !== null,
    load: () => load(null),
    loadMore: () => load(cursor),
    markRead,
    markAllRead,
  };
}
