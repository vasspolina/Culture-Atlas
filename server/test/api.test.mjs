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

let dir, prisma, app, institutions, institution, city;

// The app is driven in-process, so the tests need no open port.
async function call(path, { method = 'GET', headers = {}, body } = {}) {
  const res = await inject(app, { method, url: path, headers, payload: body });
  return {
    status: res.statusCode,
    headers: { get: name => res.headers[name.toLowerCase()] ?? null },
    json: async () => JSON.parse(res.body)
  };
}

const post = (body, headers = {}) => call(`/api/reports`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', ...headers },
  body: typeof body === 'string' ? body : JSON.stringify(body)
});
const admin = (path, options = {}) => call(`${path}`, {
  ...options,
  headers: {
    Authorization: `Bearer ${SECRET}`,
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {})
  }
});
const approved = async () => (await call(`/api/map/approved-reports`)).json();
const pending = async () => (await admin('/api/admin/reports/pending')).json();
const submit = async (extra = {}) => {
  const res = await post({ content: NOTE, institution, ...extra });
  assert.equal(res.status, 201);
  return (await res.json()).id;
};

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
  [institution, { city }] = [...institutions.byName.values()].map(e => [e.name, e]).find(([, e]) => e.city) ;
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

describe('submitting', () => {
  test('stores the note as PENDING and shows it nowhere public', async () => {
    const id = await submit();
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
    assert.equal(row.institution, institution);
    assert.equal(row.city, city);
    assert.ok(!(await approved()).some(r => r.id === id));
    assert.ok((await pending()).some(r => r.id === id));
  });

  test('stores nothing that identifies the sender', async () => {
    const id = await submit();
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.deepEqual(Object.keys(row).sort(), ['city', 'content', 'createdAt', 'id', 'institution', 'latitude', 'longitude', 'status', 'updatedAt']);
    assert.ok(!JSON.stringify(row).includes('127.0.0.1'));
  });

  test('rejects an empty or whitespace-only note', async () => {
    for (const content of ['', '   \n  ', undefined, null, 42, '<b></b>']) {
      const res = await post({ content, institution });
      assert.equal(res.status, 400, JSON.stringify(content));
    }
  });

  test('rejects a note that is too short or too long', async () => {
    assert.equal((await post({ content: 'Too short', institution })).status, 400);
    assert.equal((await post({ content: 'x'.repeat(2001), institution })).status, 400);
    assert.equal((await post({ content: 'x'.repeat(2000), institution })).status, 201);
  });

  test('requires an institution or city and matches it to the atlas', async () => {
    assert.equal((await post({ content: NOTE })).status, 400);
    assert.equal((await post({ content: NOTE, institution: 'The Museum of Nowhere' })).status, 400);
    assert.equal((await post({ content: NOTE, city: 'Atlantis' })).status, 400);
    assert.equal((await post({ content: NOTE, institution: { $ne: '' } })).status, 400);
    assert.equal((await post({ content: NOTE, institution: institution.toUpperCase() })).status, 201);
    const res = await post({ content: NOTE, city: city.toLowerCase() });
    assert.equal(res.status, 201);
    const row = await prisma.whistleblowerReport.findUnique({ where: { id: (await res.json()).id } });
    assert.equal(row.city, city);
    assert.equal(row.institution, null);
  });

  test('ignores coordinates and status sent by the client', async () => {
    const id = await submit({ status: 'APPROVED', latitude: 10, longitude: 20, id: 'mine' });
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
    assert.equal(row.latitude, null);
    assert.equal(row.longitude, null);
    assert.notEqual(id, 'mine');
  });

  test('trims and strips HTML before saving', async () => {
    const res = await post({ content: '  <script>alert(1)</script><p>They <b>shredded</b> the files</p> <img src=x onerror=alert(1)>  ', institution });
    assert.equal(res.status, 201);
    const row = await prisma.whistleblowerReport.findUnique({ where: { id: (await res.json()).id } });
    assert.equal(row.content, 'They shredded the files');
  });

  test('rejects invalid JSON', async () => {
    assert.equal((await post('{nope')).status, 400);
  });
});

describe('approving, rejecting and deleting', () => {
  test('an approved note appears on the public endpoint, newest first, with only review fields', async () => {
    const older = await submit();
    await new Promise(resolve => setTimeout(resolve, 15));
    const newer = await submit();
    for (const id of [older, newer]) {
      const res = await admin(`/api/admin/reports/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'APPROVED' }) });
      assert.equal(res.status, 200);
    }
    const list = await approved();
    const ids = list.map(r => r.id);
    assert.ok(ids.indexOf(newer) < ids.indexOf(older));
    assert.deepEqual(Object.keys(list[0]).sort(), ['city', 'content', 'createdAt', 'id', 'institution']);
    assert.ok(!(await pending()).some(r => r.id === older || r.id === newer));
    const filtered = await (await call(`/api/map/approved-reports?institution=${encodeURIComponent(institution)}`)).json();
    assert.ok(filtered.length >= 2 && filtered.every(r => r.institution === institution));
  });

  test('a rejected note never appears publicly', async () => {
    const id = await submit();
    const res = await admin(`/api/admin/reports/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'REJECTED' }) });
    assert.equal(res.status, 200);
    assert.ok(!(await approved()).some(r => r.id === id));
    assert.ok(!(await pending()).some(r => r.id === id));
    const rejected = await (await admin('/api/admin/reports?status=rejected')).json();
    assert.ok(rejected.some(r => r.id === id));
  });

  test('status changes accept only known statuses and existing notes', async () => {
    const id = await submit();
    assert.equal((await admin(`/api/admin/reports/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'LIVE' }) })).status, 400);
    assert.equal((await admin('/api/admin/reports/nope/status', { method: 'PATCH', body: JSON.stringify({ status: 'APPROVED' }) })).status, 404);
    assert.equal((await admin('/api/admin/reports?status=LIVE')).status, 400);
  });

  test('delete removes a pending and an approved note entirely', async () => {
    const waiting = await submit();
    const live = await submit();
    await admin(`/api/admin/reports/${live}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'APPROVED' }) });
    assert.ok((await approved()).some(r => r.id === live));

    for (const id of [waiting, live]) {
      const res = await admin(`/api/admin/reports/${id}`, { method: 'DELETE' });
      assert.equal(res.status, 200);
      assert.equal(await prisma.whistleblowerReport.findUnique({ where: { id } }), null);
    }
    assert.ok(!(await approved()).some(r => r.id === live));
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
    for (const [method, path] of routes) {
      for (const authorization of [undefined, 'Bearer wrong', `Bearer ${SECRET}x`, SECRET, 'Basic abc']) {
        const res = await call(path, {
          method,
          headers: { 'Content-Type': 'application/json', ...(authorization ? { Authorization: authorization } : {}) },
          body: method === 'PATCH' ? JSON.stringify({ status: 'APPROVED' }) : undefined
        });
        assert.equal(res.status, 401, `${method} ${path} with ${authorization}`);
      }
    }
    const row = await prisma.whistleblowerReport.findUnique({ where: { id } });
    assert.equal(row.status, 'PENDING');
  });
});

describe('rate limit', () => {
  test('stops one sender after the limit and counts only accepted notes', async () => {
    stop();
    start({ max: 2, windowMs: 60_000 });
    assert.equal((await post({ content: 'bad', institution })).status, 400);
    assert.equal((await post({ content: NOTE, institution })).status, 201);
    assert.equal((await post({ content: NOTE, institution })).status, 201);
    const third = await post({ content: NOTE, institution });
    assert.equal(third.status, 429);
    assert.ok(Number(third.headers.get('retry-after')) > 0);
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
