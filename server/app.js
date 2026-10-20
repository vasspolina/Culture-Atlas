import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import cors from 'cors';
import express from 'express';
import { Prisma } from '@prisma/client';
import { validateReport } from './validate.js';

const STATUSES = ['PENDING', 'APPROVED', 'REJECTED'];

// Counts submissions per sender for one window. The address is hashed with a salt that exists only in this
// process's memory, and neither the address nor the hash is written to the database or a log: when the process
// restarts the counts are gone.
function createRateLimiter({ max, windowMs }) {
  const salt = randomBytes(16);
  const hits = new Map();
  const sweep = setInterval(() => {
    const now = Date.now();
    for (const [key, entry] of hits) if (entry.resetAt <= now) hits.delete(key);
  }, Math.min(windowMs, 60_000));
  sweep.unref();
  return {
    take(address) {
      const key = createHash('sha256').update(salt).update(String(address || 'unknown')).digest('hex');
      const now = Date.now();
      let entry = hits.get(key);
      if (!entry || entry.resetAt <= now) {
        entry = { count: 0, resetAt: now + windowMs };
        hits.set(key, entry);
      }
      if (entry.count >= max) return { ok: false, retryAfter: Math.ceil((entry.resetAt - now) / 1000) };
      entry.count += 1;
      return { ok: true };
    },
    stop() { clearInterval(sweep); }
  };
}

export function createApp({
  prisma,
  adminSecret,
  institutions,
  allowedOrigins = [],
  trustProxy = false,
  rateLimit = { max: 5, windowMs: 60 * 60 * 1000 }
}) {
  if (!adminSecret) throw new Error('ADMIN_SECRET_KEY must be set before starting the report API.');
  const app = express();
  const limiter = createRateLimiter(rateLimit);
  app.locals.stop = () => limiter.stop();

  app.disable('x-powered-by');
  if (trustProxy) app.set('trust proxy', trustProxy);
  app.use(cors({
    origin(origin, callback) {
      if (!origin || allowedOrigins.includes(origin)) return callback(null, true);
      return callback(null, false);
    }
  }));
  app.use(express.json({ limit: '16kb' }));

  function requireAdminAuth(req, res, next) {
    const match = /^Bearer (.+)$/.exec(req.get('authorization') || '');
    const provided = Buffer.from(match?.[1] || '');
    const expected = Buffer.from(adminSecret);
    if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
      return res.status(401).json({ error: 'Unauthorized admin access.' });
    }
    return next();
  }

  // The only way a note enters the system. It is stored PENDING; nothing public reads PENDING rows.
  app.post('/api/reports', async (req, res, next) => {
    const result = validateReport(req.body, institutions);
    if (result.error) return res.status(400).json({ error: result.error });

    const turn = limiter.take(req.ip);
    if (!turn.ok) {
      res.set('Retry-After', String(turn.retryAfter));
      return res.status(429).json({ error: 'Too many notes from here. Try again later.' });
    }

    try {
      const report = await prisma.whistleblowerReport.create({
        data: { ...result.data, status: 'PENDING' },
        select: { id: true }
      });
      return res.status(201).json({
        message: 'Report submitted successfully for review.',
        id: report.id
      });
    } catch (error) {
      return next(error);
    }
  });

  // What the atlas shows: approved notes only, and only the fields a review needs.
  app.get('/api/map/approved-reports', async (req, res, next) => {
    const { city, institution } = req.query;
    for (const [field, value] of [['City', city], ['Institution', institution]]) {
      if (value !== undefined && (typeof value !== 'string' || value.length > 200)) {
        return res.status(400).json({ error: `${field} must be a string no longer than 200 characters.` });
      }
    }
    try {
      const reports = await prisma.whistleblowerReport.findMany({
        where: {
          status: 'APPROVED',
          ...(city ? { city } : {}),
          ...(institution ? { institution } : {})
        },
        select: { id: true, city: true, institution: true, content: true, createdAt: true },
        orderBy: { createdAt: 'desc' }
      });
      res.set('Cache-Control', 'no-store');
      return res.json(reports);
    } catch (error) {
      return next(error);
    }
  });

  async function listByStatus(status, res, next) {
    try {
      const reports = await prisma.whistleblowerReport.findMany({
        where: { status },
        orderBy: { createdAt: 'desc' }
      });
      res.set('Cache-Control', 'no-store');
      return res.json(reports);
    } catch (error) {
      return next(error);
    }
  }

  app.get('/api/admin/reports/pending', requireAdminAuth, (_req, res, next) => listByStatus('PENDING', res, next));

  app.get('/api/admin/reports', requireAdminAuth, (req, res, next) => {
    const status = String(req.query.status || 'PENDING').toUpperCase();
    if (!STATUSES.includes(status)) return res.status(400).json({ error: 'Status must be PENDING, APPROVED or REJECTED.' });
    return listByStatus(status, res, next);
  });

  app.patch('/api/admin/reports/:id/status', requireAdminAuth, async (req, res, next) => {
    const { status } = req.body || {};
    if (!STATUSES.includes(status)) {
      return res.status(400).json({ error: 'Status must be PENDING, APPROVED or REJECTED.' });
    }
    try {
      const report = await prisma.whistleblowerReport.update({
        where: { id: req.params.id },
        data: { status }
      });
      return res.json({ message: `Report marked as ${status}.`, report });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
        return res.status(404).json({ error: 'Report not found.' });
      }
      return next(error);
    }
  });

  // Removes the row, whatever its status.
  app.delete('/api/admin/reports/:id', requireAdminAuth, async (req, res, next) => {
    try {
      await prisma.whistleblowerReport.delete({ where: { id: req.params.id } });
      return res.json({ message: 'Report deleted.' });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
        return res.status(404).json({ error: 'Report not found.' });
      }
      return next(error);
    }
  });

  app.use((error, _req, res, _next) => {
    if (error instanceof SyntaxError && 'body' in error) {
      return res.status(400).json({ error: 'Send valid JSON.' });
    }
    if (error.type === 'entity.too.large') {
      return res.status(413).json({ error: 'Request body is too large.' });
    }
    console.error('Report API request failed:', error);
    return res.status(500).json({ error: 'The report API could not complete the request.' });
  });

  return app;
}
