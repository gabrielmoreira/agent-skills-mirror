import { useState } from "react";
import { useNotifications } from "../hooks/useNotifications";
import { NotificationList } from "./NotificationList";

type Props = { onOpenPreferences: () => void };

export function NotificationBell({ onOpenPreferences }: Props) {
  const [open, setOpen] = useState(false);
  const notifications = useNotifications(false);
  const badge = notifications.unread > 99 ? "99+" : String(notifications.unread);

  return (
    <div className="bell">
      <button
        type="button"
        className="bell-button"
        aria-label={`Notifications, ${notifications.unread} unread`}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
      >
        {/* Render the bell icon */}
        <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2zm6-6V11a6 6 0 0 0-5-5.9V4a1 1 0 1 0-2 0v1.1A6 6 0 0 0 6 11v5l-2 2v1h16v-1l-2-2z" />
        </svg>
        {notifications.unread > 0 && <span className="bell-badge">{badge}</span>}
      </button>
      {open && (
        <div className="bell-panel" role="dialog" aria-label="Notifications">
          <div className="bell-panel-header">
            <strong>Notifications</strong>
            <button type="button" onClick={() => void notifications.markAllRead()}>
              Mark all read
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                onOpenPreferences();
              }}
            >
              Settings
            </button>
          </div>
          <NotificationList notifications={notifications} />
        </div>
      )}
    </div>
  );
}
