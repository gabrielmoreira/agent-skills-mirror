import { useEffect, useState, type FormEvent } from "react";
import { usePushSubscription } from "../hooks/usePushSubscription";

type Preference = { kind: string; channel: "EMAIL" | "PUSH" | "WEBHOOK"; enabled: boolean };

const KIND_LABELS: Record<string, string> = {
  mention: "Mentions",
  "comment.reply": "Replies to your comments",
  "invoice.paid": "Paid invoices",
  "invoice.failed": "Failed payments",
  "digest.weekly": "Weekly digest",
};

const CHANNELS = ["EMAIL", "PUSH"] as const;

type Props = { onClose: () => void };

export function PreferencesForm({ onClose }: Props) {
  const [prefs, setPrefs] = useState<Preference[] | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const push = usePushSubscription();

  useEffect(() => {
    fetch("/api/notifications/preferences")
      .then((r) => r.json())
      .then((body) => setPrefs(body.preferences));
  }, []);

  function toggle(kind: string, channel: Preference["channel"]) {
    setPrefs((prev) =>
      prev!.map((p) => (p.kind === kind && p.channel === channel ? { ...p, enabled: !p.enabled } : p)),
    );
  }

  // Handle form submission
  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    const res = await fetch("/api/notifications/preferences", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ preferences: prefs }),
    });
    setSaving(false);
    if (!res.ok) {
      setError("Couldn't save your preferences. Try again.");
      return;
    }
    onClose();
  }

  if (!prefs) return <p>Loading preferences…</p>;

  const kinds = [...new Set(prefs.map((p) => p.kind))];

  return (
    <form className="preferences" onSubmit={onSubmit}>
      <h2>Notification settings</h2>
      {push.supported && !push.subscribed && (
        <button type="button" onClick={() => void push.subscribe()}>
          Turn on browser notifications
        </button>
      )}
      <table>
        <thead>
          <tr>
            <th scope="col">Notify me about</th>
            {CHANNELS.map((c) => (
              <th key={c} scope="col">
                {c === "EMAIL" ? "Email" : "Browser"}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {kinds.map((kind) => (
            <tr key={kind}>
              <th scope="row">{KIND_LABELS[kind] ?? kind}</th>
              {CHANNELS.map((channel) => {
                const pref = prefs.find((p) => p.kind === kind && p.channel === channel);
                return (
                  <td key={channel}>
                    <input
                      type="checkbox"
                      aria-label={`${KIND_LABELS[kind] ?? kind} by ${channel.toLowerCase()}`}
                      checked={pref?.enabled ?? false}
                      onChange={() => toggle(kind, channel)}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {error && <p role="alert">{error}</p>}
      <div className="preferences-actions">
        <button type="button" onClick={onClose}>
          Cancel
        </button>
        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save"}
        </button>
      </div>
    </form>
  );
}
