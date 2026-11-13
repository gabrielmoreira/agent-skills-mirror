import { Router } from "express";
import { OrderService } from "../services/OrderService";

export const orders = Router();
const service = new OrderService();

orders.post("/:id/status", async (req, res) => {
  await service.updateStatus(Number(req.params.id), req.body.status, req.header("x-role") ?? "");
  res.sendStatus(204);
});

orders.post("/:id/discount", async (req, res) => {
  await service.setDiscount(Number(req.params.id), req.body.pct);
  res.sendStatus(204);
});
