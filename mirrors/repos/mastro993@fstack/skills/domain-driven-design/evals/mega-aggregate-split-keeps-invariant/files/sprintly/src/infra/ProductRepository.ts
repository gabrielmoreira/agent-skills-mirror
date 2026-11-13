import type { Db } from "mongodb";
import { ConcurrencyError, Product } from "../domain/Product";

export class ProductRepository {
  constructor(private db: Db) {}

  async byId(id: string): Promise<Product> {
    const doc = await this.db.collection("products").findOne({ _id: id as any });
    if (!doc) throw new Error("no such product");
    return new Product(doc._id as any, doc.name, doc.backlogItems, doc.sprints, doc.releases, doc.version);
  }

  async save(product: Product): Promise<void> {
    const { id, version, ...rest } = product;
    const result = await this.db.collection("products").updateOne(
      { _id: id as any, version },
      { $set: { ...rest, version: version + 1 } },
    );
    if (result.matchedCount === 0) throw new ConcurrencyError("Product version mismatch");
  }
}
