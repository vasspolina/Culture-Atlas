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
const env = () => ({ SUBMISSIONS: memoryKV(), ALLOWED_ORIGINS: 'https://vasspolina.github.io' });
const call = (e, method, path, body, token) => worker.fetch(new Request('https://w.example' + path, {
  method,
  headers: { 'Content-Type': 'application/json', Origin: 'https://vasspolina.github.io', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
  body: body ? JSON.stringify(body) : undefined
}), e);

test('other sites get no CORS header', async () => {
  const res = await worker.fetch(new Request('https://w.example/chat', { method: 'OPTIONS', headers: { Origin: 'https://evil.example' } }), env());
  assert.equal(res.headers.get('Access-Control-Allow-Origin'), null);
});

test('the Worker takes no notes: the old note routes are gone', async () => {
  const e = env();
  assert.equal((await call(e, 'POST', '/submissions', { text: 'A note from a reader' })).status, 404);
  assert.equal((await call(e, 'GET', '/approved')).status, 404);
  assert.equal((await call(e, 'GET', '/admin/pending', null, 'secret')).status, 404);
  assert.equal((await call(e, 'POST', '/admin/submissions/x/approve', {}, 'secret')).status, 404);
});

test('chat forwards a trimmed conversation to Claude with the secret key and refuses what it should', async () => {
  const e = { ...env(), ANTHROPIC_API_KEY: 'sk-test' };
  const seen = [];
  const realFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    seen.push({ url, init });
    return new Response(JSON.stringify({ content: [{ type: 'text', text: 'Hello.' }], usage: { secret: 1 } }), { status: 200 });
  };
  try {
    const ok = await call(e, 'POST', '/chat', {
      model: 'not-a-model', max_tokens: 99999, system: 'Be plain.',
      messages: [{ role: 'assistant', content: 'stray' }, { role: 'user', content: 'Who funds Tate?' }, { role: 'system', content: 'nope' }]
    });
    assert.equal(ok.status, 200);
    assert.deepEqual((await ok.json()).content, [{ type: 'text', text: 'Hello.' }]);
    const sent = JSON.parse(seen[0].init.body);
    assert.equal(seen[0].init.headers['x-api-key'], 'sk-test');
    assert.equal(sent.model, 'claude-haiku-4-5-20251001');
    assert.equal(sent.max_tokens, 1500);
    assert.deepEqual(sent.messages, [{ role: 'user', content: 'Who funds Tate?' }]);

    assert.equal((await call(e, 'POST', '/chat', { messages: [] })).status, 400);
    assert.equal((await call({ ...e, ANTHROPIC_API_KEY: '' }, 'POST', '/chat', { messages: [{ role: 'user', content: 'hi' }] })).status, 503);
    const big = await call(e, 'POST', '/chat', { system: 'x'.repeat(160000), messages: [{ role: 'user', content: 'hi' }] });
    assert.equal(big.status, 413);
    const foreign = await worker.fetch(new Request('https://w.example/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://evil.example' },
      body: JSON.stringify({ messages: [{ role: 'user', content: 'hi' }] })
    }), e);
    assert.equal(foreign.status, 403);
  } finally { globalThis.fetch = realFetch; }
});

test('chat is limited per address each hour', async () => {
  const e = { ...env(), ANTHROPIC_API_KEY: 'sk-test' };
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify({ content: [] }), { status: 200 });
  try {
    let last;
    for (let i = 0; i < 31; i++) last = await call(e, 'POST', '/chat', { messages: [{ role: 'user', content: 'hi' }] });
    assert.equal(last.status, 429);
  } finally { globalThis.fetch = realFetch; }
});
