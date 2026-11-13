import { useState } from "react";
import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";

export function SearchBox({ onSearch }: { onSearch: (q: string) => void }) {
  const [q, setQ] = useState("");
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSearch(q); }} style={{ display: "flex", gap: 8 }}>
      <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search" />
      <Button type="submit">Search</Button>
    </form>
  );
}
