import { useEffect, useState } from "react";
import { NotificationBell } from "./components/NotificationBell";
import { PreferencesForm } from "./components/PreferencesForm";

type Me = { id: string; email: string };

export function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [showPreferences, setShowPreferences] = useState(false);

  // Fetch the current user
  useEffect(() => {
    fetch("/api/users/me").then((r) => r.json()).then(setMe);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Relay</h1>
        <NotificationBell onOpenPreferences={() => setShowPreferences(true)} />
        <span className="app-user">{me?.email}</span>
      </header>
      <main>{showPreferences && <PreferencesForm onClose={() => setShowPreferences(false)} />}</main>
    </div>
  );
}
