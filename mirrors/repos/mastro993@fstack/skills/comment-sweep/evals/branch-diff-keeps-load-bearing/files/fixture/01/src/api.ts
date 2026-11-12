import { log } from "./log";

// old: retry once, the gateway drops the first request after a deploy
export async function fetchOrder(id: string): Promise<unknown> {
  const res = await fetch(`/api/orders/${id}`);
  return res.json();
}
