// Culture Atlas chat backend: a Cloudflare Worker with one KV namespace.
//
// POST /chat forwards a conversation to Claude so the page can answer like a model. The Anthropic key lives here
// as the secret ANTHROPIC_API_KEY and never reaches the browser. Only a short allowlist of models is accepted, the
// reply length and the conversation size are capped, and each address gets CHATS_PER_HOUR answers an hour.
//
// This Worker takes no notes and no reviews. Whistleblower reviews go to the report API (server/).
//
// Bindings (see worker/wrangler.toml and the README):
//   SUBMISSIONS      KV namespace (holds only the hourly rate counters)
//   ANTHROPIC_API_KEY secret
//   ALLOWED_ORIGINS  comma-separated origins allowed to call the API
//
// KV layout:
//   chat:<hash>    answers sent to one address in the current hour (expires on its own)

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

  if (path === '/chat' && m === 'POST') return chat(request, env);
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

// A fixed number of sends an hour from one address. Only a salted hash of the address is kept, for an hour.
async function overLimit(request, env, prefix, limit) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const hour = Math.floor(Date.now() / 3600000);
  const key = prefix + (await sha256(ip + hour + (env.ANTHROPIC_API_KEY || ''))).slice(0, 32);
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

async function sha256(s) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}
