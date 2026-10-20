// Culture Atlas submissions backend: a Cloudflare Worker with one KV namespace.
//
// Everything a reader sends with Share information is kept as pending and is
// never shown until the editor approves it on admin.html. Approved notes are
// served to the page from GET /approved.
//
// Bindings (see worker/wrangler.toml and the README):
//   SUBMISSIONS      KV namespace
//   ADMIN_TOKEN      secret; the password for admin.html
//   ALLOWED_ORIGINS  comma-separated origins allowed to call the API
//
// Chat: POST /chat forwards a conversation to Claude so the page can answer like a model. The Anthropic key lives here
// as the secret ANTHROPIC_API_KEY and never reaches the browser. Only a short allowlist of models is accepted, the
// reply length and the conversation size are capped, and each address gets CHATS_PER_HOUR answers an hour.
//
// KV layout:
//   pending:<id>   one pending submission (JSON)
//   approved       every approved note, newest first (one JSON array, so the page reads it in one go)
//   rate:<hash>    sends from one address in the current hour (expires on its own)

// Whistleblower notes are not accepted here. They go to the report API (server/), which holds them for approval too.
const KINDS = ['information', 'gossip'];
const MAX_TEXT = 5000;
const MAX_FIELD = 200;
const SENDS_PER_HOUR = 10;
const CHAT_MODELS = ['claude-haiku-4-5-20251001', 'claude-sonnet-4-5-20250929'];
const CHAT_MAX_TOKENS = 1500;
const CHAT_MAX_TURNS = 16;
const CHAT_MAX_CHARS = 150000;
const CHATS_PER_HOUR = 30;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const cors = corsHeaders(request, env);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    try {
      const res = await route(request, env, url);
      for (const [k, v] of Object.entries(cors)) res.headers.set(k, v);
      return res;
    } catch (err) {
      return json({ error: 'Something went wrong on the server.' }, 500, cors);
    }
  }
};

async function route(request, env, url) {
  const path = url.pathname.replace(/\/+$/, '') || '/';
  const m = request.method;

  if (path === '/submissions' && m === 'POST') return submit(request, env);
  if (path === '/approved' && m === 'GET') return listApproved(env);
  if (path === '/chat' && m === 'POST') return chat(request, env);

  if (path.startsWith('/admin/')) {
    if (!(await isAdmin(request, env))) return json({ error: 'Wrong password.' }, 401);
    if (path === '/admin/pending' && m === 'GET') return listPending(env);
    if (path === '/admin/approved' && m === 'GET') return listApproved(env, true);
    const act = path.match(/^\/admin\/submissions\/([A-Za-z0-9-]+)\/(approve|reject|unpublish)$/);
    if (act && m === 'POST') {
      const [, id, action] = act;
      if (action === 'approve') return approve(request, env, id);
      if (action === 'reject') return reject(env, id);
      return unpublish(env, id);
    }
  }
  return json({ error: 'Not found.' }, 404);
}

// A reader asks a question. The conversation is checked, trimmed to what the page may send, and passed to Claude.
async function chat(request, env) {
  if (!env.ANTHROPIC_API_KEY) return json({ error: 'The chat is not switched on.' }, 503);
  const origin = request.headers.get('Origin') || '';
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(x => x.trim()).filter(Boolean);
  if (origin && !allowed.includes(origin) && !/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return json({ error: 'Not allowed from here.' }, 403);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'Send JSON.' }, 400); }
  const turns = Array.isArray(body.messages) ? body.messages.slice(-CHAT_MAX_TURNS) : [];
  const messages = turns
    .filter(t => t && (t.role === 'user' || t.role === 'assistant') && typeof t.content === 'string' && t.content.trim())
    .map(t => ({ role: t.role, content: t.content }));
  while (messages.length && messages[0].role !== 'user') messages.shift();
  if (!messages.length || messages[messages.length - 1].role !== 'user') return json({ error: 'Ask something first.' }, 400);
  const system = typeof body.system === 'string' ? body.system : '';
  const size = system.length + messages.reduce((n, t) => n + t.content.length, 0);
  if (size > CHAT_MAX_CHARS) return json({ error: 'That conversation is too long.' }, 413);

  if (await overLimit(request, env, 'chat:', CHATS_PER_HOUR)) return json({ error: 'Too many questions from here this hour. Try again later.' }, 429);

  const model = CHAT_MODELS.includes(body.model) ? body.model : CHAT_MODELS[0];
  const maxTokens = Math.min(Math.max(parseInt(body.max_tokens, 10) || 1024, 64), CHAT_MAX_TOKENS);
  let res;
  try {
    res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model, max_tokens: maxTokens, system, messages }),
      signal: AbortSignal.timeout(60000)
    });
  } catch (e) {
    return json({ error: 'The model did not answer in time.' }, 504);
  }
  if (!res.ok) return json({ error: 'The model could not answer.' }, res.status === 429 ? 429 : 502);
  const data = await res.json();
  return json({ content: Array.isArray(data.content) ? data.content : [] }, 200, { 'Cache-Control': 'no-store' });
}

