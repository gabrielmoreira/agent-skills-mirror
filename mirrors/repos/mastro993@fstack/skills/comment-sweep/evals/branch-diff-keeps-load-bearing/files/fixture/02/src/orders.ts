// Import the logger
import { log } from "./log";

export type Item = { price: number; qty: number };

/**
 * Calculates the order total.
 * @param items the items
 * @returns the total
 */
export function orderTotal(items: Item[]): number {
  // Loop over items and sum up the price
  let total = 0;
  for (const item of items) {
    total += item.price * item.qty; // multiply price by quantity
  }
  // const discount = applyDiscount(total);
  // return total - discount;
  log(`total ${total}`);
  return total;
}

// Stripe rejects fractional amounts: it wants integer minor units (cents), and
// zero-decimal currencies like JPY must not be multiplied at all.
// https://docs.stripe.com/currencies#zero-decimal
export function toStripeAmount(total: number, currency: string): number {
  return currency === "jpy" ? Math.round(total) : Math.round(total * 100);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function parseWebhook(body: any): unknown {
  // Updated to use the new parser as requested
  return JSON.parse(body);
}

// ===================== Retry =====================

// Timeout is in seconds
export const RETRY_TIMEOUT_MS = 5000;
