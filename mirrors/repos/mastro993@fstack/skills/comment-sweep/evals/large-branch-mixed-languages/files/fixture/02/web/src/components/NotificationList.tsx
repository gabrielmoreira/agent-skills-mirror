import { useEffect } from "react";
import type { useNotifications } from "../hooks/useNotifications";

type Props = { notifications: ReturnType<typeof useNotifications> };

const relative = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

function ago(iso: string): string {
  const minutes = Math.round((new Date(iso).getTime() - Date.now()) / 60_000);
  if (Math.abs(minutes) < 60) return relative.format(minutes, "minute");
  const hours = Math.round(minutes / 60);
  if (Math.abs(hours) < 24) return relative.format(hours, "hour");
  return relative.format(Math.round(hours / 24), "day");
}

export function NotificationList({ notifications }: Props) {
  const { items, loading, hasMore, load, loadMore, markRead } = notifications;
  // const [filter, setFilter] = useState<"all" | "unread">("all");

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => void load(), []);

  if (!loading && items.length === 0) {
    return <p className="notification-empty">You're all caught up.</p>;
  }

  return (
    <div className="notification-list">
      <ul>
        {items.map((n) => (
          <li key={n.id} className={n.read ? "notification read" : "notification"}>
            <a
              href={`/notifications/${n.id}`}
              onClick={() => {
                if (!n.read) void markRead(n.id);
              }}
            >
              <span className="notification-title">{n.title}</span>
              <span className="notification-body">{n.body}</span>
              <time dateTime={n.createdAt}>{ago(n.createdAt)}</time>
            </a>
          </li>
        ))}
      </ul>
      {hasMore && (
        <button type="button" disabled={loading} onClick={() => void loadMore()}>
          {loading ? "Loading…" : "Load more"}
        </button>
      )}
    </div>
  );
}
