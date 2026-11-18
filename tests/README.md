# tests/

Node's built-in test runner, no extra dependencies. From the repository root: `npm test` (this folder plus
`server/test/`), or `node --test tests/*.test.mjs`. The page scripts in `assets/` are plain browser
scripts, so most tests load them into a `vm` context and call what they set on the global.

| Test | Checks |
|---|---|
| `analytics.test.mjs` | `assets/analytics.js` is off without an address or when the browser says not to track. |
| `data-noise.test.mjs` | The records carry no broken links or empty points. |
| `editor.test.mjs`, `editor-structure.test.mjs` | The data editor (`tools/editor.py`, `editor/`): a save writes only the edited record. |
| `gossip-kind.test.mjs` | A question about a kind of story is answered from the gossip data. |
| `grounding.test.mjs` | The chat's grounding in the records. |
| `influence.test.mjs` | Influence mode shows only what `data/influence_review.json` keeps. |
| `live-feed.test.mjs` | `assets/live.json`: dated, sourced items only. |
| `name-request.test.mjs`, `names.test.mjs` | Matching a typed space or city name to a record. |
| `release.test.mjs` | The page reloads itself when its release differs from the live one. |
| `repeats.test.mjs` | A sentence is never shown twice. Also run by the deploy workflow. |
| `subtopic.test.mjs`, `tab-suggest.test.mjs` | Question topics and the Tab suggestion in the chat box. |
