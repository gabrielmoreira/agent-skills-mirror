import { useEffect, useState } from "react";

type Me = { id: string; email: string };

export function App() {
  const [me, setMe] = useState<Me | null>(null);

  // Fetch the current user
  useEffect(() => {
    fetch("/api/users/me").then((r) => r.json()).then(setMe);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Relay</h1>
        <span className="app-user">{me?.email}</span>
      </header>
      <main />
    </div>
  );
}
