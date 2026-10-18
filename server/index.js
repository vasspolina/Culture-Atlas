import { timingSafeEqual } from 'node:crypto';
import cors from 'cors';
import 'dotenv/config';
import express from 'express';
import { Prisma, PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
const app = express();
const port = Number(process.env.PORT || 4000);
const adminSecret = process.env.ADMIN_SECRET_KEY || '';
const allowedOrigins = (process.env.ALLOWED_ORIGINS || '')
  .split(',')
  .map(origin => origin.trim())
  .filter(Boolean);

if (!adminSecret) {
  throw new Error('ADMIN_SECRET_KEY must be set before starting the report API.');
}
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('PORT must be a valid TCP port.');
}

app.disable('x-powered-by');
app.use(cors({
  origin(origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) return callback(null, true);
    return callback(null, false);
  }
}));
app.use(express.json({ limit: '16kb' }));

function requireAdminAuth(req, res, next) {
  const auth = req.get('authorization') || '';
  const match = /^Bearer (.+)$/.exec(auth);
  const token = match?.[1] || '';
  const expected = Buffer.from(adminSecret);
  const provided = Buffer.from(token);

  if (provided.length !== expected.length || !timingSafeEqual(provided, expected)) {
    return res.status(401).json({ error: 'Unauthorized admin access.' });
  }
  return next();
}

function optionalText(value, field, maxLength, res) {
  if (value == null || value === '') return null;
  if (typeof value !== 'string' || value.trim().length > maxLength) {
    res.status(400).json({ error: `${field} must be a string no longer than ${maxLength} characters.` });
    return undefined;
  }
  return value.trim() || null;
}

function optionalCoordinate(value, field, min, max, res) {
  if (value == null || value === '') return null;
  const coordinate = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(coordinate) || coordinate < min || coordinate > max) {
    res.status(400).json({ error: `${field} must be a number between ${min} and ${max}.` });
    return undefined;
  }
  return coordinate;
}

app.post('/api/reports', async (req, res, next) => {
  const body = req.body || {};
  const { content } = body;
  if (typeof content !== 'string' || !content.trim()) {
    return res.status(400).json({ error: 'Content cannot be empty.' });
  }
  if (content.trim().length > 5000) {
    return res.status(400).json({ error: 'Content cannot exceed 5000 characters.' });
  }

  const city = optionalText(body.city, 'City', 200, res);
  const institution = optionalText(body.institution, 'Institution', 200, res);
  const latitude = optionalCoordinate(body.latitude, 'Latitude', -90, 90, res);
  const longitude = optionalCoordinate(body.longitude, 'Longitude', -180, 180, res);
  if ([city, institution, latitude, longitude].includes(undefined)) return;

  try {
    const report = await prisma.whistleblowerReport.create({
      data: {
        content: content.trim(),
        city: city || 'Unspecified',
        institution,
        latitude,
        longitude
      },
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

app.get('/api/map/approved-reports', async (req, res, next) => {
  const city = req.query.city;
  if (city !== undefined && (typeof city !== 'string' || city.length > 200)) {
    return res.status(400).json({ error: 'City must be a string no longer than 200 characters.' });
  }

  try {
    const reports = await prisma.whistleblowerReport.findMany({
      where: { status: 'APPROVED', ...(city ? { city } : {}) },
      select: {
        id: true,
        city: true,
        institution: true,
        content: true,
        latitude: true,
        longitude: true,
        createdAt: true
      },
      orderBy: { createdAt: 'desc' }
    });
    return res.json(reports);
  } catch (error) {
    return next(error);
  }
});

app.get('/api/admin/reports/pending', requireAdminAuth, async (_req, res, next) => {
  try {
    const reports = await prisma.whistleblowerReport.findMany({
      where: { status: 'PENDING' },
      orderBy: { createdAt: 'desc' }
    });
    return res.json(reports);
  } catch (error) {
    return next(error);
  }
});

app.patch('/api/admin/reports/:id/status', requireAdminAuth, async (req, res, next) => {
  const { status } = req.body || {};
  if (status !== 'APPROVED' && status !== 'REJECTED') {
    return res.status(400).json({ error: 'Status must be APPROVED or REJECTED.' });
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

const server = app.listen(port, () => {
  console.log(`Whistleblower report API listening on port ${port}.`);
});

async function shutdown() {
  server.close(async () => {
    await prisma.$disconnect();
    process.exit(0);
  });
}

process.once('SIGINT', shutdown);
process.once('SIGTERM', shutdown);
