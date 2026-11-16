// The data editor's server (tools/editor.py): a save writes only the edited record, keeps the file's format and number types,
// and refuses what other tools depend on not happening. Runs on a copy of institutions.json, never the file itself.
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { copyFileSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname;
const dir = mkdtempSync(join(tmpdir(), 'atlas-editor-'));
const file = join(dir, 'institutions.json');
copyFileSync(join(ROOT, 'institutions.json'), file);
const PORT = 18790 + Math.floor(Math.random() * 1000);
const base = `http://127.0.0.1:${PORT}`;
let server;

test.before(async () => {
  server = spawn('python3', [join(ROOT, 'tools/editor.py'), '--port', String(PORT)], { env: { ...process.env, INSTITUTIONS_FILE: file }, stdio: 'ignore' });
  for (let i = 0; i < 50; i++) {
    try { if ((await fetch(base + '/')).ok) return; } catch { /* not up yet */ }
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error('editor server did not start');
});
test.after(() => { server?.kill(); rmSync(dir, { recursive: true, force: true }); });

const put = (id, body, headers = {}) => fetch(`${base}/api/records/${encodeURIComponent(id)}`, {
  method: 'PUT', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body),
});

test('a save changes only the edited line and keeps whole-number floats', async () => {
  const before = readFileSync(file, 'utf8');
  const records = await (await fetch(base + '/api/records')).json();
  // Albertina stores its public money as 12983000.0, which the browser reads back as 12983000.
  const rec = records.find(r => r.id === 'albertina');
  assert.ok(before.includes('"public": 12983000.0'), 'the fixture float is still in the file');
  const edited = { ...rec, city: rec.city + ' (edited)' };
  const r = await put(rec.id, { record: edited, base: rec });
  assert.equal(r.status, 200);
  const after = readFileSync(file, 'utf8');
  const a = before.split('\n'), b = after.split('\n');
  assert.equal(a.length, b.length);
  const diff = a.map((l, i) => [l, b[i]]).filter(([x, y]) => x !== y);
  assert.equal(diff.length, 1);
  assert.match(diff[0][1], /\(edited\)/);
});

test('a stale base, a changed id, a missing name and bad coordinates are refused', async () => {
  const records = await (await fetch(base + '/api/records')).json();
  const rec = records[0];
  const stale = { ...rec, name: rec.name + ' x' };
  assert.equal((await put(rec.id, { record: rec, base: stale })).status, 409);
  assert.equal((await put(rec.id, { record: { ...rec, id: 'not-this' } })).status, 400);
  assert.equal((await put(rec.id, { record: { ...rec, name: ' ' } })).status, 400);
  assert.equal((await put(rec.id, { record: { ...rec, lat: 'north' } })).status, 400);
  assert.equal((await put(rec.id, { record: { ...rec, lon: 200 } })).status, 400);
});

test('requests from another site are refused', async () => {
  const records = await (await fetch(base + '/api/records')).json();
  const r = await put(records[0].id, { record: records[0] }, { Origin: 'https://example.com' });
  assert.equal(r.status, 403);
});

test('the lint reports wording points for a record', async () => {
  const records = await (await fetch(base + '/api/records')).json();
  const rec = { ...records[0], funding: 'A renowned museum — reportedly funded by many foundations.' };
  const found = await (await fetch(base + '/api/lint', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(rec) })).json();
  const kinds = found.filter(f => f.field === 'funding').map(f => f.problem.split(':')[0]);
  for (const k of ['dash', 'hedge', 'filler']) assert.ok(kinds.includes(k), k);
});
