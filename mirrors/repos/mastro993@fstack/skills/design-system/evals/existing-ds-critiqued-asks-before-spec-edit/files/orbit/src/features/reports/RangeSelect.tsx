const ranges = ["Last 7 days", "Last 30 days", "This quarter"];

export function RangeSelect({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <label style={{ fontSize: 13, fontWeight: 500 }}>
      Range
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ marginLeft: 8, border: "1px solid #E4E1EC", borderRadius: 4, padding: "6px 10px" }}
      >
        {ranges.map((r) => <option key={r}>{r}</option>)}
      </select>
    </label>
  );
}
