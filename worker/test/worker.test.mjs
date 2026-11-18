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

// A stand-in for the Workers AI binding that records what it was asked and answers as the model would.
function fakeAI(answer = { response: 'Hello.' }) {
  const seen = [];
  return { seen, async run(model, input) { seen.push({ model, input }); if (answer instanceof Error) throw answer; return answer; } };
}

test('chat sends a trimmed conversation to the small model and refuses what it should', async () => {
  const ai = fakeAI();
  const e = { ...env(), AI: ai };
  const ok = await call(e, 'POST', '/chat', {
    model: 'claude-sonnet-5-5', max_tokens: 99999, system: 'Be plain.',
    messages: [{ role: 'assistant', content: 'stray' }, { role: 'user', content: 'Who funds Tate?' }, { role: 'system', content: 'nope' }]
  });
  assert.equal(ok.status, 200);
  assert.deepEqual((await ok.json()).content, [{ type: 'text', text: 'Hello.' }]);
  assert.equal(ai.seen[0].model, '@cf/ibm-granite/granite-4.0-h-micro');
  assert.equal(ai.seen[0].input.max_tokens, 2000);
  assert.deepEqual(ai.seen[0].input.messages, [{ role: 'system', content: 'Be plain.' }, { role: 'user', content: 'Who funds Tate?' }]);

  assert.equal((await call(e, 'POST', '/chat', { messages: [] })).status, 400);
  assert.equal((await call({ ...env() }, 'POST', '/chat', { messages: [{ role: 'user', content: 'hi' }] })).status, 503);
  const big = await call(e, 'POST', '/chat', { system: 'x'.repeat(160000), messages: [{ role: 'user', content: 'hi' }] });
  assert.equal(big.status, 413);
  const foreign = await worker.fetch(new Request('https://w.example/chat', {
    method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://evil.example' },
    body: JSON.stringify({ messages: [{ role: 'user', content: 'hi' }] })
  }), e);
  assert.equal(foreign.status, 403);
});

test('chat reads an OpenAI-style answer too, and a failed or empty answer is a 502', async () => {
  const chatWith = (answer) => call({ ...env(), AI: fakeAI(answer) }, 'POST', '/chat', { messages: [{ role: 'user', content: 'hi' }] });
  const openai = await chatWith({ choices: [{ message: { role: 'assistant', content: ' Tate is funded by... ' } }] });
  assert.deepEqual((await openai.json()).content, [{ type: 'text', text: 'Tate is funded by...' }]);
  assert.equal((await chatWith({ response: '' })).status, 502);
  assert.equal((await chatWith(new Error('model failed'))).status, 502);
});

test('chat is limited per address each hour', async () => {
  const e = { ...env(), AI: fakeAI() };
  let last;
  for (let i = 0; i < 31; i++) last = await call(e, 'POST', '/chat', { messages: [{ role: 'user', content: 'hi' }] });
  assert.equal(last.status, 429);
});
