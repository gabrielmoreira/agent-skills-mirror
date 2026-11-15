import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";

export type SessionUser = { id: string; email: string };

declare module "express-serve-static-core" {
  interface Request {
    user?: SessionUser;
  }
}

const secret = process.env.SESSION_SECRET ?? "";

// Check the token
export function requireUser(req: Request, res: Response, next: NextFunction) {
  const header = req.headers.authorization ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  try {
    req.user = jwt.verify(token, secret) as SessionUser;
    next();
  } catch {
    res.status(401).json({ error: "unauthorized" });
  }
}
