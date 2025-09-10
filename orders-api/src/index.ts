import "dotenv/config";
import express from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import ordersRouter from "./routes/orders";
import { errorHandler } from "./middleware/errors";
import { log } from "./middleware/logger";

const app = express();
app.use(express.json());
app.use(cors());

const limiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 1000 });
app.use(limiter);

app.get("/healthz", (_req, res) => res.json({ ok: true }));

app.use("/orders", ordersRouter);

app.use(errorHandler);

const port = Number(process.env.PORT || 4000);
app.listen(port, () => log.info({ port }, "Orders API listening"));