import { log } from "./log";

// old: retry once, the gateway drops the first request after a deploy
export async function fetchOrder(id: string): Promise<unknown> {
  // Call the API to get the order
  const res = await fetch(`/api/orders/${id}`);
  log(`fetched ${id}`); // log that we fetched it
  return res.json();
}
