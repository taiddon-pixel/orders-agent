import type { Request, Response, NextFunction } from "express";
import { ZodError } from "zod";

export function errorHandler(err: any, _req: Request, res: Response, _next: NextFunction) {
  if (err instanceof ZodError) {
    return res.status(400).json({ error: "VALIDATION_ERROR", details: err.issues });
  }
  const status = err?.status || 500;
  res.status(status).json({ error: err?.code || "INTERNAL_ERROR", message: err?.message || "Unexpected error" });
}