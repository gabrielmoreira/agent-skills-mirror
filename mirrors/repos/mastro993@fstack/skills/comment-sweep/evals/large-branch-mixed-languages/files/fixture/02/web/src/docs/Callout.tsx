import type { ReactNode } from "react";

type Props = { type?: "info" | "warning"; children: ReactNode };

export function Callout({ type = "info", children }: Props) {
  return (
    <aside className={`callout callout-${type}`} role="note">
      {children}
    </aside>
  );
}
