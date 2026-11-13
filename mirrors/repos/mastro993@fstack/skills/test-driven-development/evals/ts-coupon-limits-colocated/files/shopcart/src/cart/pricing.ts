export type Item = { sku: string; unitPriceCents: number; quantity: number };

export type Coupon = { code: string; percentOff: number };

export type Price = { subtotalCents: number; discountCents: number; totalCents: number };

const HAPPY_HOUR_START = 17;
const HAPPY_HOUR_END = 19;
const HAPPY_HOUR_PERCENT = 10;

export function subtotalCents(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.unitPriceCents * item.quantity, 0);
}

function percentOf(cents: number, percent: number): number {
  return Math.round((cents * percent) / 100);
}

export function priceCart(items: Item[], coupon?: Coupon, now: Date = new Date()): Price {
  const subtotal = subtotalCents(items);
  const hour = now.getHours();
  const happyHour = hour >= HAPPY_HOUR_START && hour < HAPPY_HOUR_END;
  const percent = (coupon?.percentOff ?? 0) + (happyHour ? HAPPY_HOUR_PERCENT : 0);
  const discount = percentOf(subtotal, Math.min(percent, 100));
  return { subtotalCents: subtotal, discountCents: discount, totalCents: subtotal - discount };
}
