import { Router } from "express";
import { db } from "../db.js";

export const usersRouter = Router();

// Get the user by id
usersRouter.get("/:id", async (req, res) => {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  // const legacy = await db.legacyUser.findUnique({ where: { id: req.params.id } });
  if (!user) return res.status(404).json({ error: "not found" });
  res.json(user);
});

usersRouter.get("/me", async (req, res) => {
  res.json(req.user);
});
