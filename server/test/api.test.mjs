import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, before, describe, test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { PrismaClient } from '@prisma/client';
import inject from 'light-my-request';
import { createApp } from '../app.js';
import { cleanText, loadInstitutions } from '../validate.js';

const root = fileURLToPath(new URL('../..', import.meta.url));
const require = createRequire(import.meta.url);
const SECRET = 'test-admin-secret-0123456789abcdef';
const NOTE = 'The press office asked staff to delete the complaint thread before the audit.';

let dir, prisma, app, institutions, place, other;

// The app is driven in-process, so the tests need no open port.
async function call(path, { method = 'GET', headers = {}, body } = {}) {
  const res = await inject(app, { method, url: path, headers, payload: body });
  return {
    status: res.statusCode,
    headers: { get: name => res.headers[name.toLowerCase()] ?? null },
    json: async () => JSON.parse(res.body)
  };
}

const path = id => `/api/places/${encodeURIComponent(id)}/reviews`;
const post = (body, headers = {}, id = place.id) => call(path(id), {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', ...headers },
  body: typeof body === 'string' ? body : JSON.stringify(body)
});
const admin = (route, options = {}) => call(route, {
  ...options,
  headers: {
    Authorization: `Bearer ${SECRET}`,
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {})
  }
});
const reviews = async (id = place.id) => (await call(path(id))).json();
const pending = async () => (await admin('/api/admin/reports/pending')).json();
const submit = async (extra = {}, id = place.id) => {
  const res = await post({ content: NOTE, ...extra }, {}, id);
  assert.equal(res.status, 201);
  return (await res.json()).id;
};
const setStatus = (id, status) => admin(`/api/admin/reports/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) });

function start(rateLimit) {
  app = createApp({ prisma, adminSecret: SECRET, institutions, allowedOrigins: [], rateLimit });
}
function stop() {
  app.locals.stop();
}

before(async () => {
  dir = mkdtempSync(join(tmpdir(), 'atlas-reports-'));
  const url = `file:${join(dir, 'test.db')}`;
  execFileSync(process.execPath, [require.resolve('prisma/build/index.js'), 'db', 'push', '--skip-generate', '--accept-data-loss'], {
    cwd: root, env: { ...process.env, DATABASE_URL: url }, stdio: 'pipe'
  });
  prisma = new PrismaClient({ datasourceUrl: url });
  institutions = loadInstitutions(join(root, 'institutions.json'));
  [place, other] = [...institutions.byId.values()].filter(e => e.city);
  start({ max: 1000, windowMs: 60_000 });
});

after(async () => {
  if (app) stop();
  if (prisma) await prisma.$disconnect();
  rmSync(dir, { recursive: true, force: true });
});

test('health check answers without touching the database', async () => {
  const res = await call('/healthz');
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { ok: true });
});

describe('submitting a review', () => {
  test('stores it as PENDING under the place and shows it nowhere public', async () => {
    const id = await submit({ authorLabel: 'Former registrar' });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
    assert.equal(row.placeId, place.id);
    assert.equal(row.institution, place.name);
    assert.equal(row.city, place.city);
    assert.equal(row.authorLabel, 'Former registrar');
    assert.ok(!(await reviews()).some(r => r.id === id));
    assert.ok((await pending()).some(r => r.id === id));
  });

  test('stores nothing that identifies the sender', async () => {
    const id = await submit();
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.deepEqual(Object.keys(row).sort(), [
      'authorLabel', 'city', 'content', 'createdAt', 'id', 'institution', 'latitude', 'longitude', 'placeId', 'rating', 'status', 'updatedAt'
    ]);
    assert.equal(row.authorLabel, null);
    assert.equal(row.rating, null);
    assert.ok(!JSON.stringify(row).includes('127.0.0.1'));
  });

  test('rejects an empty or whitespace-only review', async () => {
    for (const content of ['', '   \n  ', undefined, null, 42, '<b></b>']) {
      const res = await post({ content });
      assert.equal(res.status, 400, JSON.stringify(content));
    }
  });

  test('rejects a review that is too short or too long', async () => {
    assert.equal((await post({ content: 'Too short' })).status, 400);
    assert.equal((await post({ content: 'x'.repeat(2001) })).status, 400);
    assert.equal((await post({ content: 'x'.repeat(2000) })).status, 201);
  });

  test('the place comes from the address and must be on the atlas', async () => {
    assert.equal((await post({ content: NOTE }, {}, 'the-museum-of-nowhere')).status, 404);
    assert.equal((await post({ content: NOTE }, {}, 'x'.repeat(500))).status, 404);
    assert.equal((await call(path('the-museum-of-nowhere'))).status, 404);
    // a place named in the body is ignored
    const id = await submit({ institution: 'Somewhere else', placeId: other.id, city: 'Atlantis' });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.placeId, place.id);
    assert.equal(row.city, place.city);
  });

  test('a rating sent by the client is ignored: reviews have none', async () => {
    const id = await submit({ rating: 5 });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.rating, null);
  });

  test('the display name is optional, plain text and at most 40 characters', async () => {
    assert.equal((await post({ content: NOTE, authorLabel: 'x'.repeat(41) })).status, 400);
    assert.equal((await post({ content: NOTE, authorLabel: { a: 1 } })).status, 400);
    const id = await submit({ authorLabel: '  <b>Staff</b>\n member  ' });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.authorLabel, 'Staff member');
    const blank = await submit({ authorLabel: '   ' });
    assert.equal((await prisma.whistleblowerReport.findUnique({ where: { id: blank } })).authorLabel, null);
  });

  test('ignores coordinates, status and id sent by the client', async () => {
    const id = await submit({ status: 'APPROVED', latitude: 10, longitude: 20, id: 'mine' });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
    assert.equal(row.latitude, null);
    assert.equal(row.longitude, null);
    assert.notEqual(id, 'mine');
  });

  test('trims and strips HTML before saving', async () => {
    const res = await post({ content: '  <script>alert(1)</script><p>They <b>shredded</b> the files</p> <img src=x onerror=alert(1)>  ' });
    assert.equal(res.status, 201);
    const row = await prisma.whistleblowerReport.findUnique({ where: { id: (await res.json()).id } });
    assert.equal(row.content, 'They shredded the files');
  });

  test('rejects invalid JSON', async () => {
    assert.equal((await post('{nope')).status, 400);
  });

  test('the old note routes are gone', async () => {
    assert.equal((await call('/api/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: NOTE, institution: place.name }) })).status, 404);
    assert.equal((await call('/api/map/approved-reports')).status, 404);
  });
});

describe('listing a place', () => {
  test('shows approved reviews of that place only, newest first, with only review fields', async () => {
    const older = await submit({ authorLabel: 'Visitor' });
    await new Promise(resolve => setTimeout(resolve, 15));
    const newer = await submit();
    const elsewhere = await submit({}, other.id);
    const waiting = await submit();
    for (const id of [older, newer, elsewhere]) assert.equal((await setStatus(id, 'APPROVED')).status, 200);

    const list = await reviews();
    const ids = list.map(r => r.id);
    assert.ok(ids.includes(older) && ids.includes(newer));
    assert.ok(ids.indexOf(newer) < ids.indexOf(older));
    assert.ok(!ids.includes(elsewhere) && !ids.includes(waiting));
    for (const r of list) assert.deepEqual(Object.keys(r).sort(), ['authorLabel', 'content', 'createdAt', 'id']);
    const first = list.find(r => r.id === older);
    assert.equal(first.authorLabel, 'Visitor');
    assert.ok((await reviews(other.id)).some(r => r.id === elsewhere));
    assert.ok(!(await pending()).some(r => r.id === older || r.id === newer));
  });

  test('a review stored before places had ids is found by the place name', async () => {
    const row = await prisma.whistleblowerReport.create({
      data: { content: NOTE, city: place.city, institution: place.name, status: 'APPROVED' }
    });
    assert.ok((await reviews()).some(r => r.id === row.id));
    assert.ok(!(await reviews(other.id)).some(r => r.id === row.id));
  });

  test('a rejected review never appears publicly', async () => {
    const id = await submit();
    assert.equal((await setStatus(id, 'REJECTED')).status, 200);
    assert.ok(!(await reviews()).some(r => r.id === id));
    assert.ok(!(await pending()).some(r => r.id === id));
    const rejected = await (await admin('/api/admin/reports?status=rejected')).json();
    assert.ok(rejected.some(r => r.id === id));
  });

  test('taking a review back to PENDING removes it from the place', async () => {
    const id = await submit();
    await setStatus(id, 'APPROVED');
    assert.ok((await reviews()).some(r => r.id === id));
    await setStatus(id, 'PENDING');
    assert.ok(!(await reviews()).some(r => r.id === id));
  });

  test('is never cached', async () => {
    assert.equal((await call(path(place.id))).headers.get('cache-control'), 'no-store');
  });
});

describe('moderating', () => {
  test('status changes accept only known statuses and existing notes', async () => {
    const id = await submit();
    assert.equal((await setStatus(id, 'LIVE')).status, 400);
    assert.equal((await setStatus('nope', 'APPROVED')).status, 404);
    assert.equal((await admin('/api/admin/reports?status=LIVE')).status, 400);
  });

  test('the moderator sees the name the sender gave', async () => {
    const id = await submit({ authorLabel: 'Ex-intern' });
    const row = (await pending()).find(r => r.id === id);
    assert.equal(row.authorLabel, 'Ex-intern');
    assert.equal(row.placeId, place.id);
  });

  test('delete removes a pending and an approved review entirely', async () => {
    const waiting = await submit();
    const live = await submit();
    await setStatus(live, 'APPROVED');
    assert.ok((await reviews()).some(r => r.id === live));

    for (const id of [waiting, live]) {
      const res = await admin(`/api/admin/reports/${id}`, { method: 'DELETE' });
      assert.equal(res.status, 200);
      assert.equal(await prisma.whistleblowerReport.findUnique({ where: { id } }), null);
    }
    assert.ok(!(await reviews()).some(r => r.id === live));
    assert.ok(!(await pending()).some(r => r.id === waiting));
    assert.equal((await admin(`/api/admin/reports/${live}`, { method: 'DELETE' })).status, 404);
  });
});

describe('admin routes need the bearer token', () => {
  test('refuse a missing, wrong or malformed token', async () => {
    const id = await submit();
    const routes = [
      ['GET', '/api/admin/reports/pending'],
      ['GET', '/api/admin/reports'],
      ['PATCH', `/api/admin/reports/${id}/status`],
      ['DELETE', `/api/admin/reports/${id}`]
    ];
    for (const [method, route] of routes) {
      for (const authorization of [undefined, 'Bearer wrong', `Bearer ${SECRET}x`, SECRET, 'Basic abc']) {
        const res = await call(route, {
          method,
          headers: { 'Content-Type': 'application/json', ...(authorization ? { Authorization: authorization } : {}) },
          body: method === 'PATCH' ? JSON.stringify({ status: 'APPROVED' }) : undefined
        });
        assert.equal(res.status, 401, `${method} ${route} with ${authorization}`);
      }
    }
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
  });
});

describe('rate limit', () => {
  test('stops one sender after the limit, across places, and counts only accepted reviews', async () => {
    stop();
    start({ max: 2, windowMs: 60_000 });
    assert.equal((await post({ content: 'bad' })).status, 400);
    assert.equal((await post({ content: NOTE })).status, 201);
    assert.equal((await post({ content: NOTE }, {}, other.id)).status, 201);
    const third = await post({ content: NOTE });
    assert.equal(third.status, 429);
    assert.ok(Number(third.headers.get('retry-after')) > 0);
  });
});

describe('logging', () => {
  test('a database failure logs its kind, never the review text or the sender address', async () => {
    const failing = { whistleblowerReport: { create: async ({ data }) => { throw Object.assign(new Error(`Invalid create: ${data.content}`), { code: 'P2002' }); } } };
    const broken = createApp({ prisma: failing, adminSecret: SECRET, institutions, allowedOrigins: [] });
    const lines = [];
    const original = console.error;
    console.error = (...args) => lines.push(args.map(String).join(' '));
    try {
      const res = await inject(broken, { method: 'POST', url: path(place.id), headers: { 'Content-Type': 'application/json' }, remoteAddress: '203.0.113.9', payload: JSON.stringify({ content: NOTE }) });
      assert.equal(res.statusCode, 500);
      assert.ok(!res.body.includes('shredded') && !res.body.includes(NOTE));
    } finally {
      console.error = original;
      broken.locals.stop();
    }
    assert.equal(lines.length, 1);
    assert.ok(!lines[0].includes(NOTE.slice(0, 20)) && !lines[0].includes('203.0.113.9'), lines[0]);
    assert.match(lines[0], /P2002/);
  });
});

describe('cleanText', () => {
  test('removes markup, control characters and extra whitespace', () => {
    assert.equal(cleanText('  a\u0000b \t c  '), 'ab c');
    assert.equal(cleanText('one\n\n\n\ntwo'), 'one\n\ntwo');
    assert.equal(cleanText('<style>p{}</style>text<!-- x -->'), 'text');
    assert.equal(cleanText('1 < 2 and 3 > 2'), '1 2 and 3 2');
    assert.equal(cleanText(null), '');
  });
});
