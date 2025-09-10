import { Order, Tracking } from "./types";

const today = new Date();
const daysAgo = (n: number) => new Date(today.getTime() - n * 86400000).toISOString();
const daysHence = (n: number) => new Date(today.getTime() + n * 86400000).toISOString();

export const orders = new Map<string, Order>([
  [
    "A123",
    {
      order_id: "A123",
      placed_at: daysAgo(3),
      status: "processing",
      items: [
        {
          sku: "SKU1",
          name: "Cuisinart 12-Cup Programmable Coffee Maker",
          qty: 1,
          status: "processing",
        },
        {
          sku: "SKU2",
          name: "OXO Good Grips 3-Piece Mixing Bowl Set",
          qty: 1,
          status: "processing",
        },
      ],
    },
  ],
  [
    "B456",
    {
      order_id: "B456",
      placed_at: daysAgo(12),
      status: "in_transit",
      items: [
        {
          sku: "SKU3",
          name: "Osprey Daylite Plus Backpack, Black",
          qty: 1,
          status: "in_transit",
        },
      ],
    },
  ],
  [
    "C789",
    {
      order_id: "C789",
      placed_at: daysAgo(1),
      status: "delivered",
      items: [
        {
          sku: "SKU4",
          name: "JBL Flip 6 Portable Bluetooth Speaker",
          qty: 1,
          status: "delivered",
        },
        {
          sku: "SKU5",
          name: "iOttie Easy One Touch Car Mount Phone Holder",
          qty: 2,
          status: "delivered",
        },
      ],
    },
  ],
  [
    "D234",
    {
      order_id: "D234",
      placed_at: daysAgo(7),
      status: "in_transit",
      items: [
        {
          sku: "SKU6",
          name: "Lodge Cast Iron Skillet, 10.25-Inch",
          qty: 1,
          status: "in_transit",
        },
      ],
    },
  ],
  [
    "E567",
    {
      order_id: "E567",
      placed_at: daysAgo(20),
      status: "delivered",
      items: [
        {
          sku: "SKU7",
          name: "Samsonite Winfield 2 Hardside Luggage, 24-Inch",
          qty: 1,
          status: "delivered",
        },
        {
          sku: "SKU8",
          name: "Columbia Men's Watertight II Rain Jacket",
          qty: 1,
          status: "delivered",
        },
      ],
    },
  ],
]);

export const tracking = new Map<string, Tracking>([
  [
    "A123",
    {
      order_id: "A123",
      current_status: "label_created",
      eta: daysHence(5),
      last_checkpoint: "Warehouse",
    },
  ],
  [
    "B456",
    {
      order_id: "B456",
      current_status: "in_transit",
      eta: daysHence(6),
      last_checkpoint: "Regional Hub",
    },
  ],
  [
    "C789",
    {
      order_id: "C789",
      current_status: "delivered",
      eta: daysHence(1),
      last_checkpoint: "Recipient",
    },
  ],
  [
    "D234",
    {
      order_id: "D234",
      current_status: "out_for_delivery",
      eta: daysHence(1),
      last_checkpoint: "Local Facility",
    },
  ],
  [
    "E567",
    {
      order_id: "E567",
      current_status: "delivered",
      eta: daysHence(2),
      last_checkpoint: "Recipient",
    },
  ],
]);

export const idempotency = new Map<string, unknown>();