# worker/

The chat proxy: a Cloudflare Worker that answers a conversation with a small open model on Workers AI
(IBM Granite 4.0 H Micro, set as `CHAT_MODEL` in `index.js`). It serves only `POST /chat`; it takes no
notes or reviews (those go to `server/`).

- There is no API key anywhere: the Worker reaches the model through its `AI` binding, and Workers AI
  bills the Cloudflare account.
- The model is fixed in the Worker whatever the page asks for. Reply length, conversation size and the
  answers per address per hour are capped by the constants at the top of `index.js`; other origins than
  `ALLOWED_ORIGINS` are refused.
- `wrangler.toml` holds the allowed origin and the bindings (`AI`, and the KV namespace `SUBMISSIONS`
  used only for the hourly rate counters).
- Point the page at it with `window.ATLAS_AI_PROXY_URL` in `assets/config.js`.
- Tests: `node --test worker/test/*.test.mjs`.

Setup and limits are in [docs/api.md](../docs/api.md) under "Live model answers".
