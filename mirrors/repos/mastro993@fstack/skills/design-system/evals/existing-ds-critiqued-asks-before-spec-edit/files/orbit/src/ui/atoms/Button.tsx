import type { ButtonHTMLAttributes } from "react";
import "../tokens.css";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" };

export function Button({ variant = "primary", style, ...rest }: Props) {
  const look =
    variant === "primary"
      ? { background: "var(--primary)", color: "var(--on-primary)" }
      : { background: "transparent", color: "var(--on-surface)" };
  return (
    <button
      style={{ ...look, borderRadius: "var(--radius-md)", padding: "var(--space-2) var(--space-3)", border: 0, ...style }}
      {...rest}
    />
  );
}
