import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { kind?: "primary" | "secondary" };

export function Button({ kind = "primary", className = "", ...rest }: Props) {
  const look =
    kind === "primary"
      ? "bg-primary text-on-primary hover:bg-primary-hover"
      : "border border-border bg-surface text-on-surface";
  return <button className={`rounded-md px-4 py-2 text-sm font-medium ${look} ${className}`} {...rest} />;
}
