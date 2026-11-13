import { useState } from "react";

const roles = ["Viewer", "Editor", "Admin"] as const;
type Role = (typeof roles)[number];

export function RoleDropdown({ role, onChange }: { role: Role; onChange: (r: Role) => void }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <div onClick={() => setOpen(!open)} style={{ border: "1px solid #ddd", borderRadius: 8, padding: "6px 12px", cursor: "pointer" }}>
        {role} ▾
      </div>
      {open && (
        <div style={{ position: "absolute", top: "100%", background: "white", boxShadow: "0 4px 12px rgba(0,0,0,.12)", borderRadius: 8 }}>
          {roles.map((r) => (
            <div key={r} onClick={() => { onChange(r); setOpen(false); }} style={{ padding: "6px 12px", color: r === role ? "#7C3AED" : undefined }}>
              {r}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
