import { fileURLToPath } from 'node:url';
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { createApp } from './app.js';
import { loadInstitutions } from './validate.js';

const prisma = new PrismaClient();
const port = Number(process.env.PORT || 4000);
const adminSecret = process.env.ADMIN_SECRET_KEY || '';
const allowedOrigins = (process.env.ALLOWED_ORIGINS || '')
  .split(',')
  .map(origin => origin.trim())
  .filter(Boolean);
const institutionsFile = process.env.INSTITUTIONS_FILE
  || fileURLToPath(new URL('../institutions.json', import.meta.url));
// Set TRUST_PROXY to the number of proxies in front of the API (for example 1) so the rate limit sees the sender's address.
const trustProxy = process.env.TRUST_PROXY ? Number(process.env.TRUST_PROXY) : false;
const rateMax = Number(process.env.REPORTS_PER_HOUR || 5);

if (!adminSecret) {
  throw new Error('ADMIN_SECRET_KEY must be set before starting the report API.');
}
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT must be a valid TCP port.');
}
if (!Number.isInteger(rateMax) || rateMax < 1) {
  throw new Error('REPORTS_PER_HOUR must be a whole number of at least 1.');
}

const app = createApp({
  prisma,
  adminSecret,
  allowedOrigins,
  trustProxy,
  institutions: loadInstitutions(institutionsFile),
  rateLimit: { max: rateMax, windowMs: 60 * 60 * 1000 }
});

const server = app.listen(port, () => {
  console.log(`Whistleblower report API listening on port ${port}.`);
});

async function shutdown() {
  server.close(async () => {
    app.locals.stop();
    await prisma.$disconnect();
    process.exit(0);
  });
}

process.once('SIGINT', shutdown);
process.once('SIGTERM', shutdown);
