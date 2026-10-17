// Run with `node --test worker/test/*.test.mjs`. Uses an in-memory stand-in for KV.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import worker from '../index.js';

function memoryKV() {
  const m = new Map();
  return {
    async get(k, type) { const v = m.has(k) ? m.get(k) : null; return v && type === 'json' ? JSON.parse(v) : v; },
    async put(k, v) { m.set(k, v); },
    async delete(k) { m.delete(k); },
    async list({ prefix }) { return { keys: [...m.keys()].filter(k => k.startsWith(prefix)).map(name => ({ name })), list_complete: true }; }
  };
}
const env = () => ({ SUBMISSIONS: memoryKV(), ADMIN_TOKEN: 'secret', ALLOWED_ORIGINS: 'https://vasspolina.github.io' });
const call = (e, method, path, body, token) => worker.fetch(new Request('https://w.example' + path, {
  method,
  headers: { 'Content-Type': 'application/json', Origin: 'https://vasspolina.github.io', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
  body: body ? JSON.stringify(body) : undefined
}), e);

test('a note stays hidden until it is approved', async () => {
  const e = env();
  const sent = await call(e, 'POST', '/submissions', { kind: 'gossip', text: 'Heard a thing', spaceName: 'Tate Modern' });
  assert.equal(sent.status, 201);
  assert.equal(sent.headers.get('Access-Control-Allow-Origin'), 'https://vasspolina.github.io');
  const { id } = await sent.json();
  assert.deepEqual((await (await call(e, 'GET', '/approved')).json()).notes, []);

  const pending = await (await call(e, 'GET', '/admin/pending', null, 'secret')).json();
  assert.equal(pending.submissions.length, 1);
  assert.equal(pending.submissions[0].text, 'Heard a thing');

  const ok = await call(e, 'POST', `/admin/submissions/${id}/approve`, { text: 'Edited thing' }, 'secret');
  assert.equal(ok.status, 200);
  const pub = (await (await call(e, 'GET', '/approved')).json()).notes;
  assert.equal(pub.length, 1);
  assert.equal(pub[0].text, 'Edited thing');
  assert.equal(pub[0].spaceName, 'Tate Modern');
  assert.equal((await (await call(e, 'GET', '/admin/pending', null, 'secret')).json()).submissions.length, 0);

  await call(e, 'POST', `/admin/submissions/${id}/unpublish`, null, 'secret');
  assert.deepEqual((await (await call(e, 'GET', '/approved')).json()).notes, []);
});

test('rejected notes are deleted', async () => {
  const e = env();
  const { id } = await (await call(e, 'POST', '/submissions', { text: 'spam' })).json();
  await call(e, 'POST', `/admin/submissions/${id}/reject`, null, 'secret');
  assert.equal((await (await call(e, 'GET', '/admin/pending', null, 'secret')).json()).submissions.length, 0);
  assert.deepEqual((await (await call(e, 'GET', '/approved')).json()).notes, []);
});

test('editor routes need the password', async () => {
  const e = env();
  assert.equal((await call(e, 'GET', '/admin/pending')).status, 401);
  assert.equal((await call(e, 'GET', '/admin/pending', null, 'wrong')).status, 401);
  assert.equal((await call(e, 'POST', '/admin/submissions/x/approve', {}, 'wrong')).status, 401);
});

test('empty notes, bots and floods are turned away', async () => {
  const e = env();
  assert.equal((await call(e, 'POST', '/submissions', { text: '   ' })).status, 400);
  assert.equal((await call(e, 'POST', '/submissions', { text: 'hi', website: 'spam.biz' })).status, 201);
  assert.equal((await (await call(e, 'GET', '/admin/pending', null, 'secret')).json()).submissions.length, 0);
  for (let i = 0; i < 10; i++) assert.equal((await call(e, 'POST', '/submissions', { text: 'n' + i })).status, 201);
  assert.equal((await call(e, 'POST', '/submissions', { text: 'one too many' })).status, 429);
});

test('other sites get no CORS header', async () => {
  const res = await worker.fetch(new Request('https://w.example/approved', { headers: { Origin: 'https://evil.example' } }), env());
  assert.equal(res.headers.get('Access-Control-Allow-Origin'), null);
});
