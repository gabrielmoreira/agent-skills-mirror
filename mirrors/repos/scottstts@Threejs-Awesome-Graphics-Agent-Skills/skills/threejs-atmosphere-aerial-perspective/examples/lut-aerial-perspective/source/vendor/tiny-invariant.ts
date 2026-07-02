export default function invariant(condition: unknown, message?: string | (() => string)): asserts condition {
  if (condition) return;
  const provided = typeof message === "function" ? message() : message;
  throw new Error(provided != null ? `Invariant failed: ${provided}` : "Invariant failed");
}
