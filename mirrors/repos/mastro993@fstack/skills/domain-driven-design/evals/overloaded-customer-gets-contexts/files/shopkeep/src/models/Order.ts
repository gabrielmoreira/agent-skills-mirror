import type Stripe from "stripe";

export interface OrderLine {
  sku: string;
  qty: number;
  unitPriceCents: number;
}

export interface Order {
  id: number;
  customerId: number;
  lines: OrderLine[];
  discountPct: number;
  status: number; // 0 quote, 1 placed, 2 paid, 3 shipped, 4 cancelled
  paymentIntent?: Stripe.PaymentIntent;
  invoice?: Stripe.Invoice;
  trackingNumber?: string;
}
