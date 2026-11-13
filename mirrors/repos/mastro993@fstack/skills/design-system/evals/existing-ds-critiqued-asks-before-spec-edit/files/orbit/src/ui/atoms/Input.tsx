import type { InputHTMLAttributes } from "react";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      style={{ border: "1px solid #E4E1EC", borderRadius: 6, padding: "8px 12px", fontSize: 14 }}
      {...props}
    />
  );
}
