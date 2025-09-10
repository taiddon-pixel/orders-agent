import { Order, Tracking } from "./types";

const today = new Date();
const daysAgo = (n: number) => new Date(today.getTime() - n * 86400000).toISOString();

export const orders = new Map<string, Order>([
  ["A123", { order_id: "A123", placed_at: daysAgo(3), status: "processing", items: [{ sku: "ABC", qty: 1 }] }],
  ["B456", { order_id: "B456", placed_at: daysAgo(12), status: "in_transit", items: [{ sku: "XYZ", qty: 2 }] }],
  ["C789", { order_id: "C789", placed_at: daysAgo(1), status: "delivered", items: [{ sku: "LMN", qty: 1 }] }],
]);

export const tracking = new Map<string, Tracking>([
  ["A123", { order_id: "A123", current_status: "label_created", eta: "2025-09-15", last_checkpoint: "Warehouse" }],
  ["B456", { order_id: "B456", current_status: "in_transit", eta: "2025-09-16", last_checkpoint: "Hub A" }],
  ["C789", { order_id: "C789", current_status: "delivered", eta: "2025-09-09", last_checkpoint: "Recipient" }],
]);

// Simple idempotency record: idempotencyKey -> result payload
export const idempotency = new Map<string, unknown>();