# worker/

The chat proxy: a Cloudflare Worker that forwards a conversation to Claude so the page can answer
like a model. It serves only `POST /chat`; it takes no notes or reviews (those go to `server/`).

- The Anthropic key is a Worker secret (`npx wrangler secret put ANTHROPIC_API_KEY`) and never reaches
  the browser. It is not in this folder.
- Only a short allowlist of models is accepted; reply length and conversation size are capped, and each
  address is limited to a number of answers an hour.
- `wrangler.toml` holds the allowed origin and the KV binding used for the limit.
- Point the page at it with `window.ATLAS_AI_PROXY_URL` in `assets/config.js`.
- Tests: `node --test worker/test/*.test.mjs`.

Setup steps are in [docs/api.md](../docs/api.md) under "Live Claude answers".
