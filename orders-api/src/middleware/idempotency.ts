import type { Request, Response, NextFunction } from "express";
import { idempotency } from "../lib/db";

export function idempotencyMiddleware(req: Request, res: Response, next: NextFunction) {
  const key = req.header("Idempotency-Key");
  if (!key) return next();
  if (idempotency.has(key)) {
    return res.status(200).json(idempotency.get(key));
  }
  // Attach a setter for handlers
  (res as any).saveIdempotent = (payload: unknown) => idempotency.set(key, payload);
  next();
}