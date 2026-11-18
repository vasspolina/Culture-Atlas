// Culture Atlas chat backend: a Cloudflare Worker with one KV namespace.
//
// POST /chat answers a conversation with a small open model on Cloudflare Workers AI (the AI binding), so no API key
// exists anywhere and the page never holds one. The model is fixed here whatever the page asks for, the reply length
// and the conversation size are capped, and each address gets CHATS_PER_HOUR answers an hour. The answer goes back in
// the shape the page already reads: { content: [{ type: 'text', text }] }.
//
// This Worker takes no notes and no reviews. Whistleblower reviews go to the report API (server/).
//
// Bindings (see worker/wrangler.toml and docs/GUIDE.md):
//   AI               Workers AI binding
//   SUBMISSIONS      KV namespace (holds only the hourly rate counters)
//   ALLOWED_ORIGINS  comma-separated origins allowed to call the API
//   RATE_SALT        optional secret mixed into the hashed address of the rate counters
//
// KV layout:
//   chat:<hash>    answers sent to one address in the current hour (expires on its own)

// IBM Granite 4.0 H Micro: 3B parameters, a 131,000-token context (the page's grounding runs to about 40,000 tokens),
// open to every account, $0.017 per million input tokens. Chosen 18 Nov 2026 over Llama 3.1 8B and Llama 3.2 3B,
// which Workers AI retires on 20 Nov 2026. It does not think before answering, so the cap is all answer.
const CHAT_MODEL = '@cf/ibm-granite/granite-4.0-h-micro';
const CHAT_TEMPERATURE = 0.3;
const CHAT_MAX_TOKENS = 2000;
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

// A reader asks a question. The conversation is checked, trimmed to what the page may send, and passed to the model.
async function chat(request, env) {
  if (!env.AI || typeof env.AI.run !== 'function') return json({ error: 'The chat is not switched on.' }, 503);
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

  const maxTokens = Math.min(Math.max(parseInt(body.max_tokens, 10) || CHAT_MAX_TOKENS, 256), CHAT_MAX_TOKENS);
  const input = { messages: system ? [{ role: 'system', content: system }, ...messages] : messages, max_tokens: maxTokens, temperature: CHAT_TEMPERATURE };
  let data;
  try {
    data = await withTimeout(env.AI.run(CHAT_MODEL, input), 60000);
  } catch (e) {
    // The reason goes to the Worker's own log (Cloudflare dashboard), never to the visitor.
    console.error('workers-ai', CHAT_MODEL, String(e && e.message || e).slice(0, 300));
    if (e && e.name === 'TimeoutError') return json({ error: 'The model did not answer in time.' }, 504);
    return json({ error: 'The model could not answer.' }, /capacity|rate|429|neuron/i.test(String(e && e.message)) ? 429 : 502);
  }
  const text = replyText(data);
  if (!text) {
    console.error('workers-ai', CHAT_MODEL, 'empty reply', JSON.stringify(data || null).slice(0, 300));
    return json({ error: 'The model could not answer.' }, 502);
  }
  return json({ content: [{ type: 'text', text }] }, 200, { 'Cache-Control': 'no-store' });
}

// Workers AI text models answer as { response }; the newer ones as an OpenAI-style { choices }. Either becomes plain text.
function replyText(data) {
  if (!data) return '';
  if (typeof data === 'string') return data.trim();
  if (typeof data.response === 'string') return data.response.trim();
  const msg = data.choices && data.choices[0] && data.choices[0].message;
  return msg && typeof msg.content === 'string' ? msg.content.trim() : '';
}

function withTimeout(promise, ms) {
  let timer;
  const late = new Promise((_, reject) => {
    timer = setTimeout(() => { const e = new Error('timed out'); e.name = 'TimeoutError'; reject(e); }, ms);
  });
  return Promise.race([promise, late]).finally(() => clearTimeout(timer));
}

// A fixed number of sends an hour from one address. Only a salted hash of the address is kept, for an hour.
async function overLimit(request, env, prefix, limit) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const hour = Math.floor(Date.now() / 3600000);
  const key = prefix + (await sha256(ip + hour + (env.RATE_SALT || 'culture-atlas-chat'))).slice(0, 32);
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
