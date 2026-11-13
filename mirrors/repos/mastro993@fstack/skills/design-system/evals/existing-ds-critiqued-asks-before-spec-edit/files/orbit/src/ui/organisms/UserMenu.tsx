import { useState } from "react";
import { useNavigate } from "react-router";
import { useSessionStore } from "../../store/session";
import { Button } from "../atoms/Button";

export function UserMenu() {
  const [open, setOpen] = useState(false);
  const { user, signOut } = useSessionStore();
  const navigate = useNavigate();
  if (!user) return null;
  return (
    <div style={{ position: "relative" }}>
      <Button variant="ghost" onClick={() => setOpen(!open)}>{user.name}</Button>
      {open && (
        <ul style={{ position: "absolute", right: 0, background: "#fff", border: "1px solid var(--border)", borderRadius: 6 }}>
          <li><button onClick={() => navigate("/profile")}>Profile</button></li>
          <li><button onClick={() => { signOut(); navigate("/login"); }}>Sign out</button></li>
        </ul>
      )}
    </div>
  );
}
