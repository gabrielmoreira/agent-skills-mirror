import { db } from "../db";
import type { Customer } from "../models/Customer";

export class CustomerManager {
  async update(id: number, patch: Partial<Customer>): Promise<void> {
    const cols = Object.keys(patch);
    const sets = cols.map((c, i) => `${c} = $${i + 2}`).join(", ");
    await db.query(`update customers set ${sets} where id = $1`, [id, ...Object.values(patch)]);
  }
}
