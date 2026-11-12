import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import cors from 'cors';
import express from 'express';
import { Prisma } from '@prisma/client';
import { FILE_TYPES, validateFiles } from './files.js';
import { findPlace, validateReview } from './validate.js';

const STATUSES = ['PENDING', 'APPROVED', 'REJECTED'];
const MAX_PUBLIC_REVIEWS = 200;
const FILE_META = { select: { id: true, type: true, size: true }, orderBy: { position: 'asc' } };
const REVIEW_PATH = /^\/api\/places\/[^/]+\/reviews\/?$/;

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
  // A review may carry up to 12 MB of files as base64, so its route takes a larger body; every other route stays small.
  const smallJson = express.json({ limit: '16kb' });
  const reviewJson = express.json({ limit: '18mb' });
  app.use((req, res, next) => (req.method === 'POST' && REVIEW_PATH.test(req.path) ? reviewJson : smallJson)(req, res, next));

  function requireAdminAuth(req, res, next) {
    const match = /^Bearer (.+)$/.exec(req.get('authorization') || '');
    const provided = Buffer.from(match?.[1] || '');
    const expected = Buffer.from(adminSecret);
    if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
      return res.status(401).json({ error: 'Unauthorized admin access.' });
    }
    return next();
  }

  // For the host's health check. Touches nothing.
  app.get('/healthz', (_req, res) => res.json({ ok: true }));

  // The only way a review enters the system. It is stored PENDING; nothing public reads PENDING rows.
  app.post('/api/places/:placeId/reviews', async (req, res, next) => {
    const place = findPlace(req.params.placeId, institutions);
    if (!place) return res.status(404).json({ error: 'That place is not on the atlas.' });
    const result = validateReview(req.body, place);
    if (result.error) return res.status(400).json({ error: result.error });
    const attached = validateFiles(req.body?.files);
    if (attached.error) return res.status(400).json({ error: attached.error });

    const turn = limiter.take(req.ip);
    if (!turn.ok) {
      res.set('Retry-After', String(turn.retryAfter));
      return res.status(429).json({ error: 'Too many reviews from here. Try again later.' });
    }

    try {
      const report = await prisma.whistleblowerReport.create({
        data: {
          ...result.data,
          status: 'PENDING',
          files: { create: attached.files.map((file, position) => ({ ...file, position })) }
        },
        select: { id: true }
      });
      return res.status(201).json({
        message: 'Review submitted for the editor to read. It appears here once approved.',
        id: report.id
      });
    } catch (error) {
      return next(error);
    }
  });

  // What a place shows: its approved reviews, newest first, and only the fields a review needs. Reviews stored before
  // places had ids carry the place's name and no id, so they are matched by name.
  app.get('/api/places/:placeId/reviews', async (req, res, next) => {
    const place = findPlace(req.params.placeId, institutions);
    if (!place) return res.status(404).json({ error: 'That place is not on the atlas.' });
    try {
      const reviews = await prisma.whistleblowerReport.findMany({
        where: {
          status: 'APPROVED',
          OR: [{ placeId: place.id }, { placeId: null, institution: place.name }]
        },
        select: { id: true, authorLabel: true, content: true, createdAt: true, files: FILE_META },
        orderBy: { createdAt: 'desc' },
        take: MAX_PUBLIC_REVIEWS
      });
      res.set('Cache-Control', 'no-store');
      return res.json(reviews);
    } catch (error) {
      return next(error);
    }
  });

  async function listByStatus(status, res, next) {
    try {
      const reports = await prisma.whistleblowerReport.findMany({
        where: { status },
        orderBy: { createdAt: 'desc' },
        include: { files: FILE_META }
      });
      res.set('Cache-Control', 'no-store');
      return res.json(reports);
    } catch (error) {
      return next(error);
    }
  }

  // One attached file. The public route answers only while the review is approved; the admin route answers for any
  // status. The browser is told the type and never to guess another, and an image may not run anything.
  async function sendFile(req, res, next, { publicOnly }) {
    try {
      const file = await prisma.reportFile.findUnique({
        where: { id: req.params.fileId },
        include: { report: { select: { status: true } } }
      });
      if (!file || (publicOnly && file.report.status !== 'APPROVED')) return res.status(404).json({ error: 'File not found.' });
      res.set({
        'Content-Type': file.type,
        'Content-Length': String(file.data.length),
        'Content-Disposition': `inline; filename="atlas-file-${file.id}.${FILE_TYPES[file.type] || 'bin'}"`,
        'X-Content-Type-Options': 'nosniff',
        'Cross-Origin-Resource-Policy': 'cross-origin',
        'Cache-Control': publicOnly ? 'public, max-age=300' : 'no-store'
      });
      if (file.type.startsWith('image/')) res.set('Content-Security-Policy', "default-src 'none'; sandbox");
      return res.end(Buffer.from(file.data));
    } catch (error) {
      return next(error);
    }
  }

  app.get('/api/files/:fileId', (req, res, next) => sendFile(req, res, next, { publicOnly: true }));
  app.get('/api/admin/files/:fileId', requireAdminAuth, (req, res, next) => sendFile(req, res, next, { publicOnly: false }));

  // Removes one file from a review, so the editor can approve the text and keep a file off the atlas.
  app.delete('/api/admin/files/:fileId', requireAdminAuth, async (req, res, next) => {
    try {
      await prisma.reportFile.delete({ where: { id: req.params.fileId } });
      return res.json({ message: 'File deleted.' });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
        return res.status(404).json({ error: 'File not found.' });
      }
      return next(error);
    }
  });

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
        data: { status },
        include: { files: FILE_META }
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
    // Only the kind of failure is logged. An error from the database can carry the data of the request, which is a
    // review, so the error itself is never printed.
    console.error('Report API request failed:', error?.name || 'Error', error?.code || '');
    return res.status(500).json({ error: 'The report API could not complete the request.' });
  });

  return app;
}
