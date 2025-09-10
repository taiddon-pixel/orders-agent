import pino from "pino";
import pinoPretty from "pino-pretty";

const stream = pinoPretty({ colorize: true, translateTime: true });
export const log = pino({}, stream as any);