// A reader sends a note. It is stored as pending and nothing else happens.
async function submit(request, env) {
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'Send JSON.' }, 400); }
  // Bots fill the hidden "website" field; pretend it worked and store nothing.
  if (body.website) return json({ ok: true, id: newId() }, 201);

  const text = clean(body.text, MAX_TEXT);
  if (!text) return json({ error: 'Write something first.' }, 400);
  if (body.kind === 'whistleblower') return json({ error: 'Whistleblower notes are sent to the report service, not here.' }, 400);
  const kind = KINDS.includes(body.kind) ? body.kind : 'information';

  if (await overLimit(request, env)) return json({ error: 'Too many notes from here in the last hour. Try again later.' }, 429);

  const sub = {
    id: newId(),
    kind,
    text,
    spaceName: clean(body.spaceName, MAX_FIELD),
    sourceUrl: cleanUrl(body.sourceUrl),
    receivedAt: new Date().toISOString()
  };
  await env.SUBMISSIONS.put('pending:' + sub.id, JSON.stringify(sub));
  return json({ ok: true, id: sub.id }, 201);
}

async function listPending(env) {
  const out = [];
  let cursor;
  do {
    const page = await env.SUBMISSIONS.list({ prefix: 'pending:', cursor });
    const values = await Promise.all(page.keys.map(k => env.SUBMISSIONS.get(k.name, 'json')));
    values.forEach(v => { if (v) out.push(v); });
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  out.sort((a, b) => (a.receivedAt < b.receivedAt ? -1 : 1));
  return json({ submissions: out }, 200, { 'Cache-Control': 'no-store' });
}

async function listApproved(env, isEditor = false) {
  // A whistleblower note stored here before the report API took over is never served.
  const notes = ((await env.SUBMISSIONS.get('approved', 'json')) || []).filter(n => n.kind !== 'whistleblower');
  return json({ notes }, 200, { 'Cache-Control': isEditor ? 'no-store' : 'public, max-age=60' });
}

// The editor may correct the text or the space name before approving.
async function approve(request, env, id) {
  const sub = await env.SUBMISSIONS.get('pending:' + id, 'json');
  if (!sub) return json({ error: 'That note is no longer pending.' }, 404);
  if (sub.kind === 'whistleblower') return json({ error: 'Whistleblower notes cannot be approved here. Reject it; notes of this kind go through the report API.' }, 400);
  let edits = {};
  try { edits = await request.json(); } catch (e) {}
  const note = {
    id: sub.id,
    kind: sub.kind,
    text: clean(edits.text, MAX_TEXT) || sub.text,
    spaceName: edits.spaceName !== undefined ? clean(edits.spaceName, MAX_FIELD) : sub.spaceName,
    sourceUrl: edits.sourceUrl !== undefined ? cleanUrl(edits.sourceUrl) : sub.sourceUrl,
    receivedAt: sub.receivedAt,
    approvedAt: new Date().toISOString()
  };
  const approved = ((await env.SUBMISSIONS.get('approved', 'json')) || []).filter(n => n.id !== id);
  approved.unshift(note);
  await env.SUBMISSIONS.put('approved', JSON.stringify(approved));
  await env.SUBMISSIONS.delete('pending:' + id);
  return json({ ok: true, note });
}

// Rejected notes are deleted, not kept.
async function reject(env, id) {
  await env.SUBMISSIONS.delete('pending:' + id);
  return json({ ok: true });
}

async function unpublish(env, id) {
  const approved = (await env.SUBMISSIONS.get('approved', 'json')) || [];
  await env.SUBMISSIONS.put('approved', JSON.stringify(approved.filter(n => n.id !== id)));
  return json({ ok: true });
}

async function isAdmin(request, env) {
  const given = (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (!env.ADMIN_TOKEN || !given) return false;
  // Compare digests so the check takes the same time whatever was typed.
  const [a, b] = await Promise.all([sha256(given), sha256(env.ADMIN_TOKEN)]);
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Ten sends an hour from one address. Only a salted hash of the address is kept, for an hour.
async function overLimit(request, env, prefix = 'rate:', limit = SENDS_PER_HOUR) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const hour = Math.floor(Date.now() / 3600000);
  const key = prefix + (await sha256(ip + hour + (env.ADMIN_TOKEN || ''))).slice(0, 32);
  const count = parseInt((await env.SUBMISSIONS.get(key)) || '0', 10);
  if (count >= limit) return true;
  await env.SUBMISSIONS.put(key, String(count + 1), { expirationTtl: 3600 });
  return false;
}

function corsHeaders(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const ok = allowed.includes(origin) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);
  return ok ? {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  } : { 'Vary': 'Origin' };
}

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers } });
}

function clean(value, max) {
  return typeof value === 'string' ? value.replace(/\u0000/g, '').trim().slice(0, max) : '';
}

function cleanUrl(value) {
  const v = clean(value, 500);
  return /^https?:\/\/\S+$/i.test(v) ? v : '';
}

function newId() {
  return Date.now().toString(36) + '-' + crypto.randomUUID().slice(0, 8);
}

async function sha256(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}
