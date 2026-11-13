import Stripe from "stripe";
import { db } from "../db";
import type { Order } from "../models/Order";

const stripe = new Stripe(process.env.STRIPE_KEY!);

export class OrderService {
  async updateStatus(orderId: number, status: number, userRole: string): Promise<void> {
    const order: Order = (await db.query("select * from orders where id = $1", [orderId])).rows[0];

    if (status === 3 && order.status !== 2) {
      throw new Error("cannot ship an unpaid order");
    }
    if (status === 1 && order.discountPct > 20 && userRole !== "manager") {
      throw new Error("discount over 20% needs a manager");
    }
    if (status === 2) {
      const pi = await stripe.paymentIntents.retrieve(order.paymentIntent!.id);
      if (pi.status !== "succeeded") throw new Error("payment not settled");
    }

    await db.query("update orders set status = $1 where id = $2", [status, orderId]);
    await db.query("update customers set status = 2 where id = $1 and status < 2", [order.customerId]);
  }

  async setDiscount(orderId: number, pct: number): Promise<void> {
    await db.query("update orders set discount_pct = $1 where id = $2", [pct, orderId]);
  }
}
