import type { FastifyInstance } from "fastify";
import type { ProductRepository } from "../infra/ProductRepository";

async function withRetry(fn: () => Promise<void>, attempts = 3): Promise<void> {
  for (let i = 0; i < attempts; i++) {
    try { return await fn(); } catch (e: any) { if (e.name !== "ConcurrencyError" || i === attempts - 1) throw e; }
  }
}

export function routes(app: FastifyInstance, products: ProductRepository) {
  app.put("/products/:pid/items/:iid", async (req: any) => {
    await withRetry(async () => {
      const product = await products.byId(req.params.pid);
      product.editBacklogItem(req.params.iid, req.body.title, req.body.story);
      await products.save(product);
    });
  });

  app.post("/products/:pid/items/:iid/commit", async (req: any) => {
    await withRetry(async () => {
      const product = await products.byId(req.params.pid);
      product.commitToSprint(req.params.iid, req.body.sprintId);
      await products.save(product);
    });
  });
}
