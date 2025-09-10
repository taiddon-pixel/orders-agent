import { z } from "zod";

export const OrderStatus = z.enum(["processing", "in_transit", "delivered", "cancelled"]);
export type OrderStatus = z.infer<typeof OrderStatus>;

export const Order = z.object({
  order_id: z.string().min(1),
  placed_at: z.string().datetime(),   // ISO 8601
  status: OrderStatus,
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().positive() })),
});
export type Order = z.infer<typeof Order>;

export const Tracking = z.object({
  order_id: z.string(),
  current_status: z.string(),
  eta: z.string(),           // YYYY-MM-DD for demo
  last_checkpoint: z.string(),
});
export type Tracking = z.infer<typeof Tracking>;
