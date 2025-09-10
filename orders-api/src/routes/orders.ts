import { Router } from "express";
import { orders, tracking } from "../lib/db";
import { Order, Tracking } from "../lib/types";
import { z } from "zod";

const router: Router = Router();

// GET /orders/:id
router.get("/:id", (req, res) => {
  const id = req.params.id;
  const order = orders.get(id);
  if (!order) return res.status(404).json({ error: "NOT_FOUND", message: "Order not found" });
  Order.parse(order);
  res.json(order);
});

// GET /orders/:id/tracking
router.get("/:id/tracking", (req, res) => {
  const id = req.params.id;
  const t = tracking.get(id);
  if (!t) return res.status(404).json({ error: "NOT_FOUND", message: "Tracking not found" });
  Tracking.parse(t);
  res.json(t);
});

// POST /orders/:id/cancel
router.post("/:id/cancel", (req, res) => {
  const id = req.params.id;
  const order = orders.get(id);
  if (!order) return res.status(404).json({ error: "NOT_FOUND", message: "Order not found" });

  // Policy gate: only if placed within N days & not already cancelled/delivered
  const eligibilityDays = Number(process.env.CANCELLATION_ELIGIBILITY_DAYS || 10);
  if (["delivered", "cancelled"].includes(order.status)) {
    const payload = { order_id: id, cancelled: false, error: "ALREADY_FINALIZED" as const };
    (res as any).saveIdempotent?.(payload);
    return res.status(409).json(payload);
  }
  // Validate policy inline to avoid circular import
  const placed = new Date(order.placed_at);
  const diffDays = Math.floor((Date.now() - placed.getTime()) / 86400000);
  if (!(diffDays < eligibilityDays)) {
    const payload = { order_id: id, cancelled: false, error: "ELIGIBILITY_WINDOW_EXPIRED" as const };
    (res as any).saveIdempotent?.(payload);
    return res.status(403).json(payload);
  }

  // Perform cancellation (idempotent)
  order.status = "cancelled";
  orders.set(id, order);
  const payload = { order_id: id, cancelled: true };
  (res as any).saveIdempotent?.(payload);
  res.json(payload);
});

export default router;